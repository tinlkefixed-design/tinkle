from __future__ import annotations

import hashlib
import json
from typing import Any
from uuid import UUID

from tinkle.engineering_decision import EngineeringDecisionEngine
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
from tinkle.validation import ValidationEngine

from .schemas import (
    ExpectedOutcome,
    ExperimentalCondition,
    ExperimentalVariable,
    ExperimentObjective,
    ExperimentPlan,
    ExperimentPlanRequest,
    ExperimentResultReference,
    MeasurementSpecification,
    PlanComparison,
    PlanInvalidation,
    PlanningState,
    PlanStatus,
    Prediction,
    ReproducibilityManifest,
    ResearchObjective,
)


class ExperimentPlanningEngine:
    """Planning-only orchestration over research, decisions, and validation state."""

    def __init__(self, decisions: EngineeringDecisionEngine | None = None, validation: ValidationEngine | None = None, graph: ResearchGraph | None = None) -> None:
        self.decisions = decisions or EngineeringDecisionEngine(graph=graph)
        self.validation = validation or ValidationEngine(decisions=self.decisions, graph=graph)
        self.graph = graph or self.decisions.graph
        self.state = PlanningState()
        self._plan_nodes: dict[UUID, UUID] = {}

    def create_research_objective(self, objective: ResearchObjective) -> ResearchObjective:
        self._unique(self.state.research_objectives, objective.id, "research objective")
        self.state.research_objectives[objective.id] = objective
        self.graph.create_node(ResearchGraphNode(type=NodeType.RESEARCH_PROJECT, name=str(objective.id), description=objective.description, properties=objective.model_dump(mode="json"), metadata={"phase": 10, "artifact": "research_objective"}, epistemic_state=objective.epistemic_state))
        return objective

    def create_experiment_objective(self, objective: ExperimentObjective) -> ExperimentObjective:
        self._unique(self.state.experiment_objectives, objective.id, "experiment objective")
        if objective.research_objective_id not in self.state.research_objectives:
            raise ValueError("Unknown research objective")
        if objective.decision_id is not None:
            decision = self._decision(objective.decision_id)
            if any(item not in [option.candidate_id for option in decision.options] for item in objective.candidate_ids):
                raise ValueError("Unknown decision candidate")
        missing_validation = [item for item in objective.validation_requirement_ids if item not in self.validation.requirements]
        if missing_validation:
            raise ValueError(f"Unknown validation requirement: {', '.join(missing_validation)}")
        self.state.experiment_objectives[objective.id] = objective
        return objective

    def register_variable(self, variable: ExperimentalVariable) -> ExperimentalVariable:
        self._unique(self.state.variables, variable.id, "variable")
        if variable.allowed_minimum is not None and variable.allowed_maximum is not None and variable.allowed_minimum > variable.allowed_maximum:
            raise ValueError("Variable minimum cannot exceed maximum")
        self.state.variables[variable.id] = variable
        return variable

    def register_measurement(self, measurement: MeasurementSpecification) -> MeasurementSpecification:
        self._unique(self.state.measurements, measurement.id, "measurement")
        if measurement.variable_id not in self.state.variables:
            raise ValueError("Unknown measurement variable")
        self.state.measurements[measurement.id] = measurement
        return measurement

    def register_condition(self, condition: ExperimentalCondition) -> ExperimentalCondition:
        self._unique(self.state.conditions, condition.id, "condition")
        for low, high in condition.parameter_ranges.values():
            if low > high:
                raise ValueError("Condition range minimum cannot exceed maximum")
        self.state.conditions[condition.id] = condition
        return condition

    def register_prediction(self, prediction: Prediction) -> Prediction:
        self._unique(self.state.predictions, prediction.id, "prediction")
        self.state.predictions[prediction.id] = prediction
        return prediction

    def create_plan(self, request: ExperimentPlanRequest) -> ExperimentPlan:
        objective = self._get(self.state.research_objectives, request.research_objective_id, "research objective")
        experiment_objective = self._get(self.state.experiment_objectives, request.experiment_objective_id, "experiment objective")
        if experiment_objective.research_objective_id != objective.id:
            raise ValueError("Experiment objective does not belong to research objective")
        variables = [self._get(self.state.variables, item, "variable") for item in sorted(request.variable_ids)]
        measurements = [self._get(self.state.measurements, item, "measurement") for item in sorted(request.measurement_ids)]
        conditions = [self._get(self.state.conditions, item, "condition") for item in sorted(request.condition_ids)]
        predictions = [self._get(self.state.predictions, item, "prediction") for item in sorted(request.prediction_ids)]
        for candidate_id in request.candidate_ids:
            self._candidate(candidate_id)
        if request.decision_id is not None:
            decision = self._decision(request.decision_id)
            if request.candidate_ids and any(item not in [option.candidate_id for option in decision.options] for item in request.candidate_ids):
                raise ValueError("Plan candidates do not match decision options")
        if request.validation_requirement_ids:
            missing_validation = [item for item in request.validation_requirement_ids if item not in self.validation.requirements]
            if missing_validation:
                raise ValueError(f"Unknown validation requirement: {', '.join(missing_validation)}")
        missing = self._missing(variables, measurements, request)
        safety_review = self._safety_review(request, conditions)
        status = PlanStatus.BLOCKED if missing or safety_review else PlanStatus.READY
        expected = self._expected_outcomes(predictions, experiment_objective.hypothesis_ids)
        info_value = self._information_value(objective, experiment_objective, variables, measurements, request, missing)
        limitations = list(request.limitations) + ["Estimated information value is a bounded planning estimate, not guaranteed information gain.", "This plan does not execute physical experiments or create measurements."]
        assumptions = sorted(set(objective.assumptions + request.assumptions + [item for condition in conditions for item in condition.assumptions]))
        manifest_data = {"research_objective_id": str(objective.id), "experiment_objective_id": str(experiment_objective.id), "variables": [item.model_dump(mode="json") for item in variables], "measurements": [item.model_dump(mode="json") for item in measurements], "conditions": [item.model_dump(mode="json") for item in conditions], "predictions": [item.model_dump(mode="json", exclude={"id"}) for item in predictions], "candidates": sorted(str(item) for item in request.candidate_ids), "decision_id": str(request.decision_id) if request.decision_id else None, "validation_requirement_ids": sorted(request.validation_requirement_ids), "assumptions": assumptions, "limitations": sorted(request.limitations), "cost": request.estimated_cost, "complexity": request.estimated_complexity}
        canonical_hash = self._hash(manifest_data)
        manifest = ReproducibilityManifest(input_ids=sorted([str(objective.id), str(experiment_objective.id)] + request.variable_ids + request.measurement_ids + request.condition_ids + [str(item) for item in request.prediction_ids]), hypothesis_ids=sorted(experiment_objective.hypothesis_ids), candidate_ids=sorted(request.candidate_ids, key=str), criteria={"uncertainty_reduction": 0.35, "hypothesis_discrimination": 0.30, "validation_relevance": 0.20, "decision_relevance": 0.15}, variables=variables, measurements=measurements, uncertainty_configuration={"priority_basis": "current model/sensitivity information", "references": sorted(objective.source_refs)}, simulation_refs=sorted({item.simulation_ref for item in predictions if item.simulation_ref}), evidence_refs=sorted(objective.source_refs), assumptions=assumptions, limitations=limitations, canonical_hash=canonical_hash)
        plan = ExperimentPlan(research_objective_id=objective.id, objective=experiment_objective, hypothesis_ids=sorted(experiment_objective.hypothesis_ids), candidate_ids=sorted(request.candidate_ids, key=str), decision_id=request.decision_id, validation_requirement_ids=sorted(request.validation_requirement_ids), variables=variables, controls=list(request.controls), conditions=conditions, measurements=measurements, predictions=predictions, expected_outcomes=expected, acceptance_criteria=self._acceptance(measurements, predictions), required_evidence=["External measured evidence" if measurements else "Declared evidence requirement"], prerequisites=sorted(set(request.prerequisites + (["REQUIRES_HUMAN_REVIEW"] if safety_review else []))), risks=list(request.risks), assumptions=assumptions, limitations=limitations, estimated_information_value=info_value, estimated_cost=request.estimated_cost, estimated_complexity=request.estimated_complexity, reproducibility_manifest=manifest, provenance=experiment_objective.provenance.model_copy(update={"method": "experiment_planning_v1", "input_hash": canonical_hash, "analysis_refs": sorted(objective.source_refs)}), deterministic_hash=canonical_hash, status=status, human_review_required=True)
        self.state.plans[plan.id] = plan
        self.state.history[plan.id] = [{"event": "PLAN_CREATED", "status": status.value}]
        self._graph_plan(plan)
        return plan

    def validate_plan(self, plan_id: UUID) -> dict[str, Any]:
        plan = self.get_plan(plan_id)
        missing = self._missing(plan.variables, plan.measurements, ExperimentPlanRequest(research_objective_id=plan.research_objective_id, experiment_objective_id=plan.objective.id, validation_requirement_ids=plan.validation_requirement_ids, prerequisites=plan.prerequisites, risks=plan.risks, assumptions=plan.assumptions, limitations=plan.limitations))
        if plan.status != PlanStatus.INVALIDATED:
            plan.status = PlanStatus.BLOCKED if missing else PlanStatus.READY
        result = {"plan_id": str(plan_id), "status": plan.status.value, "missing_data": missing, "execution_allowed": False}
        self.state.history[plan_id].append({"event": "PLAN_VALIDATED", "status": plan.status.value, "missing_data": missing})
        return result

    def compare(self, plan_ids: list[UUID]) -> PlanComparison:
        plans = [self.get_plan(item) for item in plan_ids]
        missing: dict[str, list[str]] = {str(plan.id): ["blocked plan"] for plan in plans if plan.status == PlanStatus.BLOCKED}
        scores = {str(plan.id): plan.estimated_information_value for plan in plans if str(plan.id) not in missing}
        if missing:
            return PlanComparison(status="REQUIRES_DATA", missing_data=missing, rationale=["Blocked plans cannot outrank ready plans."])
        ranked = sorted(scores, key=lambda item: (-scores[item], item))
        return PlanComparison(status="RANKED", ranked_plan_ids=[UUID(item) for item in ranked], scores=scores, rationale=["Sorted by bounded estimated information value, then UUID."])

    def register_result(self, result: ExperimentResultReference) -> ExperimentResultReference:
        plan = self.get_plan(result.experiment_plan_id)
        if result.epistemic_state not in {ClaimStatus.MEASURED, ClaimStatus.SOURCE_BACKED}:
            raise ValueError("External result reference requires measured or source-backed state")
        self._validate_evidence(result.evidence_ids)
        self.state.results[result.id] = result
        plan.status = PlanStatus.EXECUTED_EXTERNALLY
        self.state.history[plan.id].append({"event": "EXTERNAL_RESULT_REFERENCED", "result_id": str(result.id)})
        return result

    def invalidate(self, request: PlanInvalidation) -> ExperimentPlan:
        plan = self.get_plan(request.plan_id)
        plan.status = PlanStatus.INVALIDATED
        self.state.history[plan.id].append({"event": "PLAN_INVALIDATED", "reason": request.reason, "evidence_refs": sorted(request.evidence_refs)})
        return plan

    def get_plan(self, plan_id: UUID) -> ExperimentPlan:
        return self._get(self.state.plans, plan_id, "experiment plan")

    def history(self, plan_id: UUID) -> list[dict[str, Any]]:
        self.get_plan(plan_id)
        return list(self.state.history[plan_id])

    def missing_data(self, plan_id: UUID) -> list[str]:
        self.get_plan(plan_id)
        return self.validate_plan(plan_id)["missing_data"]

    def recommend(self, plan_ids: list[UUID]) -> PlanComparison:
        return self.compare(plan_ids)

    def _decision(self, decision_id: UUID):
        try:
            return self.decisions.decisions[decision_id]
        except KeyError as exc:
            raise ValueError(f"Unknown decision: {decision_id}") from exc

    def _candidate(self, candidate_id: UUID) -> None:
        if candidate_id not in self.decisions.invention.state.candidates:
            raise ValueError(f"Unknown candidate: {candidate_id}")

    def _validate_evidence(self, refs: list[str]) -> None:
        missing = [item for item in refs if item not in self.decisions.evidence]
        if missing:
            raise ValueError(f"Unknown evidence: {', '.join(missing)}")

    @staticmethod
    def _unique(mapping: dict, key: Any, label: str) -> None:
        if key in mapping:
            raise ValueError(f"{label.capitalize()} already exists: {key}")

    @staticmethod
    def _get(mapping: dict, key: Any, label: str):
        try:
            return mapping[key]
        except KeyError as exc:
            raise ValueError(f"Unknown {label}: {key}") from exc

    @staticmethod
    def _missing(variables: list[ExperimentalVariable], measurements: list[MeasurementSpecification], request: ExperimentPlanRequest) -> list[str]:
        missing = []
        if not variables:
            missing.append("variables")
        if not measurements:
            missing.append("measurements")
        if any(item.measurement_method is None for item in measurements):
            missing.append("measurement_method")
        if any(item.units is None for item in measurements):
            missing.append("measurement_units")
        if request.decision_id is not None and not request.validation_requirement_ids:
            missing.append("validation_requirement")
        return sorted(set(missing))

    @staticmethod
    def _safety_review(request: ExperimentPlanRequest, conditions: list[ExperimentalCondition]) -> bool:
        text = " ".join(request.risks + request.prerequisites + [item for condition in conditions for item in condition.constraints]).casefold()
        return any(word in text for word in ("hazard", "danger", "human", "high-risk", "safety")) and "REQUIRES_HUMAN_REVIEW" not in request.prerequisites

    @staticmethod
    def _expected_outcomes(predictions: list[Prediction], hypotheses: list[str]) -> list[ExpectedOutcome]:
        return [ExpectedOutcome(expected_observation=f"Observe {prediction.expected_value}", expected_minimum=prediction.expected_minimum, expected_maximum=prediction.expected_maximum, competing_outcome="Intermediate result may be ambiguous.", interpretation="Compare observation with prediction; do not promote it to validation.", hypothesis_id=hypotheses[index] if index < len(hypotheses) else None, epistemic_state=ClaimStatus.SIMULATED) for index, prediction in enumerate(predictions)]

    @staticmethod
    def _acceptance(measurements: list[MeasurementSpecification], predictions: list[Prediction]) -> list[str]:
        return [f"Record {item.id} using {item.measurement_method or 'an explicitly declared method'}" for item in measurements] + [f"Compare result with prediction {item.id} without converting prediction to observation" for item in predictions]

    @staticmethod
    def _information_value(objective: ResearchObjective, experiment: ExperimentObjective, variables: list[ExperimentalVariable], measurements: list[MeasurementSpecification], request: ExperimentPlanRequest, missing: list[str]) -> float:
        uncertainty = min(1.0, sum(1 for item in variables if item.uncertainty) / max(1, len(variables)))
        discrimination = 1.0 if len(experiment.hypothesis_ids) > 1 else 0.5 if experiment.hypothesis_ids else 0.0
        validation = 1.0 if request.validation_requirement_ids else 0.0
        decision = 1.0 if request.decision_id else 0.0
        burden = min(1.0, (len(missing) + len(request.prerequisites)) / 10)
        return round(max(0.0, min(1.0, 0.35 * uncertainty + 0.30 * discrimination + 0.20 * validation + 0.15 * decision - 0.10 * burden)), 6)

    @staticmethod
    def _hash(value: Any) -> str:
        return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()

    def _graph_plan(self, plan: ExperimentPlan) -> None:
        node_id = self._plan_nodes.get(plan.id)
        if node_id is None:
            node = self.graph.create_node(ResearchGraphNode(type=NodeType.EXPERIMENT, name=f"Plan {plan.id}", description=plan.objective.description, properties={"plan_id": str(plan.id), "hash": plan.deterministic_hash}, metadata={"phase": 10, "artifact": "experiment_plan"}, epistemic_state=ClaimStatus.INFERRED, provenance=GraphProvenance(notes="Phase 10 planning artifact")))
            node_id = node.id
            self._plan_nodes[plan.id] = node_id
        for ref, relationship in [(str(plan.research_objective_id), RelationshipType.PLANS_EXPERIMENT), *[(str(item), RelationshipType.TARGETS_HYPOTHESIS) for item in plan.hypothesis_ids]]:
            source = self.graph.search_graph(__import__("tinkle.research_graph", fromlist=["GraphSearchRequest"]).GraphSearchRequest(query=ref))
            if source:
                try:
                    self._edge(source[0].id, node_id, relationship, ClaimStatus.INFERRED)
                except DuplicateGraphError:
                    pass

    def _edge(self, source: UUID, target: UUID, relationship: RelationshipType, state: ClaimStatus) -> None:
        if source == target:
            return
        try:
            self.graph.create_edge(EdgeCreate(source_id=source, target_id=target, relationship=relationship, epistemic_state=state, provenance=GraphProvenance(notes="Phase 10 planning trace")))
        except DuplicateGraphError:
            pass
