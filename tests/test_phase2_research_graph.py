from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from tinkle.api.main import app
from tinkle.reality_engine import ClaimStatus
from tinkle.research_graph import (
    DuplicateGraphError,
    EdgeCreate,
    GraphPathRequest,
    GraphProvenance,
    GraphSearchRequest,
    InvalidGraphError,
    KnowledgeGapRequest,
    NodeType,
    NodeUpdate,
    RelationshipType,
    ResearchGraph,
    ResearchGraphNode,
    SQLiteResearchGraphStore,
)


@pytest.fixture
def graph(tmp_path):
    return ResearchGraph(SQLiteResearchGraphStore(str(tmp_path / "graph.db")))


def node(node_type=NodeType.CONCEPT, name="node", **kwargs):
    return ResearchGraphNode(type=node_type, name=name, **kwargs)


def test_node_crud_and_duplicate_protection(graph):
    original = graph.create_node(node(name="force"))
    assert graph.get_node(original.id).name == "force"
    updated = graph.update_node(original.id, NodeUpdate(name="updated", description="changed"))
    assert updated.name == "updated"
    with pytest.raises(DuplicateGraphError):
        graph.create_node(original)
    graph.delete_node(original.id)
    with pytest.raises(KeyError):
        graph.get_node(original.id)


def test_edge_creation_retrieval_and_invalid_relationship_targets(graph):
    source = graph.create_node(node(NodeType.PROBLEM, "problem"))
    target = graph.create_node(node(NodeType.CONCEPT, "concept"))
    edge = graph.create_edge(EdgeCreate(source_id=source.id, target_id=target.id, relationship=RelationshipType.DEPENDS_ON))
    assert graph.get_edges(source.id) == [edge]
    assert graph.neighbors(source.id) == [target]
    with pytest.raises(KeyError):
        graph.create_edge(EdgeCreate(source_id=source.id, target_id=uuid4(), relationship=RelationshipType.USES))
    with pytest.raises(InvalidGraphError):
        graph.create_edge(EdgeCreate(source_id=source.id, target_id=source.id, relationship=RelationshipType.RELATED_TO))
    with pytest.raises(DuplicateGraphError):
        graph.create_edge(EdgeCreate(source_id=source.id, target_id=target.id, relationship=RelationshipType.DEPENDS_ON))
    graph.remove_edge(edge.id)
    assert graph.get_edges(source.id) == []


def test_dependency_descendant_and_path_traversal_handles_cycles(graph):
    question = graph.create_node(node(NodeType.RESEARCH_QUESTION, "question"))
    problem = graph.create_node(node(NodeType.PROBLEM, "problem"))
    result = graph.create_node(node(NodeType.RESULT, "result"))
    graph.create_edge(EdgeCreate(source_id=question.id, target_id=problem.id, relationship=RelationshipType.PART_OF))
    graph.create_edge(EdgeCreate(source_id=problem.id, target_id=result.id, relationship=RelationshipType.PRODUCES))
    graph.create_edge(EdgeCreate(source_id=result.id, target_id=problem.id, relationship=RelationshipType.RELATED_TO))
    assert {item.id for item in graph.descendants(question.id)} == {problem.id, result.id}
    assert {item.id for item in graph.ancestors(result.id)} == {problem.id, question.id}
    path = graph.find_path(GraphPathRequest(source_id=question.id, target_id=result.id))
    assert [item.id for item in path] == [question.id, problem.id, result.id]


def test_persistence_survives_new_store_instance(tmp_path):
    path = str(tmp_path / "persistent.db")
    first = ResearchGraph(SQLiteResearchGraphStore(path))
    created = first.create_node(node(NodeType.SOURCE, "primary source"))
    second = ResearchGraph(SQLiteResearchGraphStore(path))
    assert second.get_node(created.id).name == "primary source"


def test_provenance_and_evidence_traversal_preserve_epistemic_state(graph):
    source = graph.create_node(node(NodeType.SOURCE, "paper", epistemic_state=ClaimStatus.SOURCE_BACKED, confidence=0.9))
    evidence = graph.create_node(node(NodeType.EVIDENCE, "measurement", epistemic_state=ClaimStatus.MEASURED, confidence=0.95))
    claim = graph.create_node(node(
        NodeType.CLAIM,
        "material property claim",
        epistemic_state=ClaimStatus.SOURCE_BACKED,
        confidence=0.85,
        provenance=GraphProvenance(source_ids=[str(source.id)], evidence_ids=[str(evidence.id)]),
    ))
    assert graph.get_node(claim.id).epistemic_state == ClaimStatus.SOURCE_BACKED
    assert {item.id for item in graph.trace_provenance(claim.id)} == {source.id, evidence.id}
    assert {item.id for item in graph.trace_evidence(claim.id)} == {evidence.id}


