from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from tinkle.api.main import app
from tinkle.engineering_decision import (
    DecisionCriterion,
    DecisionEvidence,
    DecisionRequest,
    DecisionState,
    EngineeringDecisionEngine,
)
from tinkle.invention_design import (
    ConstraintStatus,
    DesignCandidate,
    EngineeringRequirement,
    EvaluationRequest,
    ProvenanceBundle,
)
from tinkle.reality_engine import ClaimStatus
from tinkle.simulation_engine import MechanicsSimulationRequest, PhysicsQuantity


def build_engine():
    engine = EngineeringDecisionEngine()
    evidence = engine.create_evidence(DecisionEvidence(description="source evidence", source="test"))
    engine.invention.create_requirement(EngineeringRequirement(id=f"r-{uuid4()}", description="force", minimum=1, hard_constraint=True, epistemic_state=ClaimStatus.SOURCE_BACKED))
    requirement = next(iter(engine.invention.state.requirements))
    first = engine.invention.create_candidate(DesignCandidate(name="A", description="first", requirement_ids=[requirement], provenance=ProvenanceBundle(originating_artifact="hypothesis-1")))
    second = engine.invention.create_candidate(DesignCandidate(name="B", description="second", requirement_ids=[requirement]))
    first_eval = engine.invention.evaluate(first.id, EvaluationRequest(actual_values={requirement: 2}, objective_score=0.8))
    second_eval = engine.invention.evaluate(second.id, EvaluationRequest(actual_values={requirement: 2}, objective_score=0.6))
    criterion = DecisionCriterion(name="performance", weight=2, values={str(first.id): 10, str(second.id): 8}, epistemic_state=ClaimStatus.SOURCE_BACKED, evidence_refs=[str(evidence.id)])
    request = DecisionRequest(title="choose design", objective="maximize performance", requirement_refs=[requirement], candidate_refs=[first.id, second.id], evaluation_refs=[first_eval.id, second_eval.id], criteria=[criterion], evidence_refs=[str(evidence.id)], provenance=ProvenanceBundle(originating_artifact="research-question-1"))
    return engine, request, first, second


def test_request_validates_candidate_references():
    engine = EngineeringDecisionEngine()
    with pytest.raises(ValueError, match="Unknown candidate"):
        engine.create_request(DecisionRequest(title="x", objective="y", candidate_refs=[uuid4(), uuid4()], criteria=[DecisionCriterion(name="x", weight=1, epistemic_state=ClaimStatus.SOURCE_BACKED)]))


def test_missing_evaluation_and_unknown_criterion_prevent_recommendation():
    engine, request, first, second = build_engine()
    request.criteria[0].values.pop(str(second.id))
    request.evaluation_refs = [engine.invention.state.evaluations[first.id][0].id]
    stored = engine.create_request(request)
    result = engine.evaluate(stored.id)
    assert result.state == DecisionState.DATA_INSUFFICIENT
    assert result.recommendation is None
    assert result.missing_evidence


def test_hard_constraint_failure_excludes_option_and_recommends_valid_option():
    engine, request, first, second = build_engine()
    engine.invention.state.evaluations[first.id][0].failed_constraints = [next(iter(engine.invention.state.requirements))]
    engine.invention.state.evaluations[first.id][0].constraints[0].status = ConstraintStatus.FAIL
    stored = engine.create_request(request)
    result = engine.evaluate(stored.id)
    assert result.recommendation == second.id
    assert str(first.id) in result.hard_constraint_failures


def test_tradeoffs_hash_and_history_are_deterministic_and_explainable():
    engine, request, _, _ = build_engine()
    stored = engine.create_request(request)
    result = engine.evaluate(stored.id)
    repeat = engine.evaluate(stored.id)
    assert result.input_hash == repeat.input_hash
    assert result.tradeoffs[0].magnitude == 2
    assert result.explanation and result.provenance.method == "explicit_weighted_sum_v1"
    assert [event.event_type for event in engine.history(stored.id)] == ["REQUEST_CREATED", "DECISION_EVALUATED", "DECISION_EVALUATED"]


def test_simulated_evidence_remains_simulated():
    engine, request, first, _ = build_engine()
    stored = engine.create_request(request)
    result = engine.evaluate(stored.id)
    assert result.epistemic_state == ClaimStatus.ESTIMATED
    engine.invention.state.evaluations[first.id][0].epistemic_state = ClaimStatus.SIMULATED
    engine.decisions.pop(stored.id)
    result = engine.evaluate(stored.id)
    assert result.epistemic_state == ClaimStatus.SIMULATED


def test_simulation_is_reused_without_becoming_measurement():
    engine = EngineeringDecisionEngine()
    engine.invention.create_requirement(EngineeringRequirement(id="velocity", description="velocity", minimum=0, epistemic_state=ClaimStatus.SOURCE_BACKED))
    first = engine.invention.create_candidate(DesignCandidate(name="A", description="first", requirement_ids=["velocity"]))
    second = engine.invention.create_candidate(DesignCandidate(name="B", description="second", requirement_ids=["velocity"]))
    simulation = MechanicsSimulationRequest(mass=PhysicsQuantity(value=1, unit="kg", epistemic_state=ClaimStatus.ASSUMED), force=PhysicsQuantity(value=2, unit="N", epistemic_state=ClaimStatus.ASSUMED), gravity=PhysicsQuantity(value=0, unit="m/s^2", epistemic_state=ClaimStatus.SOURCE_BACKED), steps=1)
    first_eval = engine.invention.evaluate(first.id, EvaluationRequest(simulation=simulation, objective_score=1))
    second_eval = engine.invention.evaluate(second.id, EvaluationRequest(simulation=simulation, objective_score=.5))
    request = engine.create_request(DecisionRequest(title="simulated choice", objective="compare", candidate_refs=[first.id, second.id], evaluation_refs=[first_eval.id, second_eval.id], criteria=[DecisionCriterion(name="performance", weight=1, values={str(first.id): 2, str(second.id): 1}, epistemic_state=ClaimStatus.SIMULATED)]))
    result = engine.evaluate(request.id)
    assert result.epistemic_state == ClaimStatus.SIMULATED
    assert result.options[0].simulation_refs
    assert "measurement" in " ".join(result.limitations)


def test_measured_evidence_remains_measured():
    engine, request, _, _ = build_engine()
    evidence = engine.create_evidence(DecisionEvidence(description="measured result", epistemic_state=ClaimStatus.MEASURED))
    request.evidence_refs = [str(evidence.id)]
    stored = engine.create_request(request)
    assert engine.evaluate(stored.id).epistemic_state == ClaimStatus.MEASURED


def test_api_authentication_and_happy_path():
    client = TestClient(app)
    assert client.post("/api/v1/engineering/decisions/requests", json={"title": "x", "objective": "y", "candidate_refs": [str(uuid4()), str(uuid4())], "criteria": [{"name": "x", "weight": 1}]}).status_code == 401
    assert client.post("/api/v1/engineering/decisions/evidence", headers={"X-API-Key": "dev-key"}, json={"description": "evidence"}).status_code == 200


def test_api_rejects_malformed_candidate_reference():
    client = TestClient(app)
    response = client.post("/api/v1/engineering/decisions/requests", headers={"X-API-Key": "dev-key"}, json={"title": "x", "objective": "y", "candidate_refs": [str(uuid4()), str(uuid4())], "criteria": [{"name": "x", "weight": 1}]})
    assert response.status_code == 422
