from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from importlib.metadata import PackageNotFoundError, version
from typing import Any
from uuid import UUID

from tinkle.engineering_decision import EngineeringDecisionEngine, ProvenanceBundle
from tinkle.reality_engine import ClaimStatus
from tinkle.research_graph import (
    EdgeCreate,
    GraphProvenance,
    NodeType,
    RelationshipType,
    ResearchGraph,
    ResearchGraphNode,
)
from tinkle.research_graph.store import DuplicateGraphError

from .schemas import (
    DecisionTrace,
    EvidenceChain,
    EvidenceKind,
    EvidenceLink,
    InvalidationCondition,
    ReproducibilityManifest,
    ReproducibilityStatus,
    ValidationEvent,
    ValidationGate,
    ValidationGateState,
    ValidationRecord,
    ValidationRequirement,
    ValidationStatus,
)


class ValidationEngine:
    """Validation, traceability, and reproducibility over existing decisions."""

    def __init__(self, decisions: EngineeringDecisionEngine | None = None, graph: ResearchGraph | None = None) -> None:
        self.decisions = decisions or EngineeringDecisionEngine(graph=graph)
        self.graph = graph or self.decisions.graph
        self.requirements: dict[str, ValidationRequirement] = {}
        self.records: dict[UUID, ValidationRecord] = {}
        self.conditions: dict[UUID, InvalidationCondition] = {}
        self.gates: dict[UUID, ValidationGate] = {}
        self.traces: dict[UUID, DecisionTrace] = {}
        self.manifests: dict[UUID, ReproducibilityManifest] = {}
        self.history_events: dict[UUID, list[ValidationEvent]] = defaultdict(list)

    def create_requirement(self, requirement: ValidationRequirement) -> ValidationRequirement:
        if requirement.id in self.requirements:
            raise ValueError(f"Validation requirement already exists: {requirement.id}")
        if requirement.target_decision_id is not None:
            self._decision(requirement.target_decision_id)
        if requirement.target_candidate_id is not None and requirement.target_decision_id is not None:
            decision = self._decision(requirement.target_decision_id)
            if requirement.target_candidate_id not in [item.candidate_id for item in decision.options]:
                raise ValueError("Validation requirement candidate is not a decision option")
        self.requirements[requirement.id] = requirement
        if requirement.target_decision_id is not None:
            self._event(requirement.target_decision_id, "VALIDATION_REQUIRED", new_state=ValidationGateState.VALIDATION_REQUIRED, artifact_id=None, details={"validation_requirement_id": requirement.id})
            self._graph_requirement(requirement)
        return requirement

    def create_record(self, record: ValidationRecord) -> ValidationRecord:
        if record.id in self.records:
            raise ValueError(f"Validation record already exists: {record.id}")
        requirement = self._requirement(record.validation_requirement_id)
        decision_id = self._record_decision_id(record, requirement)
        if record.target_id != decision_id and record.target_type.casefold() == "decision":
            raise ValueError("Validation record target does not match its decision")
        self._validate_evidence_refs(record.evidence_refs)
        if record.status == ValidationStatus.PASSED:
            measured = self._evidence_states(record.evidence_refs)
            if not record.evidence_refs or ClaimStatus.MEASURED not in measured:
                raise ValueError("PASSED validation requires explicit measured evidence")
        canonical = self._canonical_record(record)
        record.input_hash = self._hash(canonical)
        record.result_hash = self._hash({"expected": record.expected_result, "observed": record.observed_result, "status": record.status.value, "epistemic_state": record.epistemic_state.value, "evidence_refs": sorted(record.evidence_refs)})
        self.records[record.id] = record
        self._event(decision_id, self._event_for_status(record.status), artifact_id=record.id, details={"validation_requirement_id": record.validation_requirement_id})
        self._graph_record(record, decision_id)
        return record

    def add_invalidation_condition(self, condition: InvalidationCondition) -> InvalidationCondition:
        self._decision(condition.decision_id)
        self._validate_evidence_refs(condition.evidence_refs)
        self.conditions[condition.id] = condition
        self._event(condition.decision_id, "INVALIDATION_CONDITION_ADDED", artifact_id=condition.id, details={"trigger": condition.trigger})
        return condition

    def trigger_invalidation(self, condition_id: UUID, evidence_refs: list[str]) -> InvalidationCondition:
        try:
            condition = self.conditions[condition_id]
        except KeyError as exc:
            raise KeyError(f"Invalidation condition not found: {condition_id}") from exc
        self._validate_evidence_refs(evidence_refs)
        if not condition.active:
            raise ValueError("Inactive invalidation condition cannot be triggered")
        condition.triggered = True
        condition.triggered_by = sorted(set(condition.triggered_by + evidence_refs))
        self._event(condition.decision_id, "DECISION_INVALIDATED", artifact_id=condition.id, details={"evidence_refs": evidence_refs})
        return condition

    def gate(self, decision_id: UUID) -> ValidationGate:
        decision = self._decision(decision_id)
        requirements = sorted((item for item in self.requirements.values() if item.target_decision_id == decision_id), key=lambda item: item.id)
        records = [item for item in self.records.values() if item.validation_requirement_id in {req.id for req in requirements}]
        conflicts = self._conflicting_evidence(records)
        invalidations = [item for item in self.conditions.values() if item.decision_id == decision_id and item.triggered]
        missing = [item.id for item in requirements if not any(record.validation_requirement_id == item.id and record.status not in {ValidationStatus.NOT_STARTED, ValidationStatus.REQUIRED} for record in records)]
        if invalidations:
            state = ValidationGateState.INVALIDATED
        elif conflicts:
            state = ValidationGateState.DATA_INSUFFICIENT
        elif not requirements:
            state = ValidationGateState.VALIDATION_REQUIRED if decision.recommendation else ValidationGateState.VALIDATION_NOT_REQUIRED
        elif missing:
            state = ValidationGateState.VALIDATION_REQUIRED
        elif any(item.status == ValidationStatus.FAILED for item in records):
            state = ValidationGateState.VALIDATION_FAILED
        elif any(item.status == ValidationStatus.INCONCLUSIVE for item in records):
            state = ValidationGateState.VALIDATION_INCONCLUSIVE
        elif all(item.status == ValidationStatus.PASSED for item in records) and all(self._record_has_measured_evidence(item) for item in records):
            state = ValidationGateState.VALIDATED
        else:
            state = ValidationGateState.DATA_INSUFFICIENT
        epistemic = ClaimStatus.MEASURED if state == ValidationGateState.VALIDATED else ClaimStatus.UNKNOWN
        gate = ValidationGate(decision_id=decision_id, state=state, requirement_ids=[item.id for item in requirements], record_ids=[item.id for item in sorted(records, key=lambda item: str(item.id))], missing_requirements=missing, conflicting_evidence_ids=conflicts, invalidation_condition_ids=[item.id for item in invalidations], explanation=self._gate_explanation(state, missing, conflicts), assumptions=decision.assumptions, limitations=["A validation gate records declared evidence status; it is not a claim of universal scientific truth."], provenance=decision.provenance, epistemic_state=epistemic)
        self.gates[decision_id] = gate
        return gate

    def trace(self, decision_id: UUID) -> DecisionTrace:
        decision = self._decision(decision_id)
        requirements = sorted((item for item in self.requirements.values() if item.target_decision_id == decision_id), key=lambda item: item.id)
        options = sorted(decision.options, key=lambda item: str(item.candidate_id))
        evidence_ids = sorted(set(decision.evidence_refs + [ref for criterion in decision.criteria for ref in criterion.evidence_refs]))
        validation_ids = sorted((item.id for item in self.records.values() if item.validation_requirement_id in {req.id for req in requirements}), key=str)
        trace_input = {"decision": decision.model_dump(mode="json", exclude={"id", "created_at"}), "requirements": [item.model_dump(mode="json") for item in requirements], "validation_ids": [str(item) for item in validation_ids], "evidence_ids": evidence_ids}
        trace_hash = self._hash(trace_input)
        trace = DecisionTrace(root_decision_id=decision_id, requirement_ids=[item for item in decision.options[0].evaluation.requirements_evaluated] if decision.options and decision.options[0].evaluation else [], candidate_ids=[item.candidate_id for item in options], evaluation_ids=[item.evaluation_id for item in options if item.evaluation_id is not None], criteria=decision.criteria, evidence_ids=evidence_ids, validation_ids=validation_ids, graph_relationships=[RelationshipType.TRACEABLE_TO.value, RelationshipType.REQUIRES_VALIDATION.value], assumptions=decision.assumptions, limitations=decision.limitations, provenance=decision.provenance.model_copy(update={"method": "decision_trace_v1", "input_hash": trace_hash}), canonical_input_hash=trace_hash)
        self.traces[decision_id] = trace
        self._graph_trace(decision_id, trace)
        return trace

    def evidence_chain(self, decision_id: UUID) -> EvidenceChain:
        decision = self._decision(decision_id)
        trace = self.traces.get(decision_id) or self.trace(decision_id)
        links: list[EvidenceLink] = []
        sequence = 1
        for candidate_id in trace.candidate_ids:
            links.append(EvidenceLink(sequence=sequence, kind=EvidenceKind.DERIVED, artifact_id=str(candidate_id)))
            sequence += 1
        for option in decision.options:
            if option.evaluation_id:
                links.append(EvidenceLink(sequence=sequence, kind=EvidenceKind.SIMULATED if option.simulation_refs else EvidenceKind.DERIVED, artifact_id=str(option.evaluation_id), epistemic_state=option.evaluation.epistemic_state if option.evaluation else ClaimStatus.UNKNOWN))
                sequence += 1
                for ref in option.simulation_refs + option.uncertainty_refs + option.sensitivity_refs:
                    links.append(EvidenceLink(sequence=sequence, kind=EvidenceKind.SIMULATED, artifact_id=ref, epistemic_state=ClaimStatus.SIMULATED))
                    sequence += 1
        for ref in trace.evidence_ids:
            evidence = self.decisions.evidence.get(ref)
            links.append(EvidenceLink(sequence=sequence, kind=self._kind(evidence.epistemic_state if evidence else ClaimStatus.UNKNOWN), artifact_id=ref, epistemic_state=evidence.epistemic_state if evidence else ClaimStatus.UNKNOWN, provenance=evidence.provenance if evidence else ProvenanceBundle()))
            sequence += 1
        missing = sorted(set(self.gate(decision_id).missing_requirements))
        payload = {"decision_id": str(decision_id), "links": [item.model_dump(mode="json") for item in links], "missing": missing}
        return EvidenceChain(decision_id=decision_id, links=links, missing_evidence=missing, conflicts=self._conflicting_evidence([item for item in self.records.values() if item.validation_requirement_id in set(missing)]), input_hash=self._hash(payload), provenance=decision.provenance)

    def reproducibility(self, decision_id: UUID) -> ReproducibilityManifest:
        decision = self._decision(decision_id)
        trace = self.traces.get(decision_id) or self.trace(decision_id)
        validation_ids = sorted((item.id for item in self.records.values() if item.target_id in trace.candidate_ids or item.target_id == decision_id), key=str)
        missing: list[str] = []
        if not decision.input_hash:
            missing.append("decision.input_hash")
        if any(item.evaluation_id is None for item in decision.options):
            missing.append("candidate evaluation")
        if not decision.criterion_weights:
            missing.append("criterion weights")
        status = ReproducibilityStatus.REPRODUCIBLE if not missing else ReproducibilityStatus.PARTIALLY_REPRODUCIBLE if decision.input_hash else ReproducibilityStatus.UNKNOWN
        model_ids = sorted({option.evaluation.provenance.model_id for option in decision.options if option.evaluation and option.evaluation.provenance.model_id})
        data = {"decision_id": str(decision_id), "input_hash": decision.input_hash, "candidate_ids": [str(item.candidate_id) for item in decision.options], "evaluation_ids": [str(item.evaluation_id) for item in decision.options if item.evaluation_id], "weights": decision.criterion_weights, "evidence_ids": sorted(decision.evidence_refs), "validation_ids": [str(item) for item in validation_ids], "method": decision.method}
        manifest_hash = self._hash(data)
        manifest = ReproducibilityManifest(decision_id=decision_id, canonical_input_hash=decision.input_hash, candidate_ids=[item.candidate_id for item in decision.options], evaluation_ids=[item.evaluation_id for item in decision.options if item.evaluation_id], criterion_definitions=decision.criteria, criterion_weights=decision.criterion_weights, evidence_ids=sorted(decision.evidence_refs), validation_ids=validation_ids, simulation_model_ids=model_ids, assumptions=decision.assumptions, uncertainty_configuration={"uncertainty_refs": sorted(ref for option in decision.options for ref in option.uncertainty_refs)}, software_metadata={"tinkle": self._package_version()}, status=status, missing_inputs=missing, provenance=decision.provenance, canonical_manifest_hash=manifest_hash)
        self.manifests[decision_id] = manifest
        return manifest

    def history(self, decision_id: UUID) -> list[ValidationEvent]:
        self._decision(decision_id)
        return list(self.history_events[decision_id])

    def _decision(self, decision_id: UUID):
        try:
            return self.decisions.decisions[decision_id]
        except KeyError as exc:
            raise KeyError(f"Decision not found: {decision_id}") from exc

    def _requirement(self, requirement_id: str) -> ValidationRequirement:
        try:
            return self.requirements[requirement_id]
        except KeyError as exc:
            raise KeyError(f"Validation requirement not found: {requirement_id}") from exc

    def _record_decision_id(self, record: ValidationRecord, requirement: ValidationRequirement) -> UUID:
        if requirement.target_decision_id is not None:
            self._decision(requirement.target_decision_id)
            return requirement.target_decision_id
        if requirement.target_candidate_id is not None:
            for decision in self.decisions.decisions.values():
                if requirement.target_candidate_id in [item.candidate_id for item in decision.options]:
                    return decision.request_id
        raise ValueError("Validation requirement must target a known decision or candidate")

    def _validate_evidence_refs(self, refs: list[str]) -> None:
        missing = [ref for ref in refs if ref not in self.decisions.evidence and not ref.startswith("http")]
        if missing:
            raise ValueError(f"Unknown evidence ids: {', '.join(missing)}")

    def _evidence_states(self, refs: list[str]) -> set[ClaimStatus]:
        return {self.decisions.evidence[ref].epistemic_state for ref in refs if ref in self.decisions.evidence}

    def _record_has_measured_evidence(self, record: ValidationRecord) -> bool:
        return ClaimStatus.MEASURED in self._evidence_states(record.evidence_refs)

    def _conflicting_evidence(self, records: list[ValidationRecord]) -> list[str]:
        grouped: dict[tuple[str, str, str | None], list[ValidationRecord]] = defaultdict(list)
        for record in records:
            if isinstance(record.observed_result, (int, float)):
                grouped[(record.validation_requirement_id, record.method, record.units)].append(record)
        conflicts: set[str] = set()
        for group in grouped.values():
            values = {float(item.observed_result) for item in group}
            if len(values) > 1:
                for item in group:
                    conflicts.update(item.evidence_refs or [str(item.id)])
        return sorted(conflicts)

    @staticmethod
    def _canonical_record(record: ValidationRecord) -> dict[str, Any]:
        return record.model_dump(mode="json", exclude={"id", "timestamp", "input_hash", "result_hash"})

    @staticmethod
    def _hash(value: Any) -> str:
        return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()

    @staticmethod
    def _event_for_status(status: ValidationStatus) -> str:
        return {ValidationStatus.PASSED: "VALIDATION_PASSED", ValidationStatus.FAILED: "VALIDATION_FAILED", ValidationStatus.INCONCLUSIVE: "VALIDATION_INCONCLUSIVE", ValidationStatus.IN_PROGRESS: "VALIDATION_STARTED"}.get(status, "VALIDATION_RECORD_CREATED")

    def _event(self, decision_id: UUID, event_type: str, new_state: ValidationGateState | None = None, artifact_id: UUID | None = None, details: dict[str, Any] | None = None) -> None:
        self.history_events[decision_id].append(ValidationEvent(decision_id=decision_id, event_type=event_type, new_state=new_state, artifact_id=artifact_id, details=details or {}, provenance=self.decisions.decisions[decision_id].provenance))

    @staticmethod
    def _kind(state: ClaimStatus) -> EvidenceKind:
        return {ClaimStatus.MEASURED: EvidenceKind.MEASURED, ClaimStatus.SOURCE_BACKED: EvidenceKind.SOURCE_BACKED, ClaimStatus.SIMULATED: EvidenceKind.SIMULATED, ClaimStatus.ASSUMED: EvidenceKind.ASSUMED}.get(state, EvidenceKind.UNKNOWN)

    @staticmethod
    def _gate_explanation(state: ValidationGateState, missing: list[str], conflicts: list[str]) -> list[str]:
        if conflicts:
            return ["Conflicting evidence was detected; no evidence was silently selected.", f"Conflicting references: {', '.join(conflicts)}"]
        if missing:
            return [f"Validation remains required for: {', '.join(missing)}"]
        return [f"Validation gate state is {state.value}."]

    @staticmethod
    def _package_version() -> str:
        try:
            return version("tinkle")
        except PackageNotFoundError:
            return "unknown"

    def _graph_requirement(self, requirement: ValidationRequirement) -> None:
        node = self.graph.create_node(ResearchGraphNode(type=NodeType.EXPERIMENT, name=requirement.id, description=requirement.description, properties=requirement.model_dump(mode="json"), metadata={"phase": 9, "artifact": "validation_requirement"}, epistemic_state=requirement.epistemic_state))
        decision_node = self.decisions._decision_nodes.get(requirement.target_decision_id) if requirement.target_decision_id else None
        if decision_node:
            self._edge(decision_node, node.id, RelationshipType.REQUIRES_VALIDATION, requirement.epistemic_state)

    def _graph_record(self, record: ValidationRecord, decision_id: UUID) -> None:
        node = self.graph.create_node(ResearchGraphNode(type=NodeType.RESULT, name=str(record.id), description=record.method, properties=record.model_dump(mode="json"), metadata={"phase": 9, "artifact": "validation_record"}, epistemic_state=record.epistemic_state))
        decision_node = self.decisions._decision_nodes.get(decision_id)
        if decision_node:
            self._edge(node.id, decision_node, RelationshipType.VALIDATES if record.status == ValidationStatus.PASSED else RelationshipType.INFORMS, record.epistemic_state)

    def _graph_trace(self, decision_id: UUID, trace: DecisionTrace) -> None:
        node = self.graph.create_node(ResearchGraphNode(type=NodeType.RESULT, name=f"Trace {trace.canonical_input_hash[:12]}", description="Machine-readable decision trace", properties=trace.model_dump(mode="json"), metadata={"phase": 9, "artifact": "decision_trace"}, epistemic_state=ClaimStatus.SIMULATED))
        decision_node = self.decisions._decision_nodes.get(decision_id)
        if decision_node:
            self._edge(node.id, decision_node, RelationshipType.TRACEABLE_TO, ClaimStatus.SIMULATED)

    def _edge(self, source: UUID, target: UUID, relationship: RelationshipType, state: ClaimStatus) -> None:
        try:
            self.graph.create_edge(EdgeCreate(source_id=source, target_id=target, relationship=relationship, epistemic_state=state, provenance=GraphProvenance(notes="Phase 9 validation trace")))
        except DuplicateGraphError:
            pass


__all__ = ["ValidationEngine"]