def test_unknown_and_simulated_states_are_not_promoted(graph):
    unknown = graph.create_node(node(NodeType.UNKNOWN, "missing density", epistemic_state=ClaimStatus.UNKNOWN))
    simulation = graph.create_node(node(NodeType.SIMULATION, "finite element run", epistemic_state=ClaimStatus.SIMULATED))
    assert graph.get_node(unknown.id).epistemic_state == ClaimStatus.UNKNOWN
    assert graph.get_node(simulation.id).epistemic_state == ClaimStatus.SIMULATED
    assert graph.search_graph(GraphSearchRequest(query="density", epistemic_state=ClaimStatus.UNKNOWN))[0].id == unknown.id


def test_knowledge_gap_detection_distinguishes_missing_unknown_and_unvalidated(graph):
    question = graph.create_node(node(NodeType.RESEARCH_QUESTION, "exosuit load question"))
    known = graph.create_node(node(NodeType.CONCEPT, "load", epistemic_state=ClaimStatus.KNOWN))
    unknown = graph.create_node(node(NodeType.PARAMETER, "density", epistemic_state=ClaimStatus.UNKNOWN))
    unvalidated = graph.create_node(node(NodeType.MODEL, "load model", epistemic_state=ClaimStatus.UNVALIDATED))
    for target in (known, unknown, unvalidated):
        graph.create_edge(EdgeCreate(source_id=question.id, target_id=target.id, relationship=RelationshipType.REQUIRES))
    gaps = graph.detect_knowledge_gaps(KnowledgeGapRequest(
        question_id=question.id,
        required_types=[NodeType.EQUATION],
        required_names=["yield strength"],
    ))
    assert [item.name for item in gaps.known] == ["load"]
    assert {item.name for item in gaps.unknown} == {"density"}
    assert {item.name for item in gaps.unvalidated} == {"load model"}
    assert set(gaps.missing) == {"yield strength", "Equation"}


def test_search_filters_by_type_and_project(graph):
    project_id = uuid4()
    graph.create_node(node(NodeType.MATERIAL, "carbon fiber", project_id=project_id))
    graph.create_node(node(NodeType.CONCEPT, "carbon fiber concept"))
    result = graph.search_graph(GraphSearchRequest(query="carbon", node_type=NodeType.MATERIAL, project_id=project_id))
    assert len(result) == 1
    assert result[0].type == NodeType.MATERIAL


def test_api_supports_nodes_edges_paths_and_gaps():
    client = TestClient(app)
    headers = {"X-API-Key": "dev-key"}
    suffix = str(uuid4())
    question = client.post("/api/v1/research-graph/nodes", headers=headers, json={"type": "ResearchQuestion", "name": f"question {suffix}"})
    concept = client.post("/api/v1/research-graph/nodes", headers=headers, json={"type": "Concept", "name": f"concept {suffix}", "epistemic_state": "KNOWN"})
    assert question.status_code == 201 and concept.status_code == 201
    question_id, concept_id = question.json()["id"], concept.json()["id"]
    edge = client.post("/api/v1/research-graph/edges", headers=headers, json={"source_id": question_id, "target_id": concept_id, "relationship": "REQUIRES"})
    assert edge.status_code == 201
    assert client.get(f"/api/v1/research-graph/nodes/{question_id}/neighbors", headers=headers).json()[0]["id"] == concept_id
    path = client.post("/api/v1/research-graph/path", headers=headers, json={"source_id": question_id, "target_id": concept_id})
    assert path.status_code == 200 and len(path.json()) == 2
    gaps = client.post("/api/v1/research-graph/knowledge-gaps", headers=headers, json={"question_id": question_id, "required_names": ["missing concept"]})
    assert gaps.status_code == 200 and "missing concept" in gaps.json()["missing"]
    assert client.get(f"/api/v1/research-graph/nodes/{question_id}").status_code == 401


def test_api_rejects_malformed_relationship():
    client = TestClient(app)
    response = client.post("/api/v1/research-graph/edges", headers={"X-API-Key": "dev-key"}, json={"source_id": str(uuid4()), "target_id": str(uuid4()), "relationship": "MADE_UP"})
    assert response.status_code == 422
