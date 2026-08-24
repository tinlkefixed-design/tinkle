from __future__ import annotations

import hashlib
import json
import math
from datetime import UTC, datetime
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
from tinkle.simulation_engine.physics_schemas import (
    MechanicsSimulationRequest,
    MechanicsSimulationResult,
    PhysicsCalculation,
    PhysicsQuantity,
    ScientificModel,
)


class PhysicsLabEngine:
    """Bounded mechanics calculations and constant-force Euler simulations."""

    def __init__(self, graph: ResearchGraph | None = None) -> None:
        self.graph = graph or ResearchGraph()
        self.models: dict[UUID, ScientificModel] = {}
        self.results: dict[UUID, MechanicsSimulationResult] = {}

    def register_model(self, model: ScientificModel) -> ScientificModel:
        self.models[model.id] = model
        return model

    def get_model(self, model_id: UUID) -> ScientificModel:
        try:
            return self.models[model_id]
        except KeyError as exc:
            raise KeyError(f"Scientific model not found: {model_id}") from exc

    @staticmethod
    def _value(quantity: PhysicsQuantity, name: str) -> float:
        if quantity.value is None or quantity.epistemic_state == ClaimStatus.UNKNOWN:
            raise ValueError(f"Required input is unknown: {name}")
        if not math.isfinite(float(quantity.value)):
            raise ValueError(f"Required input must be finite: {name}")
        return float(quantity.value)

    @staticmethod
    def kinetic_energy(mass: PhysicsQuantity, velocity: PhysicsQuantity) -> PhysicsCalculation:
        m, v = PhysicsLabEngine._value(mass, "mass"), PhysicsLabEngine._value(velocity, "velocity")
        return PhysicsCalculation(quantity="kinetic_energy", value=0.5 * m * v**2, unit="J", equation="KE = 1/2 m v^2", inputs={"mass": mass, "velocity": velocity})

    @staticmethod
    def potential_energy(mass: PhysicsQuantity, gravity: PhysicsQuantity, height: PhysicsQuantity) -> PhysicsCalculation:
        m = PhysicsLabEngine._value(mass, "mass")
        g = PhysicsLabEngine._value(gravity, "gravity")
        h = PhysicsLabEngine._value(height, "height")
        return PhysicsCalculation(quantity="potential_energy", value=m * g * h, unit="J", equation="PE = m g h", inputs={"mass": mass, "gravity": gravity, "height": height})

    @staticmethod
    def momentum(mass: PhysicsQuantity, velocity: PhysicsQuantity) -> PhysicsCalculation:
        m, v = PhysicsLabEngine._value(mass, "mass"), PhysicsLabEngine._value(velocity, "velocity")
        return PhysicsCalculation(quantity="momentum", value=m * v, unit="kg m/s", equation="p = m v", inputs={"mass": mass, "velocity": velocity})

    @staticmethod
    def spring_force(spring_constant: PhysicsQuantity, displacement: PhysicsQuantity) -> PhysicsCalculation:
        k = PhysicsLabEngine._value(spring_constant, "spring_constant")
        x = PhysicsLabEngine._value(displacement, "spring_displacement")
        return PhysicsCalculation(quantity="spring_force", value=-k * x, unit="N", equation="F = -k x", inputs={"spring_constant": spring_constant, "displacement": displacement})

    def simulate(self, request: MechanicsSimulationRequest) -> MechanicsSimulationResult:
        model = request.model or (self.get_model(request.model_id) if request.model_id else None)
        if model is None:
            model = ScientificModel(name="constant-force Newtonian mechanics", description="One-dimensional constant-force motion with explicit Euler integration.", equations=["F = m a", "v_next = v + a dt", "x_next = x + v dt"], variables=["position", "velocity", "acceleration"], parameters=["mass", "force", "timestep"], assumptions=["One-dimensional motion", "Constant net force", "Non-relativistic regime"], limitations=["Explicit Euler is timestep-dependent and can be unstable.", "This is not a rigid-body, CFD, FEM, or electromagnetic solver."], epistemic_state=ClaimStatus.SOURCE_BACKED)
        self.register_model(model)
        mass = self._value(request.mass, "mass")
        force = self._value(request.force, "force")
        position = self._value(request.initial_position, "initial_position")
        velocity = self._value(request.initial_velocity, "initial_velocity")
        gravity = self._value(request.gravity, "gravity")
        if mass <= 0:
            raise ValueError("mass must be positive")
        acceleration = force / mass
        if "gravity" in request.requested_outputs:
            acceleration -= gravity
        rows: list[dict[str, float]] = []
        for step in range(request.steps + 1):
            if not all(math.isfinite(value) for value in (position, velocity, acceleration)):
                raise ValueError("simulation diverged to a non-finite state")
            rows.append({"step": float(step), "time": step * request.timestep, "position": position, "velocity": velocity, "acceleration": acceleration})
            velocity += acceleration * request.timestep
            position += velocity * request.timestep
        simulation_id = UUID(bytes=hashlib.sha256(json.dumps(request.model_dump(mode="json"), sort_keys=True).encode()).digest()[:16])
        result = MechanicsSimulationResult(simulation_id=simulation_id, model_id=model.id, inputs={"mass": request.mass, "force": request.force, "initial_position": request.initial_position, "initial_velocity": request.initial_velocity}, parameters={"timestep": PhysicsQuantity(value=request.timestep, unit="s", epistemic_state=ClaimStatus.ASSUMED), "gravity": request.gravity}, outputs=rows, execution_metadata={"steps": request.steps, "deterministic": True, "generated_at": datetime.now(UTC).isoformat()}, assumptions=model.assumptions + request.assumptions, limitations=model.limitations + ["Simulation output is not a real-world measurement."], provenance={"engine": "PhysicsLabEngine", "model_id": str(model.id), "input_hash": hashlib.sha256(json.dumps(request.model_dump(mode="json"), sort_keys=True).encode()).hexdigest()}, epistemic_state=ClaimStatus.SIMULATED)
        self.results[result.simulation_id] = result
        self._graph_result(model, request, result)
        return result

    def _graph_result(self, model: ScientificModel, request: MechanicsSimulationRequest, result: MechanicsSimulationResult) -> None:
        model_node = self.graph.create_node(ResearchGraphNode(type=NodeType.MODEL, name=model.name, description=model.description, properties={"equations": model.equations}, epistemic_state=model.epistemic_state, metadata={"physics_model_id": str(model.id)}))
        simulation_node = self.graph.create_node(ResearchGraphNode(type=NodeType.SIMULATION, name=f"Simulation {result.simulation_id}", description="Deterministic constant-force mechanics simulation.", properties={"solver": result.solver, "numerical_method": result.numerical_method, "outputs": result.outputs}, epistemic_state=ClaimStatus.SIMULATED, metadata={"simulation_id": str(result.simulation_id)}, provenance=GraphProvenance(notes="Generated by PhysicsLabEngine")))
        self.graph.create_edge(EdgeCreate(source_id=model_node.id, target_id=simulation_node.id, relationship=RelationshipType.SIMULATES, epistemic_state=ClaimStatus.SIMULATED))
        for name, quantity in {"mass": request.mass, "force": request.force}.items():
            input_node = self.graph.create_node(ResearchGraphNode(type=NodeType.PARAMETER, name=name, properties={"value": quantity.value, "unit": quantity.unit}, epistemic_state=quantity.epistemic_state))
            self.graph.create_edge(EdgeCreate(source_id=simulation_node.id, target_id=input_node.id, relationship=RelationshipType.REQUIRES, epistemic_state=quantity.epistemic_state))
        result_node = self.graph.create_node(ResearchGraphNode(type=NodeType.RESULT, name=f"Result {result.simulation_id}", properties={"outputs": result.outputs}, epistemic_state=ClaimStatus.SIMULATED, metadata={"simulation_id": str(result.simulation_id)}, provenance=GraphProvenance(notes="Simulation result; not a measurement")))
        self.graph.create_edge(EdgeCreate(source_id=simulation_node.id, target_id=result_node.id, relationship=RelationshipType.PRODUCES, epistemic_state=ClaimStatus.SIMULATED))

    def get_result(self, simulation_id: UUID) -> MechanicsSimulationResult:
        try:
            return self.results[simulation_id]
        except KeyError as exc:
            raise KeyError(f"Simulation result not found: {simulation_id}") from exc

    def trace_graph(self, simulation_id: UUID) -> list[ResearchGraphNode]:
        result = self.get_result(simulation_id)
        return self.graph.ancestors(UUID(self._find_simulation_node(result)))

    def _find_simulation_node(self, result: MechanicsSimulationResult) -> str:
        matches = self.graph.search_graph(__import__('tinkle.research_graph', fromlist=['GraphSearchRequest']).GraphSearchRequest(query=str(result.simulation_id), node_type=NodeType.SIMULATION))
        if not matches:
            raise KeyError(f"Simulation graph node not found: {result.simulation_id}")
        return str(matches[0].id)
