from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from tinkle.api.main import app
from tinkle.reality_engine import ClaimStatus
from tinkle.research_graph import (
    GraphSearchRequest,
    NodeType,
    ResearchGraph,
    SQLiteResearchGraphStore,
)
from tinkle.simulation_engine import (
    AnalysisRequest,
    MechanicsSimulationRequest,
    OptimizationRequest,
    ParameterRange,
    PhysicsQuantity,
    UncertaintyEngine,
)


def q(value, unit, state=ClaimStatus.ASSUMED):
    return PhysicsQuantity(value=value, unit=unit, epistemic_state=state)


def request():
    return MechanicsSimulationRequest(mass=q(2, "kg"), force=q(10, "N"), gravity=q(0, "m/s^2"), steps=2, timestep=0.5)


def ranges():
    return [ParameterRange(name="mass", nominal=2, lower=1, upper=3, unit="kg", epistemic_state=ClaimStatus.ASSUMED), ParameterRange(name="force", nominal=10, lower=5, upper=15, unit="N", epistemic_state=ClaimStatus.ASSUMED)]


def test_sweep_is_explicit_deterministic_and_reuses_simulator(tmp_path: Path):
    engine = UncertaintyEngine(graph=ResearchGraph(SQLiteResearchGraphStore(str(tmp_path / "a.db"))))
    result = engine.sweep(AnalysisRequest(simulation=request(), ranges=ranges()))
    again = engine.sweep(AnalysisRequest(simulation=request(), ranges=ranges()))
    assert result.evaluations == 9
    assert [item.outputs for item in result.simulations] == [item.outputs for item in again.simulations]
    assert all(item.epistemic_state == ClaimStatus.SIMULATED for item in result.simulations)


def test_sensitivity_uses_normalized_local_finite_difference(tmp_path: Path):
    engine = UncertaintyEngine(graph=ResearchGraph(SQLiteResearchGraphStore(str(tmp_path / "b.db"))))
    result = engine.sensitivity(AnalysisRequest(simulation=request(), ranges=ranges(), output="velocity"))
    assert [item.rank for item in result] == [1, 2]
    assert result[0].provenance["formula"] == "(delta Y / Y) / (delta X / X)"
    assert result[0].epistemic_state == ClaimStatus.SIMULATED


def test_uncertainty_and_robustness_preserve_input_states(tmp_path: Path):
    engine = UncertaintyEngine(graph=ResearchGraph(SQLiteResearchGraphStore(str(tmp_path / "c.db"))))
    analysis = AnalysisRequest(simulation=request(), ranges=ranges(), output="velocity")
    uncertainty = engine.uncertainty(analysis)
    robust = engine.robustness(analysis)
    assert uncertainty.output_range["minimum"] <= uncertainty.output_range["maximum"]
    assert robust.variation >= 0
    assert uncertainty.input_parameters[0].epistemic_state == ClaimStatus.ASSUMED
    assert uncertainty.epistemic_state == ClaimStatus.SIMULATED
    assert "not measured" in uncertainty.limitations[0]


def test_unknown_range_is_rejected_and_no_range_is_invented(tmp_path: Path):
    engine = UncertaintyEngine(graph=ResearchGraph(SQLiteResearchGraphStore(str(tmp_path / "d.db"))))
    unknown = ParameterRange(name="mass", nominal=2, lower=1, upper=3, epistemic_state=ClaimStatus.UNKNOWN)
    with pytest.raises(ValueError, match="unknown"):
        engine.sweep(AnalysisRequest(simulation=request(), ranges=[unknown]))
    with pytest.raises(ValueError, match="explicit"):
        engine.sweep(AnalysisRequest(simulation=request()))


def test_grid_optimization_is_bounded_and_not_global_claim(tmp_path: Path):
    engine = UncertaintyEngine(graph=ResearchGraph(SQLiteResearchGraphStore(str(tmp_path / "e.db"))))
    result = engine.optimize(OptimizationRequest(simulation=request(), ranges=ranges()))
    assert result.evaluations == 9
    assert result.selected_configuration == {"mass": 1.0, "force": 15.0}
    assert "within the evaluated grid" in result.limitations[0]
    assert result.epistemic_state == ClaimStatus.SIMULATED
    assert result.provenance["method"] == "deterministic_grid_search"


def test_phase5_artifacts_are_recorded_in_research_graph(tmp_path: Path):
    graph = ResearchGraph(SQLiteResearchGraphStore(str(tmp_path / "f.db")))
    engine = UncertaintyEngine(graph=graph)
    result = engine.uncertainty(AnalysisRequest(simulation=request(), ranges=ranges()))
    nodes = graph.search_graph(GraphSearchRequest(query=str(result.analysis_id), node_type=NodeType.RESULT))
    assert nodes and nodes[0].epistemic_state == ClaimStatus.SIMULATED


def test_phase5_api_is_authenticated_and_runs():
    client = TestClient(app)
    headers = {"X-API-Key": "dev-key"}
    payload = {"simulation": request().model_dump(mode="json"), "ranges": [item.model_dump(mode="json") for item in ranges()]}
    response = client.post("/api/v1/simulation/analysis/uncertainty", headers=headers, json=payload)
    assert response.status_code == 200
    assert response.json()["epistemic_state"] == "SIMULATED"
    assert client.post("/api/v1/simulation/analysis/sweep", json=payload).status_code == 401
