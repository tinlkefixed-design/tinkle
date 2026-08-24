from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from tinkle.api.main import app
from tinkle.reality_engine import ClaimStatus
from tinkle.research_graph import ResearchGraph, SQLiteResearchGraphStore
from tinkle.simulation_engine import (
    MechanicsSimulationRequest,
    PhysicsLabEngine,
    PhysicsQuantity,
)


def quantity(value, unit, state=ClaimStatus.ASSUMED, provenance=None):
    return PhysicsQuantity(value=value, unit=unit, epistemic_state=state, provenance=provenance)


def test_newtonian_motion_and_reproducibility(tmp_path: Path):
    engine = PhysicsLabEngine(ResearchGraph(SQLiteResearchGraphStore(str(tmp_path / "a.db"))))
    request = MechanicsSimulationRequest(mass=quantity(2, "kg"), force=quantity(10, "N"), gravity=quantity(0, "m/s^2"), steps=2, timestep=0.5)
    first = engine.simulate(request)
    second = engine.simulate(request)
    assert first.outputs[-1]["velocity"] == pytest.approx(5)
    assert first.outputs == second.outputs
    assert first.epistemic_state == ClaimStatus.SIMULATED
    assert first.solver == "deterministic_euler"


def test_energy_momentum_and_spring_equations():
    engine = PhysicsLabEngine(ResearchGraph(SQLiteResearchGraphStore(":memory:")))
    mass = quantity(2, "kg")
    velocity = quantity(3, "m/s")
    gravity = quantity(10, "m/s^2", ClaimStatus.SOURCE_BACKED, "standard approximation")
    height = quantity(4, "m")
    assert engine.kinetic_energy(mass, velocity).value == pytest.approx(9)
    assert engine.potential_energy(mass, gravity, height).value == pytest.approx(80)
    assert engine.momentum(mass, velocity).value == pytest.approx(6)
    assert engine.spring_force(quantity(100, "N/m"), quantity(0.2, "m")).value == pytest.approx(-20)


def test_unknown_required_input_is_rejected_without_defaulting(tmp_path: Path):
    engine = PhysicsLabEngine(ResearchGraph(SQLiteResearchGraphStore(str(tmp_path / "unknown.db"))))
    request = MechanicsSimulationRequest(mass=quantity(None, "kg", ClaimStatus.UNKNOWN), force=quantity(1, "N"))
    with pytest.raises(ValueError, match="mass"):
        engine.simulate(request)


def test_input_states_and_provenance_survive_simulation(tmp_path: Path):
    engine = PhysicsLabEngine(ResearchGraph(SQLiteResearchGraphStore(str(tmp_path / "state.db"))))
    result = engine.simulate(MechanicsSimulationRequest(
        mass=quantity(2, "kg", ClaimStatus.ASSUMED, "design assumption"),
        force=quantity(10, "N", ClaimStatus.SOURCE_BACKED, "force specification"),
        gravity=quantity(0, "m/s^2", ClaimStatus.ASSUMED),
        steps=1,
    ))
    assert result.inputs["mass"].epistemic_state == ClaimStatus.ASSUMED
    assert result.inputs["force"].epistemic_state == ClaimStatus.SOURCE_BACKED
    assert result.epistemic_state == ClaimStatus.SIMULATED
    assert result.provenance["input_hash"]
    assert "not a real-world measurement" in result.limitations[-1]


def test_research_graph_contains_model_simulation_inputs_and_result(tmp_path: Path):
    graph = ResearchGraph(SQLiteResearchGraphStore(str(tmp_path / "graph.db")))
    engine = PhysicsLabEngine(graph)
    result = engine.simulate(MechanicsSimulationRequest(mass=quantity(1, "kg"), force=quantity(2, "N"), gravity=quantity(0, "m/s^2")))
    simulation_nodes = graph.search_graph(__import__('tinkle.research_graph', fromlist=['GraphSearchRequest']).GraphSearchRequest(query=str(result.simulation_id)))
    assert {node.type.value for node in simulation_nodes} >= {"Simulation", "Result"}
    assert all(node.epistemic_state == ClaimStatus.SIMULATED for node in simulation_nodes)


def test_mechanics_api_requires_auth_and_runs():
    client = TestClient(app)
    payload = {"mass": {"value": 2, "unit": "kg", "epistemic_state": "ASSUMED"}, "force": {"value": 10, "unit": "N", "epistemic_state": "ASSUMED"}, "gravity": {"value": 0, "unit": "m/s^2", "epistemic_state": "ASSUMED"}, "steps": 1, "timestep": 0.5}
    response = client.post('/api/v1/simulation/mechanics/run', headers={'X-API-Key': 'dev-key'}, json=payload)
    assert response.status_code == 200
    assert response.json()['epistemic_state'] == 'SIMULATED'
    assert client.post('/api/v1/simulation/mechanics/run', json=payload).status_code == 401


def test_mechanics_api_rejects_unknown_mass():
    client = TestClient(app)
    payload = {"mass": {"unit": "kg", "epistemic_state": "UNKNOWN"}, "force": {"value": 10, "unit": "N"}}
    response = client.post('/api/v1/simulation/mechanics/run', headers={'X-API-Key': 'dev-key'}, json=payload)
    assert response.status_code == 422
