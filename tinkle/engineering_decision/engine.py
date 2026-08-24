from __future__ import annotations

import hashlib
import json
from itertools import combinations
from typing import Any
from uuid import UUID

from tinkle.invention_design import InventionDesignEngine
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
    CriterionDirection,
    DecisionEvent,
    DecisionEvidence,
    DecisionOption,
    DecisionRequest,
    DecisionState,
    EngineeringDecision,
    Tradeoff,
)


class EngineeringDecisionEngine:
    """Evidence-bound decision orchestration over Phase 7 design evaluations."""

    def __init__(self, invention: InventionDesignEngine | None = None, graph: ResearchGraph | None = None) -> None:
        self.invention = invention or InventionDesignEngine(graph=graph)
        self.graph = graph or self.invention.graph
        self.requests: dict[UUID, DecisionRequest] = {}
        self.evidence: dict[str, DecisionEvidence] = {}
        self.decisions: dict[UUID, EngineeringDecision] = {}
        self.events: dict[UUID, list[DecisionEvent]] = {}
        self._decision_nodes: dict[UUID, UUID] = {}

    def create_evidence(self, evidence: DecisionEvidence) -> DecisionEvidence:
        key = str(evidence.id)
        if key in self.evidence:
            raise ValueError(f"Evidence already exists: {key}")
        self.evidence[key] = evidence
        return evidence

    def create_request(self, request: DecisionRequest) -> DecisionRequest:
        if request.id in self.requests:
            raise ValueError(f"Decision request already exists: {request.id}")
        self._validate_request(request)
        self.requests[request.id] = request
        self.events[request.id] = [DecisionEvent(artifact_id=request.id, event_type="REQUEST_CREATED", new_state=DecisionState.UNDECIDED, provenance=request.provenance)]
        node = self.graph.create_node(ResearchGraphNode(type=NodeType.CLAIM, name=request.title, description=request.objective, properties={"request_id": str(request.id)}, metadata={"phase": 8, "artifact": "decision_request"}, epistemic_state=request.epistemic_state, provenance=GraphProvenance(notes="Phase 8 engineering decision request")))
        self._decision_nodes[request.id] = node.id
        return request

    def evaluate(self, request_id: UUID) -> EngineeringDecision:
        request = self.get_request(request_id)
        options = self._options(request)
        missing = list(request.unresolved_unknowns)
        conflicts: list[str] = []
        hard_failures: dict[str, list[str]] = {}
        exclusions: dict[str, list[str]] = {}
        for option in options:
            if option.evaluation is None:
                missing.append(f"evaluation:{option.candidate_id}")
                continue
            failed_hard = [item.requirement_id for item in option.evaluation.constraints if getattr(item.status, "value", item.status) == "FAIL" and self.invention.state.requirements.get(item.requirement_id, None) and self.invention.state.requirements[item.requirement_id].hard_constraint]
            if failed_hard:
                hard_failures[str(option.candidate_id)] = failed_hard
                exclusions[str(option.candidate_id)] = ["hard_constraint_failure"]
            if option.evaluation.unknown_constraints:
                missing.extend(f"{option.candidate_id}:{item}" for item in option.evaluation.unknown_constraints)
        criteria_missing, normalized, scores, weights = self._score(request, options)
        missing.extend(criteria_missing)
        tradeoffs = self._tradeoffs(request, options)
        if hard_failures and len(hard_failures) == len(options) and not request.allow_constraint_relaxation:
            state = DecisionState.CONSTRAINED
        elif missing:
            state = DecisionState.DATA_INSUFFICIENT
        elif tradeoffs and len({item.magnitude for item in tradeoffs}) > 1:
            state = DecisionState.TRADEOFF_REQUIRED
        else:
            state = DecisionState.RECOMMENDED
        recommendation = self._recommendation(options, scores, hard_failures, request, state)
        epistemic_state = self._epistemic_state(options, request, recommendation)
        input_data = self._canonical_input(request, options)
        input_hash = self._hash(input_data)
        analysis_refs = list(request.provenance.analysis_refs)
        analysis_refs.extend(str(item.evaluation_id) for item in options if item.evaluation_id is not None)
        provenance = request.provenance.model_copy(update={"method": "explicit_weighted_sum_v1", "input_hash": input_hash, "analysis_refs": sorted(set(analysis_refs))})
        decision = EngineeringDecision(request_id=request.id, state=state, options=options, recommendation=recommendation, criteria=request.criteria, tradeoffs=tradeoffs, evidence_refs=request.evidence_refs, missing_evidence=sorted(set(missing)), conflicts=conflicts, hard_constraint_failures=hard_failures, scores=scores, normalized_values=normalized, criterion_weights=weights, exclusions=exclusions, input_hash=input_hash, explanation=self._explanation(request, options, state, recommendation, missing, tradeoffs), assumptions=request.assumptions, limitations=["A recommendation is an engineering decision, not scientific or physical validation.", "Scores use only explicit criterion values and weights.", "Simulation remains SIMULATED and is not a measurement."], validation_requirements=self._validation_requirements(state, missing, epistemic_state), provenance=provenance, epistemic_state=epistemic_state)
        self.decisions[request.id] = decision
        self._append_event(request.id, "DECISION_EVALUATED", DecisionState.UNDECIDED, state, {"decision_id": str(decision.id), "recommendation": str(recommendation) if recommendation else None})
        self._graph_decision(request, decision)
        return decision

    def tradeoffs(self, request_id: UUID) -> list[Tradeoff]:
        decision = self.decisions.get(request_id) or self.evaluate(request_id)
        return decision.tradeoffs

    def decide(self, request_id: UUID, selected_candidate: UUID | None = None) -> EngineeringDecision:
        decision = self.decisions.get(request_id) or self.evaluate(request_id)
        if selected_candidate is not None:
            if selected_candidate not in [item.candidate_id for item in decision.options]:
                raise ValueError("Selected candidate is not an option")
            if decision.state != DecisionState.RECOMMENDED or selected_candidate != decision.recommendation:
                raise ValueError("Only the justified recommendation can be selected")
            decision.selected_candidate = selected_candidate
            decision.state = DecisionState.SELECTED
            self._append_event(request_id, "CANDIDATE_SELECTED", DecisionState.RECOMMENDED, DecisionState.SELECTED, {"candidate_id": str(selected_candidate)})
        return decision

    def get_request(self, request_id: UUID) -> DecisionRequest:
        try:
            return self.requests[request_id]
        except KeyError as exc:
            raise KeyError(f"Decision request not found: {request_id}") from exc

    def history(self, request_id: UUID) -> list[DecisionEvent]:
        self.get_request(request_id)
        return list(self.events[request_id])

    def _validate_request(self, request: DecisionRequest) -> None:
        missing_candidates = [str(item) for item in request.candidate_refs if item not in self.invention.state.candidates]
        missing_requirements = [item for item in request.requirement_refs if item not in self.invention.state.requirements]
        if missing_candidates:
            raise ValueError(f"Unknown candidate ids: {', '.join(missing_candidates)}")
        if missing_requirements:
            raise ValueError(f"Unknown requirement ids: {', '.join(missing_requirements)}")
        known_evaluations = {
            evaluation.id
            for candidate_id in request.candidate_refs
            for evaluation in self.invention.state.evaluations.get(candidate_id, [])
        }
        missing_evaluations = [str(item) for item in request.evaluation_refs if item not in known_evaluations]
        if missing_evaluations:
            raise ValueError(f"Unknown evaluation ids: {', '.join(missing_evaluations)}")
        evidence_refs = set(request.evidence_refs)
        evidence_refs.update(item for criterion in request.criteria for item in criterion.evidence_refs)
        unknown_evidence = [item for item in evidence_refs if item not in self.evidence and not item.startswith("http")]
        if unknown_evidence:
            raise ValueError(f"Unknown evidence ids: {', '.join(unknown_evidence)}")
        if len(set(request.candidate_refs)) != len(request.candidate_refs):
            raise ValueError("Candidate references must be unique")
        if request.requirement_refs and any(set(self.invention.state.candidates[item].requirement_ids) != set(request.requirement_refs) for item in request.candidate_refs):
            raise ValueError("Candidates are not comparable for the requested requirements")

    def _options(self, request: DecisionRequest) -> list[DecisionOption]:
        options: list[DecisionOption] = []
        requested_evaluations = set(request.evaluation_refs)
        for candidate_id in request.candidate_refs:
            evaluations = self.invention.state.evaluations.get(candidate_id, [])
            matches = [item for item in evaluations if not requested_evaluations or item.id in requested_evaluations]
            evaluation = matches[-1] if matches else None
            candidate = self.invention.state.candidates[candidate_id]
            research_refs = candidate.provenance.hypothesis_refs + candidate.provenance.prediction_refs + candidate.provenance.experiment_refs
            options.append(DecisionOption(candidate_id=candidate_id, evaluation_id=evaluation.id if evaluation else None, evaluation=evaluation, constraint_results=[self._status_value(item.status) for item in evaluation.constraints] if evaluation else [], simulation_refs=evaluation.simulation_refs if evaluation else [], uncertainty_refs=evaluation.uncertainty_refs if evaluation else [], sensitivity_refs=evaluation.sensitivity_refs if evaluation else [], research_refs=research_refs, limitations=evaluation.limitations if evaluation else ["Candidate has no Phase 7 evaluation."]))
        return options

    def _score(self, request: DecisionRequest, options: list[DecisionOption]) -> tuple[list[str], dict[str, dict[str, float]], dict[str, float], dict[str, float]]:
        missing: list[str] = []
        normalized: dict[str, dict[str, float]] = {}
        scores = {str(item.candidate_id): 0.0 for item in options}
        weights: dict[str, float] = {}
        for criterion in request.criteria:
            if criterion.weight is None:
                missing.append(f"criterion_weight:{criterion.name}")
                continue
            weights[criterion.name] = criterion.weight
            numeric = {str(option.candidate_id): value for option in options if isinstance((value := criterion.values.get(str(option.candidate_id))), (int, float)) and criterion.epistemic_state != ClaimStatus.UNKNOWN}
            if len(numeric) != len(options):
                missing.extend(f"criterion:{criterion.name}:{option.candidate_id}" for option in options if str(option.candidate_id) not in numeric)
                continue
            low, high = min(numeric.values()), max(numeric.values())
            if high == low:
                values = {key: 1.0 for key in numeric}
            elif criterion.direction == CriterionDirection.MINIMIZE:
                values = {key: (high - value) / (high - low) for key, value in numeric.items()}
            else:
                values = {key: (value - low) / (high - low) for key, value in numeric.items()}
            normalized[criterion.name] = values
            for key, value in values.items():
                scores[key] += criterion.weight * value
        return missing, normalized, scores, weights

    def _recommendation(self, options: list[DecisionOption], scores: dict[str, float], failures: dict[str, list[str]], request: DecisionRequest, state: DecisionState) -> UUID | None:
        if state != DecisionState.RECOMMENDED:
            return None
        eligible = [item.candidate_id for item in options if str(item.candidate_id) not in failures]
        return min(eligible, key=lambda item: (-scores[str(item)], str(item))) if eligible else None

    def _tradeoffs(self, request: DecisionRequest, options: list[DecisionOption]) -> list[Tradeoff]:
        result: list[Tradeoff] = []
        for criterion in request.criteria:
            for first, second in combinations(options, 2):
                left, right = criterion.values.get(str(first.candidate_id)), criterion.values.get(str(second.candidate_id))
                if isinstance(left, (int, float)) and isinstance(right, (int, float)) and criterion.epistemic_state != ClaimStatus.UNKNOWN:
                    direction = "A_HIGHER" if left > right else "B_HIGHER" if right > left else "EQUAL"
                    magnitude = abs(float(left) - float(right))
                    state = criterion.epistemic_state
                else:
                    direction, magnitude, state = "UNKNOWN", None, ClaimStatus.UNKNOWN
                result.append(Tradeoff(criterion=criterion.name, option_a=first.candidate_id, option_b=second.candidate_id, evidence_refs=criterion.evidence_refs, direction=direction, magnitude=magnitude, uncertainty="UNKNOWN" if not criterion.evidence_refs else "As specified by evidence references", limitation="Criterion values are caller-supplied and do not establish physical performance.", epistemic_state=state))
        return result

    def _epistemic_state(self, options: list[DecisionOption], request: DecisionRequest, recommendation: UUID | None) -> ClaimStatus:
        states = [item.evaluation.epistemic_state for item in options if item.evaluation is not None]
        states.extend(self.evidence[item].epistemic_state for item in request.evidence_refs if item in self.evidence)
        if any(item == ClaimStatus.MEASURED for item in states):
            return ClaimStatus.MEASURED
        if states and all(item == ClaimStatus.SOURCE_BACKED for item in states):
            return ClaimStatus.SOURCE_BACKED
        if any(item == ClaimStatus.SIMULATED for item in states):
            return ClaimStatus.SIMULATED
        return ClaimStatus.ESTIMATED if recommendation else ClaimStatus.UNKNOWN

    @staticmethod
    def _canonical_input(request: DecisionRequest, options: list[DecisionOption]) -> dict[str, Any]:
        return {"request": request.model_dump(mode="json", exclude={"id", "created_at"}), "options": [item.model_dump(mode="json", exclude={"evaluation": {"id"}}) for item in options]}

    @staticmethod
    def _hash(value: Any) -> str:
        return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()

    @staticmethod
    def _explanation(request: DecisionRequest, options: list[DecisionOption], state: DecisionState, recommendation: UUID | None, missing: list[str], tradeoffs: list[Tradeoff]) -> list[str]:
        lines = [f"Decision objective: {request.objective}.", f"Compared {len(options)} existing Phase 7 candidate(s) against {len(request.criteria)} explicit criterion/criteria."]
        if recommendation:
            lines.append(f"Candidate {recommendation} is recommended by the explicit weighted method after hard-constraint screening.")
        else:
            lines.append(f"No candidate is recommended because the decision state is {state.value}.")
        if tradeoffs:
            lines.append(f"Preserved {len(tradeoffs)} criterion trade-off(s) instead of hiding them in a single score.")
        if missing:
            lines.append(f"Missing or unknown inputs remain explicit: {len(set(missing))} item(s).")
        return lines

    @staticmethod
    def _validation_requirements(state: DecisionState, missing: list[str], epistemic_state: ClaimStatus) -> list[str]:
        requirements = ["Validate the selected design with appropriate physical measurements before release."]
        if state != DecisionState.RECOMMENDED or missing:
            requirements.append("Resolve every missing criterion, evaluation, and constraint datum before selection.")
        if epistemic_state == ClaimStatus.SIMULATED:
            requirements.append("Compare simulated outputs with measurements; simulation is not measurement.")
        return requirements

    def _append_event(self, request_id: UUID, event_type: str, previous: DecisionState, new: DecisionState, details: dict[str, Any]) -> None:
        self.events[request_id].append(DecisionEvent(artifact_id=request_id, event_type=event_type, previous_state=previous, new_state=new, details=details, provenance=self.get_request(request_id).provenance))

    def _graph_decision(self, request: DecisionRequest, decision: EngineeringDecision) -> None:
        node_id = self._decision_nodes[request.id]
        for option in decision.options:
            candidate = self.invention.state.candidates[option.candidate_id]
            candidates = self.graph.search_graph(__import__("tinkle.research_graph", fromlist=["GraphSearchRequest"]).GraphSearchRequest(query=candidate.name, node_type=NodeType.DESIGN))
            if candidates:
                relationship = RelationshipType.SELECTS if decision.recommendation == option.candidate_id else RelationshipType.INFORMS
                try:
                    self.graph.create_edge(EdgeCreate(source_id=candidates[0].id, target_id=node_id, relationship=relationship, epistemic_state=decision.epistemic_state, provenance=GraphProvenance(notes="Phase 8 decision trace")))
                except DuplicateGraphError:
                    pass

    @staticmethod
    def _status_value(status: Any) -> str:
        return str(getattr(status, "value", status))


__all__ = ["EngineeringDecisionEngine"]
