from pathlib import Path

from fastapi.testclient import TestClient

from tinkle.api.main import app
from tinkle.invention_engine import (
    FictionalFunctionTranslation,
    InventionGenerationEngine,
    InventionRequest,
)
from tinkle.reality_engine import ClaimStatus
from tinkle.research_graph import ResearchGraph, SQLiteResearchGraphStore


def test_invention_pipeline_decomposes_safe_wearable_goal_and_preserves_state(tmp_path: Path):
    graph = ResearchGraph(SQLiteResearchGraphStore(str(tmp_path / "invention.db")))
    engine = InventionGenerationEngine(graph)
    result = engine.analyze_invention_goal(InventionRequest(
        problem="Design a compact wearable system capable of providing controlled assistance to arm movement",
        constraints=["compact size", "human safety"],
    ))
    assert result.goal.primary_function
    assert result.functions and result.requirements and result.constraints
    assert result.domains and result.principles and result.mechanisms
    assert result.architectures and result.candidates and result.tradeoffs
    assert result.failures and result.feasibility and result.hypotheses
    assert result.validation and result.simulations and result.experiments
    assert result.graph_node_ids
    assert all(item.epistemic_state == ClaimStatus.UNVALIDATED for item in result.candidates)
    assert all(item.epistemic_state != ClaimStatus.KNOWN for item in result.hypotheses)


def test_unknown_constraints_and_feasibility_are_explicit():
    result = InventionGenerationEngine().analyze_invention_goal(InventionRequest(problem="Provide controlled motion"))
    assert result.constraints[0].epistemic_state == ClaimStatus.UNKNOWN
    assert result.feasibility[0].status.value == "UNCERTAIN"
    assert result.research_gaps
    assert all(item.target is None for item in result.performance_targets)


def test_fictional_function_translation_does_not_claim_fictional_technology():
    result = InventionGenerationEngine.translate_fictional_function("Rapidly launch and anchor a filament")
    assert isinstance(result, FictionalFunctionTranslation)
    assert result.fictional_capability.startswith("Rapidly")
    assert result.epistemic_state == ClaimStatus.UNVALIDATED
    assert result.limitations
    assert "measurable" in result.real_world_function


def test_research_graph_persistence_contains_invention_nodes(tmp_path: Path):
    path = str(tmp_path / "persistent.db")
    graph = ResearchGraph(SQLiteResearchGraphStore(path))
    result = InventionGenerationEngine(graph).analyze_invention_goal(InventionRequest(problem="Generate controlled motion"))
    reopened = ResearchGraph(SQLiteResearchGraphStore(path))
    nodes = [reopened.get_node(uuid) for uuid in result.graph_node_ids]
    assert len(nodes) == len(result.graph_node_ids)
    assert {node.type.value for node in nodes} >= {
        "ResearchProject", "Variable", "Principle", "Technology", "Design",
        "Failure", "Unknown", "Hypothesis", "Simulation", "Experiment",
    }
    assert all(node.metadata["invention_analysis_id"] == str(result.id) for node in nodes)


def test_invention_api_analyze_and_subresource_endpoints():
    client = TestClient(app)
    headers = {"X-API-Key": "dev-key"}
    response = client.post("/api/v1/inventions/analyze", headers=headers, json={"problem": "Design a compact wearable system for controlled arm assistance"})
    assert response.status_code == 200
    analysis_id = response.json()["id"]
    for suffix in ("requirements", "mechanisms", "concepts", "tradeoffs", "failures", "feasibility", "research-gaps", "graph"):
        item = client.get(f"/api/v1/inventions/{analysis_id}/{suffix}", headers=headers)
        assert item.status_code == 200
    assert client.get(f"/api/v1/inventions/{analysis_id}").status_code == 401


def test_invention_api_rejects_empty_goal():
    client = TestClient(app)
    response = client.post("/api/v1/inventions/analyze", headers={"X-API-Key": "dev-key"}, json={"problem": ""})
    assert response.status_code == 422
