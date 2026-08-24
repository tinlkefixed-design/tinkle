import pytest
from fastapi.testclient import TestClient

from tinkle.api.main import app
from tinkle.engineering_decision import (
    DecisionCriterion,
    DecisionEvidence,
    DecisionRequest,
    EngineeringDecisionEngine,
)
from tinkle.experiment_planning import (
    ExperimentalCondition,
    ExperimentalVariable,
    ExperimentObjective,
    ExperimentPlanningEngine,
    ExperimentPlanRequest,
    ExperimentResultReference,
    MeasurementSpecification,
    PlanInvalidation,
    PlanStatus,
    Prediction,
    ResearchObjective,
    VariableRole,
)
from tinkle.invention_design import (
    DesignCandidate,
    EngineeringRequirement,
    EvaluationRequest,
)
from tinkle.reality_engine import ClaimStatus
from tinkle.validation import ValidationEngine, ValidationRequirement


def setup_engine():
    decisions = EngineeringDecisionEngine()
    decisions.invention.create_requirement(EngineeringRequirement(id="efficiency", description="efficiency", minimum=1, epistemic_state=ClaimStatus.SOURCE_BACKED))
    first = decisions.invention.create_candidate(DesignCandidate(name="A", description="A", requirement_ids=["efficiency"]))
    second = decisions.invention.create_candidate(DesignCandidate(name="B", description="B", requirement_ids=["efficiency"]))
    first_eval = decisions.invention.evaluate(first.id, EvaluationRequest(actual_values={"efficiency": 2}, objective_score=.8))
    second_eval = decisions.invention.evaluate(second.id, EvaluationRequest(actual_values={"efficiency": 2}, objective_score=.6))
    evidence = decisions.create_evidence(DecisionEvidence(description="criterion source", epistemic_state=ClaimStatus.SOURCE_BACKED))
    decision_request = decisions.create_request(DecisionRequest(title="select", objective="choose", requirement_refs=["efficiency"], candidate_refs=[first.id, second.id], evaluation_refs=[first_eval.id, second_eval.id], evidence_refs=[str(evidence.id)], criteria=[DecisionCriterion(name="efficiency", weight=1, values={str(first.id): 2, str(second.id): 1}, evidence_refs=[str(evidence.id)], epistemic_state=ClaimStatus.SOURCE_BACKED)]))
    decisions.evaluate(decision_request.id)
    validation = ValidationEngine(decisions=decisions)
    validation_requirement = validation.create_requirement(ValidationRequirement(id="measure-efficiency", description="Measure efficiency", target_decision_id=decision_request.id, acceptance_condition="efficiency >= 1"))
    planner = ExperimentPlanningEngine(decisions=decisions, validation=validation)
    research = planner.create_research_objective(ResearchObjective(title="resolve efficiency", description="Measure uncertain efficiency", hypothesis_ids=["H-A", "H-B"], requirement_ids=["efficiency"], source_refs=[str(decision_request.id)]))
    objective = planner.create_experiment_objective(ExperimentObjective(objective_type="discriminate", description="Distinguish candidates", research_objective_id=research.id, hypothesis_ids=["H-A", "H-B"], candidate_ids=[first.id, second.id], decision_id=decision_request.id, validation_requirement_ids=[validation_requirement.id]))
    planner.register_variable(ExperimentalVariable(id="input", name="input power", units="W", role=VariableRole.INDEPENDENT, allowed_minimum=1, allowed_maximum=10, nominal_value=5, epistemic_state=ClaimStatus.ASSUMED, uncertainty={"range": "1..10"}))
    planner.register_variable(ExperimentalVariable(id="output", name="output power", units="W", role=VariableRole.DEPENDENT, epistemic_state=ClaimStatus.UNKNOWN))
    planner.register_measurement(MeasurementSpecification(id="m-output", variable_id="output", measurement_method="power meter", units="W", expected_minimum=0, expected_maximum=10, required_evidence_state=ClaimStatus.MEASURED))
    planner.register_condition(ExperimentalCondition(id="room", parameter_values={"temperature": 20}, environment={"location": "lab"}, epistemic_state=ClaimStatus.ASSUMED))
    planner.register_prediction(Prediction(source_refs=["H-A"], expected_minimum=3, expected_maximum=5, units="W", simulation_ref="sim-1", epistemic_state=ClaimStatus.SIMULATED))
    return planner, research, objective, first, second, decision_request


