from __future__ import annotations

import hashlib
import json
from typing import Any
from uuid import UUID

from tinkle.reality_engine import ClaimStatus
from tinkle.research_graph import (
    EdgeCreate,
    GraphProvenance,
    NodeType,
    RelationshipType,
    ResearchGraph,
    ResearchGraphNode,
)
from tinkle.research_graph.store import SQLiteResearchGraphStore
from tinkle.simulation_engine import AnalysisRequest, PhysicsLabEngine, UncertaintyEngine

from .schemas import (
    CandidateComparison,
    CandidateLifecycle,
    ConstraintResult,
    ConstraintStatus,
    DesignCandidate,
    DesignEvaluation,
    EngineeringRequirement,
    EvaluationRequest,
    InventionDesignState,
    ProvenanceBundle,
)


class InventionDesignEngine:
    """Orchestrate auditable engineering synthesis over existing Phase 4/5 systems."""

    def __init__(self, graph: ResearchGraph | None = None, physics: PhysicsLabEngine | None = None) -> None:
        self.graph = graph or ResearchGraph(SQLiteResearchGraphStore(":memory:"))
        self.physics = physics or PhysicsLabEngine(self.graph)
        self.uncertainty = UncertaintyEngine(self.physics, self.graph)
        self.state = InventionDesignState()
        self._requirement_nodes: dict[str, UUID] = {}

    def create_requirement(self, requirement: EngineeringRequirement) -> EngineeringRequirement:
        if requirement.id in self.state.requirements:
            raise ValueError(f"Requirement already exists: {requirement.id}")
        if requirement.minimum is not None and requirement.maximum is not None and requirement.minimum > requirement.maximum:
            raise ValueError("minimum cannot exceed maximum")
        self.state.requirements[requirement.id] = requirement
        self._record_requirement(requirement)
        return requirement

    def create_candidate(self, candidate: DesignCandidate) -> DesignCandidate:
        missing = sorted(set(candidate.requirement_ids) - self.state.requirements.keys())
        if missing:
            raise ValueError(f"Unknown requirement ids: {', '.join(missing)}")
        self.state.candidates[candidate.id] = candidate
        self.state.history[candidate.id] = [{"event": "CANDIDATE_CREATED", "lifecycle": candidate.lifecycle.value}]
        candidate_node = self.graph.create_node(ResearchGraphNode(
            type=NodeType.DESIGN,
            name=candidate.name,
            description=candidate.description,
            properties={"candidate_id": str(candidate.id)},
            metadata={"phase": 7, "artifact": "design_candidate", "provenance": candidate.provenance.model_dump(mode="json")},
            epistemic_state=candidate.epistemic_state,
        ))
        for requirement_id in candidate.requirement_ids:
            requirement_node = self._requirement_nodes.get(requirement_id)
            if requirement_node is not None:
                self.graph.create_edge(EdgeCreate(source_id=candidate_node.id, target_id=requirement_node, relationship=RelationshipType.CONSTRAINED_BY, epistemic_state=self.state.requirements[requirement_id].epistemic_state, provenance=GraphProvenance(notes="Phase 7 requirement association")))
        return candidate

    def evaluate(self, candidate_id: UUID, request: EvaluationRequest) -> DesignEvaluation:
        candidate = self.get_candidate(candidate_id)
        actual = dict(request.actual_values)
        simulation_refs: list[str] = []
        uncertainty_refs: list[str] = []
        sensitivity_refs: list[str] = []
        assumptions = list(candidate.assumptions)
        limitations = ["Digital evaluation is not experimental measurement.", "Passing constraints does not establish physical safety, manufacturability, or certification."]
        model_id: str | None = None
        if request.simulation is not None:
            simulation = self.physics.simulate(request.simulation)
            simulation_refs.append(str(simulation.simulation_id))
            model_id = str(simulation.model_id)
            if simulation.outputs:
                actual.update(simulation.outputs[-1])
            assumptions.extend(simulation.assumptions)
            limitations.extend(simulation.limitations)
            if request.ranges:
                analysis_request = AnalysisRequest(simulation=request.simulation, ranges=request.ranges, output=request.output)
                uncertainty_result = self.uncertainty.uncertainty(analysis_request)
                uncertainty_refs.append(str(uncertainty_result.analysis_id))
                sensitivity_refs.extend(str(item.analysis_id) for item in self.uncertainty.sensitivity(analysis_request))
        constraints = [self._check(self.state.requirements[item], actual, model_id) for item in candidate.requirement_ids]
        passed = [item.requirement_id for item in constraints if item.status == ConstraintStatus.PASS]
        failed = [item.requirement_id for item in constraints if item.status == ConstraintStatus.FAIL]
        unknown = [item.requirement_id for item in constraints if item.status == ConstraintStatus.UNKNOWN]
        score = request.objective_score if request.objective_score is not None else (len(passed) / len(constraints) if constraints and not unknown else None)
        state = ClaimStatus.SIMULATED if simulation_refs else ClaimStatus.ESTIMATED
        provenance = candidate.provenance.model_copy(update={"simulation_refs": simulation_refs, "analysis_refs": uncertainty_refs + sensitivity_refs, "model_id": model_id, "method": "deterministic_constraint_evaluation", "input_hash": self._hash(request.model_dump(mode="json"))})
        evaluation = DesignEvaluation(candidate_id=candidate.id, requirements_evaluated=candidate.requirement_ids, constraints=constraints, simulation_refs=simulation_refs, uncertainty_refs=uncertainty_refs, sensitivity_refs=sensitivity_refs, passed_constraints=passed, failed_constraints=failed, unknown_constraints=unknown, score=score, assumptions=assumptions, limitations=limitations, provenance=provenance, epistemic_state=state)
        self.state.evaluations.setdefault(candidate.id, []).append(evaluation)
        candidate.lifecycle = CandidateLifecycle.REQUIRES_DATA if unknown else CandidateLifecycle.REJECTED if failed else CandidateLifecycle.EVALUATED
        self.state.history[candidate.id].append({"event": "CANDIDATE_EVALUATED", "evaluation_id": str(evaluation.id), "lifecycle": candidate.lifecycle.value})
        return evaluation

    def compare(self, candidate_ids: list[UUID]) -> CandidateComparison:
        evaluations = {candidate_id: self.state.evaluations.get(candidate_id, [])[-1] if self.state.evaluations.get(candidate_id) else None for candidate_id in candidate_ids}
        missing: dict[str, list[str]] = {}
        scores: dict[str, float] = {}
        for candidate_id, evaluation in evaluations.items():
            if evaluation is None:
                missing[str(candidate_id)] = ["evaluation"]
            elif evaluation.unknown_constraints:
                missing[str(candidate_id)] = evaluation.unknown_constraints
            elif evaluation.score is None:
                missing[str(candidate_id)] = ["objective score"]
            else:
                scores[str(candidate_id)] = evaluation.score
        if missing:
            return CandidateComparison(status="REQUIRES_DATA", scores=scores, missing_information=missing, rationale=["Ranking requires complete, comparable evaluations."], provenance=ProvenanceBundle(method="deterministic_candidate_comparison"), epistemic_state=ClaimStatus.UNKNOWN)
        ranked = sorted(candidate_ids, key=lambda item: (-scores[str(item)], str(item)))
        return CandidateComparison(status="RANKED", ranked_candidate_ids=ranked, scores=scores, rationale=["Ranked by supplied objective score, then UUID for deterministic tie-breaking."], provenance=ProvenanceBundle(method="deterministic_candidate_comparison"), epistemic_state=ClaimStatus.ESTIMATED)

    def get_candidate(self, candidate_id: UUID) -> DesignCandidate:
        try:
            return self.state.candidates[candidate_id]
        except KeyError as exc:
            raise KeyError(f"Design candidate not found: {candidate_id}") from exc

    def history(self, candidate_id: UUID) -> list[dict[str, Any]]:
        self.get_candidate(candidate_id)
        return list(self.state.history[candidate_id])

    @staticmethod
    def _check(requirement: EngineeringRequirement, actual: dict[str, float | str], model_id: str | None) -> ConstraintResult:
        value = actual.get(requirement.id)
        provenance = requirement.provenance.model_copy(update={"model_id": model_id})
        if requirement.epistemic_state == ClaimStatus.UNKNOWN or value is None or not isinstance(value, (int, float)):
            return ConstraintResult(requirement_id=requirement.id, required_condition=InventionDesignEngine._condition(requirement), actual_value=value, status=ConstraintStatus.UNKNOWN, provenance=provenance, epistemic_state=ClaimStatus.UNKNOWN)
        numeric = float(value)
        if requirement.minimum is not None:
            margin = numeric - requirement.minimum
            status = ConstraintStatus.PASS if numeric >= requirement.minimum else ConstraintStatus.FAIL
        elif requirement.maximum is not None:
            margin = requirement.maximum - numeric
            status = ConstraintStatus.PASS if numeric <= requirement.maximum else ConstraintStatus.FAIL
        elif isinstance(requirement.target, (int, float)):
            margin = numeric - float(requirement.target)
            status = ConstraintStatus.PASS if numeric == float(requirement.target) else ConstraintStatus.FAIL
        else:
            return ConstraintResult(requirement_id=requirement.id, required_condition=InventionDesignEngine._condition(requirement), actual_value=value, status=ConstraintStatus.UNKNOWN, provenance=provenance, epistemic_state=requirement.epistemic_state)
        return ConstraintResult(requirement_id=requirement.id, required_condition=InventionDesignEngine._condition(requirement), actual_value=value, status=status, margin=margin, provenance=provenance, epistemic_state=requirement.epistemic_state)

    @staticmethod
    def _condition(requirement: EngineeringRequirement) -> str:
        if requirement.minimum is not None:
            return f">= {requirement.minimum} {requirement.units or ''}".strip()
        if requirement.maximum is not None:
            return f"<= {requirement.maximum} {requirement.units or ''}".strip()
        return f"= {requirement.target} {requirement.units or ''}".strip()

    def _record_requirement(self, requirement: EngineeringRequirement) -> None:
        node = self.graph.create_node(ResearchGraphNode(type=NodeType.VARIABLE, name=requirement.id, description=requirement.description, properties=requirement.model_dump(mode="json"), metadata={"phase": 7, "artifact": "engineering_requirement"}, epistemic_state=requirement.epistemic_state))
        self._requirement_nodes[requirement.id] = node.id

    @staticmethod
    def _hash(value: Any) -> str:
        return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode()).hexdigest()
