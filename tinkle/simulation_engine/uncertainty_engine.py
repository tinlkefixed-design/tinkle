from __future__ import annotations

import itertools
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
from tinkle.simulation_engine.physics_engine import PhysicsLabEngine
from tinkle.simulation_engine.physics_schemas import MechanicsSimulationRequest, PhysicsQuantity
from tinkle.simulation_engine.uncertainty_schemas import (
    AnalysisRequest,
    OptimizationRequest,
    OptimizationResult,
    ParameterRange,
    RobustnessResult,
    SensitivityResult,
    SweepResult,
    UncertaintyAnalysisResult,
    UncertaintySpec,
)


class UncertaintyEngine:
    """Deterministic uncertainty and sensitivity analysis over the Phase 4 simulator."""

    def __init__(self, physics: PhysicsLabEngine | None = None, graph: ResearchGraph | None = None) -> None:
        self.graph = graph or (physics.graph if physics else ResearchGraph())
        self.physics = physics or PhysicsLabEngine(self.graph)

    @staticmethod
    def _validate_ranges(ranges: list[ParameterRange]) -> None:
        names: set[str] = set()
        for item in ranges:
            if item.name in names:
                raise ValueError(f"Duplicate parameter range: {item.name}")
            names.add(item.name)
            if item.epistemic_state == ClaimStatus.UNKNOWN:
                raise ValueError(f"Parameter range state is unknown: {item.name}")
            if item.lower > item.upper or not item.lower <= item.nominal <= item.upper:
                raise ValueError(f"Invalid bounds for parameter: {item.name}")

    @staticmethod
    def _quantity(request: MechanicsSimulationRequest, name: str) -> PhysicsQuantity:
        values = {"mass": request.mass, "force": request.force, "initial_velocity": request.initial_velocity, "gravity": request.gravity, "initial_position": request.initial_position}
        if name not in values:
            raise ValueError(f"Unsupported mechanics parameter: {name}")
        return values[name]

    @classmethod
    def _with_values(cls, request: MechanicsSimulationRequest, values: dict[str, float]) -> MechanicsSimulationRequest:
        updates = {
            name: current_quantity.model_copy(update={"value": value})
            for name, value in values.items()
            for current_quantity in [cls._quantity(request, name)]
        }
        return request.model_copy(update=updates)

    @staticmethod
    def _output(result, output: str) -> float:
        if not result.outputs or output not in result.outputs[-1]:
            raise ValueError(f"Unsupported or unavailable output: {output}")
        return float(result.outputs[-1][output])

    def sweep(self, request: AnalysisRequest) -> SweepResult:
        self._validate_ranges(request.ranges)
        if not request.ranges:
            raise ValueError("At least one explicit parameter range is required")
        values = [[item.lower, item.nominal, item.upper] for item in request.ranges]
        simulations = [self.physics.simulate(self._with_values(request.simulation, dict(zip([item.name for item in request.ranges], combination)))) for combination in itertools.product(*values)]
        result = SweepResult(model_id=simulations[0].model_id, simulations=simulations, evaluations=len(simulations), provenance={"method": "explicit_grid", "ranges": [item.model_dump(mode="json") for item in request.ranges]}, epistemic_state=ClaimStatus.SIMULATED)
        self._record_analysis(result.analysis_id, "Parameter sweep", result.model_id)
        return result

    def sensitivity(self, request: AnalysisRequest) -> list[SensitivityResult]:
        self._validate_ranges(request.ranges)
        baseline_values = {item.name: item.nominal for item in request.ranges}
        baseline = self.physics.simulate(self._with_values(request.simulation, baseline_values))
        baseline_output = self._output(baseline, request.output)
        results = []
        for item in request.ranges:
            changed_value = item.nominal * (1 + request.perturbation) if item.nominal else item.upper
            changed = self.physics.simulate(self._with_values(request.simulation, {item.name: changed_value}))
            changed_output = self._output(changed, request.output)
            metric = ((changed_output - baseline_output) / baseline_output) / ((changed_value - item.nominal) / item.nominal) if baseline_output and item.nominal else changed_output - baseline_output
            results.append(SensitivityResult(model_id=baseline.model_id, simulation_id=baseline.simulation_id, parameter=item.name, perturbation=request.perturbation, output_variable=request.output, baseline_output=baseline_output, changed_output=changed_output, sensitivity_metric=metric, assumptions=baseline.assumptions, provenance={"method": "normalized_local_finite_difference", "formula": "(delta Y / Y) / (delta X / X)"}))
        for rank, result in enumerate(sorted(results, key=lambda item: abs(item.sensitivity_metric), reverse=True), 1):
            result.rank = rank
        ordered = sorted(results, key=lambda item: item.rank)
        for result in ordered:
            self._record_analysis(result.analysis_id, "Sensitivity analysis", result.model_id)
        return ordered

    def uncertainty(self, request: AnalysisRequest) -> UncertaintyAnalysisResult:
        sweep = self.sweep(request)
        outputs = [self._output(result, request.output) for result in sweep.simulations]
        specs = [UncertaintySpec(parameter=item, source="caller-supplied explicit interval", magnitude=f"{item.lower}..{item.upper}", epistemic_state=item.epistemic_state, provenance=item.provenance, assumptions=item.assumptions) for item in request.ranges]
        result = UncertaintyAnalysisResult(model_id=sweep.model_id, input_parameters=request.ranges, uncertainty_specifications=specs, propagation_method="deterministic_interval_grid", output_variable=request.output, output_range={"minimum": min(outputs), "maximum": max(outputs)}, evaluations=sweep.evaluations, assumptions=["Output range is bounded by the caller-supplied intervals."], limitations=["This is computational interval propagation, not measured uncertainty or statistical confidence."], provenance=sweep.provenance)
        self._record_analysis(result.analysis_id, "Uncertainty analysis", result.model_id)
        return result

    def robustness(self, request: AnalysisRequest) -> RobustnessResult:
        uncertainty = self.uncertainty(request)
        baseline = self.physics.simulate(self._with_values(request.simulation, {item.name: item.nominal for item in request.ranges}))
        nominal = self._output(baseline, request.output)
        variation = uncertainty.output_range["maximum"] - uncertainty.output_range["minimum"]
        result = RobustnessResult(**uncertainty.model_dump(), nominal_output=nominal, variation=variation, normalized_variation=variation / abs(nominal) if nominal else None)
        self._record_analysis(result.analysis_id, "Robustness analysis", result.model_id)
        return result

    def optimize(self, request: OptimizationRequest) -> OptimizationResult:
        self._validate_ranges(request.ranges)
        names = [item.name for item in request.ranges]
        grids = [self._grid(item) for item in request.ranges]
        candidates = []
        for combination in itertools.product(*grids):
            configuration = dict(zip(names, combination))
            simulation = self.physics.simulate(self._with_values(request.simulation, configuration))
            value = self._output(simulation, "velocity")
            candidates.append({"configuration": configuration, "objective_value": value, "simulation_id": str(simulation.simulation_id), "epistemic_state": ClaimStatus.SIMULATED.value})
        if request.objective == "maximize_final_velocity":
            selected = max(candidates, key=lambda item: item["objective_value"])
        elif request.objective == "minimize_final_position":
            selected = min(candidates, key=lambda item: item["objective_value"])
        else:
            raise ValueError(f"Unsupported objective: {request.objective}")
        result = OptimizationResult(model_id=simulation.model_id, objective=request.objective, bounds=request.ranges, candidates=candidates, selected_configuration=selected["configuration"], objective_value=selected["objective_value"], constraints=request.constraints, evaluations=len(candidates), assumptions=["Only the explicitly supplied grid was evaluated."], limitations=["Best configuration found within the evaluated grid; no global optimum or experimental optimality is claimed."], provenance={"method": "deterministic_grid_search", "objective": request.objective})
        self._record_analysis(result.optimization_id, "Optimization", result.model_id)
        return result

    def _record_analysis(self, analysis_id: UUID, name: str, model_id: UUID) -> None:
        analysis_node = self.graph.create_node(ResearchGraphNode(type=NodeType.RESULT, name=f"{name} {analysis_id}", description=name, metadata={"analysis_id": str(analysis_id), "model_id": str(model_id)}, epistemic_state=ClaimStatus.SIMULATED, provenance=GraphProvenance(notes="Computational analysis result")))
        model_matches = self.graph.search_graph(__import__('tinkle.research_graph', fromlist=['GraphSearchRequest']).GraphSearchRequest(query=str(model_id), node_type=NodeType.MODEL))
        if model_matches:
            self.graph.create_edge(EdgeCreate(source_id=model_matches[0].id, target_id=analysis_node.id, relationship=RelationshipType.DERIVED_FROM, epistemic_state=ClaimStatus.SIMULATED))

    @staticmethod
    def _grid(item: ParameterRange) -> list[float]:
        if item.lower == item.upper:
            return [item.lower]
        step = (item.upper - item.lower) / 2
        return [item.lower, item.lower + step, item.upper]