def plan_request(planner, research, objective, first, second, **updates):
    data = {
        "research_objective_id": research.id,
        "experiment_objective_id": objective.id,
        "variable_ids": ["input", "output"],
        "measurement_ids": ["m-output"],
        "condition_ids": ["room"],
        "prediction_ids": list(planner.state.predictions),
        "candidate_ids": [first.id, second.id],
        "decision_id": objective.decision_id,
        "validation_requirement_ids": objective.validation_requirement_ids,
    }
    data.update(updates)
    return planner.create_plan(ExperimentPlanRequest(**data))


def test_objectives_plan_and_missing_data():
    planner, research, objective, first, second, _ = setup_engine()
    plan = plan_request(planner, research, objective, first, second)
    assert plan.status == PlanStatus.READY
    assert plan.estimated_information_value > 0
    assert plan.predictions[0].epistemic_state == ClaimStatus.SIMULATED
    blocked = planner.create_plan(ExperimentPlanRequest(research_objective_id=research.id, experiment_objective_id=objective.id, candidate_ids=[first.id, second.id], decision_id=objective.decision_id, validation_requirement_ids=objective.validation_requirement_ids))
    assert blocked.status == PlanStatus.BLOCKED
    assert "measurements" in planner.missing_data(blocked.id)


def test_plan_safety_review_blocks_without_authorization():
    planner, research, objective, first, second, _ = setup_engine()
    plan = plan_request(planner, research, objective, first, second, risks=["human hazard review required"])
    assert plan.status == PlanStatus.BLOCKED
    assert "REQUIRES_HUMAN_REVIEW" in plan.prerequisites
    assert plan.human_review_required


def test_deterministic_manifest_hash_and_comparison():
    planner, research, objective, first, second, _ = setup_engine()
    first_plan = plan_request(planner, research, objective, first, second)
    second_plan = plan_request(planner, research, objective, first, second, limitations=["repeat"])
    assert first_plan.deterministic_hash != second_plan.deterministic_hash
    comparison = planner.compare([first_plan.id, second_plan.id])
    assert comparison.status == "RANKED"
    assert comparison.ranked_plan_ids[0] in [first_plan.id, second_plan.id]


def test_external_results_and_invalidation_preserve_boundaries():
    planner, research, objective, first, second, _ = setup_engine()
    plan = plan_request(planner, research, objective, first, second)
    with pytest.raises(ValueError, match="measured or source"):
        planner.register_result(ExperimentResultReference(experiment_plan_id=plan.id, source="external", epistemic_state=ClaimStatus.SIMULATED))
    result = planner.register_result(ExperimentResultReference(experiment_plan_id=plan.id, source="external lab", epistemic_state=ClaimStatus.MEASURED))
    assert result.id in planner.state.results and plan.status == PlanStatus.EXECUTED_EXTERNALLY
    invalidated = planner.invalidate(PlanInvalidation(plan_id=plan.id, reason="assumption contradicted", evidence_refs=["external-measurement"]))
    assert invalidated.status == PlanStatus.INVALIDATED
    assert len(planner.history(plan.id)) == 3


def test_graph_idempotency_and_provenance():
    planner, research, objective, first, second, _ = setup_engine()
    plan = plan_request(planner, research, objective, first, second)
    before = len(planner.graph.get_edges())
    planner._graph_plan(plan)
    assert len(planner.graph.get_edges()) == before
    assert plan.provenance.input_hash == plan.deterministic_hash
    assert plan.reproducibility_manifest and plan.reproducibility_manifest.canonical_hash == plan.deterministic_hash


def test_invalid_references_and_authentication():
    planner, research, objective, first, second, _ = setup_engine()
    with pytest.raises(ValueError, match="Unknown variable"):
        planner.create_plan(ExperimentPlanRequest(research_objective_id=research.id, experiment_objective_id=objective.id, variable_ids=["missing"], candidate_ids=[first.id, second.id]))
    client = TestClient(app)
    assert client.post("/api/v1/experiments/objectives", json={"title": "x", "description": "y"}).status_code == 401
    response = client.post("/api/v1/experiments/objectives", headers={"X-API-Key": "dev-key"}, json={"title": "x", "description": "y"})
    assert response.status_code == 200
