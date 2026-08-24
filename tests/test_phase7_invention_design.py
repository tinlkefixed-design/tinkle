from fastapi.testclient import TestClient

from tinkle.api.main import app
from tinkle.invention_design import (
    CandidateLifecycle,
    DesignCandidate,
    DesignParameter,
    EngineeringRequirement,
    EvaluationRequest,
    InventionDesignEngine,
    ProvenanceBundle,
)
from tinkle.reality_engine import ClaimStatus
from tinkle.research_graph import NodeType, RelationshipType
from tinkle.simulation_engine import MechanicsSimulationRequest, ParameterRange, PhysicsQuantity


def requirement(identifier, **updates):
    return EngineeringRequirement(id=identifier, description=identifier, epistemic_state=ClaimStatus.SOURCE_BACKED, **updates)


def candidate(*ids):
    return DesignCandidate(name="candidate", description="test candidate", requirement_ids=list(ids), parameters=[DesignParameter(name="mass", value=None, unit="kg", provenance=ProvenanceBundle(originating_artifact="measurement-1"))])


def test_requirement_and_candidate_creation_preserve_unknowns():
    engine = InventionDesignEngine()
    engine.create_requirement(EngineeringRequirement(id="unknown", description="not supplied"))
    created = engine.create_candidate(candidate("unknown"))
    assert created.lifecycle == CandidateLifecycle.PROPOSED
    evaluation = engine.evaluate(created.id, EvaluationRequest())
    assert evaluation.unknown_constraints == ["unknown"]
    assert created.lifecycle == CandidateLifecycle.REQUIRES_DATA
    assert created.parameters[0].provenance.originating_artifact == "measurement-1"


def test_constraint_pass_fail_and_unknown_are_deterministic():
    engine = InventionDesignEngine()
    engine.create_requirement(requirement("minimum", minimum=5))
    engine.create_requirement(requirement("maximum", maximum=5))
    engine.create_requirement(EngineeringRequirement(id="unknown", description="unknown"))
    item = engine.create_candidate(candidate("minimum", "maximum", "unknown"))
    result = engine.evaluate(item.id, EvaluationRequest(actual_values={"minimum": 6, "maximum": 6}))
    assert [item.status.value for item in result.constraints] == ["PASS", "FAIL", "UNKNOWN"]
    assert result.passed_constraints == ["minimum"]
    assert result.failed_constraints == ["maximum"]


def test_simulation_uncertainty_sensitivity_and_graph_provenance():
    engine = InventionDesignEngine()
    engine.create_requirement(requirement("velocity", minimum=0))
    item = engine.create_candidate(candidate("velocity"))
    simulation = MechanicsSimulationRequest(mass=PhysicsQuantity(value=1, unit="kg", epistemic_state=ClaimStatus.ASSUMED), force=PhysicsQuantity(value=10, unit="N", epistemic_state=ClaimStatus.ASSUMED), gravity=PhysicsQuantity(value=0, unit="m/s^2", epistemic_state=ClaimStatus.SOURCE_BACKED), steps=1)
    result = engine.evaluate(item.id, EvaluationRequest(simulation=simulation, ranges=[ParameterRange(name="force", nominal=10, lower=9, upper=11, unit="N", epistemic_state=ClaimStatus.ASSUMED)]))
    assert result.simulation_refs and result.uncertainty_refs and result.sensitivity_refs
    assert result.provenance.input_hash and result.epistemic_state == ClaimStatus.SIMULATED
    nodes = engine.graph.search_graph(__import__("tinkle.research_graph", fromlist=["GraphSearchRequest"]).GraphSearchRequest(query="velocity", node_type=NodeType.VARIABLE))
    assert nodes and any(edge.relationship == RelationshipType.CONSTRAINED_BY for edge in engine.graph.get_edges())


def test_comparison_requires_data_then_ranks_deterministically():
    engine = InventionDesignEngine()
    engine.create_requirement(requirement("r", minimum=1))
    first = engine.create_candidate(candidate("r"))
    second = engine.create_candidate(candidate("r"))
    assert engine.compare([first.id, second.id]).status == "REQUIRES_DATA"
    engine.evaluate(first.id, EvaluationRequest(actual_values={"r": 1}, objective_score=2))
    engine.evaluate(second.id, EvaluationRequest(actual_values={"r": 2}, objective_score=2))
    result = engine.compare([second.id, first.id])
    assert result.status == "RANKED"
    assert result.ranked_candidate_ids == sorted([first.id, second.id], key=str)


def test_authenticated_api_behavior():
    client = TestClient(app)
    assert client.post("/api/v1/invention/requirements", json={"id": "api-r", "description": "x"}).status_code == 401
    response = client.post("/api/v1/invention/requirements", headers={"X-API-Key": "dev-key"}, json={"id": "api-r", "description": "x"})
    assert response.status_code == 200
    assert response.json()["epistemic_state"] == "UNKNOWN"
