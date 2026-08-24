from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.research_graph import (
    DuplicateGraphError,
    EdgeCreate,
    GraphNotFoundError,
    GraphPathRequest,
    GraphSearchRequest,
    KnowledgeGap,
    KnowledgeGapRequest,
    NodeUpdate,
    RelationshipType,
    ResearchGraph,
    ResearchGraphNode,
)

router = APIRouter(prefix="/api/v1/research-graph", tags=["research-graph"])
graph = ResearchGraph()


def not_found(exc: GraphNotFoundError) -> HTTPException:
    return HTTPException(status_code=404, detail=str(exc))


@router.post("/nodes", response_model=ResearchGraphNode, status_code=201)
def create_node(node: ResearchGraphNode, p: Principal = Depends(principal_from_key)):
    require(p, Permission.write)
    try:
        return graph.create_node(node)
    except DuplicateGraphError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/nodes/{node_id}", response_model=ResearchGraphNode)
def get_node(node_id: UUID, p: Principal = Depends(principal_from_key)):
    require(p, Permission.read)
    try:
        return graph.get_node(node_id)
    except GraphNotFoundError as exc:
        raise not_found(exc) from exc


@router.patch("/nodes/{node_id}", response_model=ResearchGraphNode)
def update_node(node_id: UUID, changes: NodeUpdate, p: Principal = Depends(principal_from_key)):
    require(p, Permission.write)
    try:
        return graph.update_node(node_id, changes)
    except GraphNotFoundError as exc:
        raise not_found(exc) from exc


@router.delete("/nodes/{node_id}", status_code=204)
def delete_node(node_id: UUID, p: Principal = Depends(principal_from_key)):
    require(p, Permission.write)
    try:
        graph.delete_node(node_id)
    except GraphNotFoundError as exc:
        raise not_found(exc) from exc


@router.post("/edges", response_model=object, status_code=201)
def create_edge(edge: EdgeCreate, p: Principal = Depends(principal_from_key)):
    require(p, Permission.write)
    try:
        return graph.create_edge(edge)
    except (DuplicateGraphError, GraphNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/edges", response_model=list)
def get_edges(
    node_id: UUID | None = None,
    relationship: RelationshipType | None = None,
    p: Principal = Depends(principal_from_key),
):
    require(p, Permission.read)
    return graph.get_edges(node_id, relationship)


@router.delete("/edges/{edge_id}", status_code=204)
def remove_edge(edge_id: UUID, p: Principal = Depends(principal_from_key)):
    require(p, Permission.write)
    try:
        graph.remove_edge(edge_id)
    except GraphNotFoundError as exc:
        raise not_found(exc) from exc


@router.get("/nodes/{node_id}/neighbors", response_model=list[ResearchGraphNode])
def neighbors(node_id: UUID, relationship: RelationshipType | None = None, p: Principal = Depends(principal_from_key)):
    require(p, Permission.read)
    try:
        graph.get_node(node_id)
        return graph.neighbors(node_id, relationship)
    except GraphNotFoundError as exc:
        raise not_found(exc) from exc


@router.get("/nodes/{node_id}/dependencies", response_model=list[ResearchGraphNode])
def dependencies(node_id: UUID, p: Principal = Depends(principal_from_key)):
    require(p, Permission.read)
    try:
        return graph.find_dependencies(node_id)
    except GraphNotFoundError as exc:
        raise not_found(exc) from exc


@router.get("/nodes/{node_id}/dependents", response_model=list[ResearchGraphNode])
def dependents(node_id: UUID, p: Principal = Depends(principal_from_key)):
    require(p, Permission.read)
    try:
        return graph.find_dependents(node_id)
    except GraphNotFoundError as exc:
        raise not_found(exc) from exc


@router.get("/nodes/{node_id}/provenance", response_model=list[ResearchGraphNode])
def provenance(node_id: UUID, p: Principal = Depends(principal_from_key)):
    require(p, Permission.read)
    try:
        return graph.trace_provenance(node_id)
    except GraphNotFoundError as exc:
        raise not_found(exc) from exc


@router.get("/nodes/{node_id}/evidence", response_model=list[ResearchGraphNode])
def evidence(node_id: UUID, p: Principal = Depends(principal_from_key)):
    require(p, Permission.read)
    try:
        return graph.trace_evidence(node_id)
    except GraphNotFoundError as exc:
        raise not_found(exc) from exc


@router.post("/search", response_model=list[ResearchGraphNode])
def search(request: GraphSearchRequest, p: Principal = Depends(principal_from_key)):
    require(p, Permission.read)
    return graph.search_graph(request)


@router.post("/path", response_model=list[ResearchGraphNode])
def path(request: GraphPathRequest, p: Principal = Depends(principal_from_key)):
    require(p, Permission.read)
    try:
        return graph.find_path(request)
    except GraphNotFoundError as exc:
        raise not_found(exc) from exc


@router.post("/knowledge-gaps", response_model=KnowledgeGap)
def knowledge_gaps(request: KnowledgeGapRequest, p: Principal = Depends(principal_from_key)):
    require(p, Permission.read)
    try:
        return graph.detect_knowledge_gaps(request)
    except GraphNotFoundError as exc:
        raise not_found(exc) from exc
