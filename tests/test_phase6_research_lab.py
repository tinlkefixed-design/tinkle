from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from tinkle.api.main import app
from tinkle.reality_engine import ClaimStatus
from tinkle.research_graph import NodeType, ResearchGraph, SQLiteResearchGraphStore
from tinkle.research_lab import (
    ExecutionType,
    HumanMeasurement,
    Prediction,
    ResearchExperiment,
    ResearchHypothesis,
    ResearchLab,
    ResearchQuestion,
)
from tinkle.simulation_engine import MechanicsSimulationRequest, PhysicsLabEngine, PhysicsQuantity


def q(value, unit, state=ClaimStatus.ASSUMED):
    return PhysicsQuantity(value=value, unit=unit, epistemic_state=state)


def workflow(tmp_path: Path):
    graph = ResearchGraph(SQLiteResearchGraphStore(str(tmp_path / "lab.db")))
    lab = ResearchLab(PhysicsLabEngine(graph), graph)
    question = ResearchQuestion(question="Does force increase velocity?", objective="Test motion", domain="mechanics")
    hypothesis = ResearchHypothesis(question_id=question.id, statement="A constant force increases final velocity.", falsification_criterion="Final velocity is outside the predicted range.", variables=["force", "velocity"])
    prediction = Prediction(hypothesis_id=hypothesis.id, expected_output={"velocity": 2.5}, expected_range={"velocity": (2.0, 3.0)}, assumptions=["Constant force"])
    experiment = ResearchExperiment(question_id=question.id, hypothesis_id=hypothesis.id, prediction_id=prediction.id, execution_type=ExecutionType.PLANNED, simulation_request=MechanicsSimulationRequest(mass=q(2, "kg"), force=q(10, "N"), gravity=q(0, "m/s^2"), steps=1, timestep=.5))
    state = lab.create_workflow(question, hypothesis, experiment)
    lab.create_prediction(question.id, prediction)
    return lab, state


def test_question_hypothesis_prediction_history(tmp_path: Path):
    lab, state = workflow(tmp_path)
    assert state.question.question.startswith("Does force")
    assert state.hypothesis.lifecycle_state == "NEW"
    assert state.prediction is not None
    assert [event.event for event in lab.history(state.question.id)] == ["QUESTION_CREATED", "HYPOTHESIS_CREATED", "PREDICTION_CREATED"]


def test_simulation_experiment_comparison_and_supported_update(tmp_path: Path):
    lab, state = workflow(tmp_path)
    result = lab.run_simulation(state.question.id)
    assert result.execution_type == ExecutionType.SIMULATION
    assert result.epistemic_state == ClaimStatus.SIMULATED
    comparison = lab.compare(state.question.id)
    assert comparison.state == "COMPATIBLE"
    assert lab.update_hypothesis(state.question.id).lifecycle_state == "SUPPORTED"
    assert len(lab.history(state.question.id)) == 6


def test_contradiction_and_falsification(tmp_path: Path):
    lab, state = workflow(tmp_path)
    lab.run_simulation(state.question.id)
    comparison = lab.compare(state.question.id, {"velocity": (20.0, 30.0)})
    assert comparison.state == "INCOMPATIBLE"
    assert lab.update_hypothesis(state.question.id).lifecycle_state == "FALSIFIED"


def test_missing_result_requires_data(tmp_path: Path):
    lab, state = workflow(tmp_path)
    assert lab.update_hypothesis(state.question.id).lifecycle_state == "REQUIRES_DATA"


def test_human_measurement_requires_explicit_provenance(tmp_path: Path):
    lab, state = workflow(tmp_path)
    with pytest.raises(ValueError, match="source and method"):
        lab.record_measurement(state.question.id, HumanMeasurement(experiment_id=state.experiment.id, variable="velocity", value=2.5, unit="m/s", source="", method="", epistemic_state=ClaimStatus.MEASURED))
    measurement = HumanMeasurement(experiment_id=state.experiment.id, variable="velocity", value=2.5, unit="m/s", source="operator observation", method="tachometer", epistemic_state=ClaimStatus.MEASURED, provenance={"observed_externally": True})
    assert lab.record_measurement(state.question.id, measurement).epistemic_state == ClaimStatus.MEASURED
    lab.compare(state.question.id, {"velocity": (2.0, 3.0)}) if False else None


def test_graph_contains_workflow_artifacts(tmp_path: Path):
    lab, state = workflow(tmp_path)
    lab.run_simulation(state.question.id)
    nodes = [lab.graph.get_node(__import__('uuid').UUID(node_id)) for node_id in state.graph_node_ids]
    assert {node.type for node in nodes} >= {NodeType.RESEARCH_QUESTION, NodeType.HYPOTHESIS}
    descendants = lab.graph.descendants(nodes[0].id)
    assert any(node.type == NodeType.RESULT for node in descendants)


def test_phase6_api_auth_and_workflow_creation():
    client = TestClient(app)
    response = client.post("/api/v1/research/questions", headers={"X-API-Key": "dev-key"}, json={"question": "Does force increase velocity?"})
    assert response.status_code == 200
    assert client.post("/api/v1/research/questions", json={"question": "x"}).status_code == 401
