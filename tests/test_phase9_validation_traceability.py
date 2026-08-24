import pytest
from fastapi.testclient import TestClient

from tinkle.api.main import app
from tinkle.engineering_decision import (
    DecisionCriterion,
    DecisionEvidence,
    DecisionRequest,
    EngineeringDecisionEngine,
)
from tinkle.invention_design import (
    DesignCandidate,
    EngineeringRequirement,
    EvaluationRequest,
    ProvenanceBundle,
)
from tinkle.reality_engine import ClaimStatus
from tinkle.validation import (
    EvidenceKind,
    InvalidationCondition,
    ReproducibilityStatus,
    ValidationEngine,
    ValidationGateState,
    ValidationRecord,
    ValidationRequirement,
    ValidationStatus,
)


def build_decision(simulated=False):
    engine = EngineeringDecisionEngine()
    engine.invention.create_requirement(EngineeringRequirement(id="force", description="force", minimum=1, epistemic_state=ClaimStatus.SOURCE_BACKED))
    first = engine.invention.create_candidate(DesignCandidate(name="candidate-a", description="A", requirement_ids=["force"], provenance=ProvenanceBundle(hypothesis_refs=["hypothesis-1"])))
    second = engine.invention.create_candidate(DesignCandidate(name="candidate-b", description="B", requirement_ids=["force"]))
    kwargs = {"actual_values": {"force": 2}, "objective_score": 1}
    if simulated:
        from tinkle.simulation_engine import MechanicsSimulationRequest, PhysicsQuantity
        simulation = MechanicsSimulationRequest(mass=PhysicsQuantity(value=1, unit="kg", epistemic_state=ClaimStatus.ASSUMED), force=PhysicsQuantity(value=2, unit="N", epistemic_state=ClaimStatus.ASSUMED), gravity=PhysicsQuantity(value=0, unit="m/s^2", epistemic_state=ClaimStatus.SOURCE_BACKED), steps=1)
        kwargs = {"simulation": simulation, "actual_values": {"force": 2}, "objective_score": 1}
    first_eval = engine.invention.evaluate(first.id, EvaluationRequest(**kwargs))
    second_eval = engine.invention.evaluate(second.id, EvaluationRequest(**kwargs))
    evidence = engine.create_evidence(DecisionEvidence(description="source-backed criterion", epistemic_state=ClaimStatus.SOURCE_BACKED))
    request = engine.create_request(DecisionRequest(title="select design", objective="choose the strongest option", requirement_refs=["force"], candidate_refs=[first.id, second.id], evaluation_refs=[first_eval.id, second_eval.id], evidence_refs=[str(evidence.id)], criteria=[DecisionCriterion(name="performance", weight=1, values={str(first.id): 10, str(second.id): 8}, evidence_refs=[str(evidence.id)], epistemic_state=ClaimStatus.SOURCE_BACKED)]))
    decision = engine.evaluate(request.id)
    return engine, request, decision, evidence


def test_validation_requirement_creation_and_unknown_state():
    decisions, request, _, _ = build_decision()
    validation = ValidationEngine(decisions=decisions)
    requirement = validation.create_requirement(ValidationRequirement(id="measure-force", description="Measure force", target_decision_id=request.id, criterion="performance", expected_evidence_type=EvidenceKind.MEASURED, acceptance_condition="force >= 1 N"))
    assert requirement.epistemic_state == ClaimStatus.UNKNOWN
    assert validation.gate(request.id).state == ValidationGateState.VALIDATION_REQUIRED


def test_simulation_is_not_measurement_and_recommendation_needs_validation():
    decisions, request, decision, _ = build_decision(simulated=True)
    validation = ValidationEngine(decisions=decisions)
    validation.create_requirement(ValidationRequirement(id="physical-check", description="Check motion", target_decision_id=request.id, acceptance_condition="measured velocity is in range"))
    gate = validation.gate(request.id)
    assert decision.recommendation is not None
    assert gate.state == ValidationGateState.VALIDATION_REQUIRED
    assert decision.options[0].evaluation.epistemic_state == ClaimStatus.SIMULATED


def test_passed_validation_requires_explicit_measured_evidence():
    decisions, request, _, _ = build_decision()
    validation = ValidationEngine(decisions=decisions)
    validation.create_requirement(ValidationRequirement(id="m", description="measurement", target_decision_id=request.id, acceptance_condition="value is acceptable"))
    record = ValidationRecord(target_type="decision", target_id=request.id, validation_requirement_id="m", method="instrument", expected_result=2, observed_result=2, status=ValidationStatus.PASSED, epistemic_state=ClaimStatus.MEASURED)
    with pytest.raises(ValueError, match="measured evidence"):
        validation.create_record(record)
    evidence = decisions.create_evidence(DecisionEvidence(description="instrument reading", epistemic_state=ClaimStatus.MEASURED))
    record.evidence_refs = [str(evidence.id)]
    created = validation.create_record(record)
    assert created.result_hash and validation.gate(request.id).state == ValidationGateState.VALIDATED


def test_conflicting_evidence_is_explicit_and_history_preserved():
    decisions, request, _, _ = build_decision()
    validation = ValidationEngine(decisions=decisions)
    validation.create_requirement(ValidationRequirement(id="m", description="measurement", target_decision_id=request.id, acceptance_condition="value"))
    first = decisions.create_evidence(DecisionEvidence(description="reading one", epistemic_state=ClaimStatus.MEASURED))
    second = decisions.create_evidence(DecisionEvidence(description="reading two", epistemic_state=ClaimStatus.MEASURED))
    for value, evidence in [(10, first), (14, second)]:
        validation.create_record(ValidationRecord(target_type="decision", target_id=request.id, validation_requirement_id="m", method="same instrument", observed_result=value, status=ValidationStatus.INCONCLUSIVE, epistemic_state=ClaimStatus.MEASURED, evidence_refs=[str(evidence.id)]))
    gate = validation.gate(request.id)
    assert gate.state == ValidationGateState.DATA_INSUFFICIENT
    assert set(gate.conflicting_evidence_ids) == {str(first.id), str(second.id)}
    assert len(validation.history(request.id)) >= 3


def test_trace_chain_reproducibility_and_invalidation():
    decisions, request, _, evidence = build_decision()
    validation = ValidationEngine(decisions=decisions)
    validation.create_requirement(ValidationRequirement(id="m", description="measurement", target_decision_id=request.id, acceptance_condition="value"))
    trace = validation.trace(request.id)
    repeat = validation.trace(request.id)
    chain = validation.evidence_chain(request.id)
    manifest = validation.reproducibility(request.id)
    assert trace.canonical_input_hash == repeat.canonical_input_hash
    assert chain.links and chain.input_hash
    assert manifest.status == ReproducibilityStatus.REPRODUCIBLE
    condition = validation.add_invalidation_condition(InvalidationCondition(decision_id=request.id, description="model changes", trigger="model version changes"))
    validation.trigger_invalidation(condition.id, [str(evidence.id)])
    assert validation.gate(request.id).state == ValidationGateState.INVALIDATED
    assert len(validation.history(request.id)) >= 3


def test_missing_evidence_and_references_are_rejected():
    decisions, request, _, _ = build_decision()
    validation = ValidationEngine(decisions=decisions)
    with pytest.raises(KeyError, match="Validation requirement"):
        validation.create_record(ValidationRecord(target_type="decision", target_id=request.id, validation_requirement_id="missing", method="test"))
    with pytest.raises(ValueError, match="Unknown evidence"):
        validation.create_requirement(ValidationRequirement(id="m", description="x", target_decision_id=request.id, acceptance_condition="x"))
        validation.create_record(ValidationRecord(target_type="decision", target_id=request.id, validation_requirement_id="m", method="test", evidence_refs=["missing-evidence"]))


def test_graph_relationships_and_idempotent_trace():
    decisions, request, _, _ = build_decision()
    validation = ValidationEngine(decisions=decisions)
    validation.create_requirement(ValidationRequirement(id="m", description="measurement", target_decision_id=request.id, acceptance_condition="value"))
    validation.trace(request.id)
    validation.trace(request.id)
    relationships = {edge.relationship.value for edge in validation.graph.get_edges()}
    assert "REQUIRES_VALIDATION" in relationships and "TRACEABLE_TO" in relationships


def test_authenticated_validation_api_and_happy_path():
    client = TestClient(app)
    assert client.post("/api/v1/validation/requirements", json={"id": "api-v", "description": "x", "acceptance_condition": "x"}).status_code == 401
    response = client.post("/api/v1/validation/requirements", headers={"X-API-Key": "dev-key"}, json={"id": "api-v", "description": "x", "acceptance_condition": "x"})
    assert response.status_code == 200
    assert response.json()["epistemic_state"] == "UNKNOWN"
