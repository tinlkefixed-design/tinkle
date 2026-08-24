from __future__ import annotations

from collections import deque
from datetime import UTC, datetime
from uuid import UUID

from tinkle.reality_engine import ClaimStatus
from tinkle.research_graph.schemas import (
    EdgeCreate,
    GraphPathRequest,
    GraphSearchRequest,
    KnowledgeGap,
    KnowledgeGapRequest,
    NodeUpdate,
    RelationshipType,
    ResearchGraphEdge,
    ResearchGraphNode,
)
from tinkle.research_graph.store import (
    DuplicateGraphError,
    GraphNotFoundError,
    InvalidGraphError,
    SQLiteResearchGraphStore,
)


class ResearchGraph:
    def __init__(self, store: SQLiteResearchGraphStore | None = None) -> None:
        self.store = store or SQLiteResearchGraphStore()

    def create_node(self, node: ResearchGraphNode) -> ResearchGraphNode:
        return self.store.create_node(node)

    def get_node(self, node_id: UUID) -> ResearchGraphNode:
        return self.store.get_node(node_id)

    def update_node(self, node_id: UUID, changes: NodeUpdate) -> ResearchGraphNode:
        node = self.get_node(node_id)
        data = changes.model_dump(exclude_unset=True)
        data["updated_at"] = datetime.now(UTC)
        return self.store.update_node(node.model_copy(update=data))

    def delete_node(self, node_id: UUID) -> None:
        self.store.delete_node(node_id)

    def create_edge(self, request: EdgeCreate) -> ResearchGraphEdge:
        if request.source_id == request.target_id:
            raise InvalidGraphError("Self-referential graph edges are not permitted")
        return self.store.create_edge(ResearchGraphEdge(**request.model_dump()))

    def get_edges(self, node_id: UUID | None = None,
                  relationship: RelationshipType | None = None) -> list[ResearchGraphEdge]:
        return self.store.get_edges(node_id, relationship.value if relationship else None)

    def remove_edge(self, edge_id: UUID) -> None:
        self.store.remove_edge(edge_id)

    def neighbors(self, node_id: UUID, relationship: RelationshipType | None = None) -> list[ResearchGraphNode]:
        edges = self.get_edges(node_id, relationship)
        ids = {edge.target_id if edge.source_id == node_id else edge.source_id for edge in edges}
        return [self.get_node(item) for item in ids]

    def _walk(self, start: UUID, *, reverse: bool, max_depth: int = 100) -> list[ResearchGraphNode]:
        found: list[ResearchGraphNode] = []
        visited = {start}
        queue = deque([(start, 0)])
        while queue:
            current, depth = queue.popleft()
            if depth >= max_depth:
                continue
            for edge in self.get_edges(current):
                next_id = edge.source_id if reverse and edge.target_id == current else edge.target_id if not reverse and edge.source_id == current else None
                if next_id is None or next_id in visited:
                    continue
                visited.add(next_id)
                found.append(self.get_node(next_id))
                queue.append((next_id, depth + 1))
        return found

    def ancestors(self, node_id: UUID) -> list[ResearchGraphNode]:
        return self._walk(node_id, reverse=True)

    def descendants(self, node_id: UUID) -> list[ResearchGraphNode]:
        return self._walk(node_id, reverse=False)

    def find_path(self, request: GraphPathRequest) -> list[ResearchGraphNode]:
        if request.source_id == request.target_id:
            return [self.get_node(request.source_id)]
        queue = deque([(request.source_id, 0)])
        previous: dict[UUID, UUID | None] = {request.source_id: None}
        while queue:
            current, depth = queue.popleft()
            if depth >= request.max_depth:
                continue
            if len(previous) > 10000:
                break
            for edge in self.get_edges(current, request.relationship):
                if edge.source_id != current or edge.target_id in previous:
                    continue
                previous[edge.target_id] = current
                if edge.target_id == request.target_id:
                    queue.clear()
                    break
                queue.append((edge.target_id, depth + 1))
        if request.target_id not in previous:
            return []
        path: list[UUID] = []
        current: UUID | None = request.target_id
        while current is not None:
            path.append(current)
            current = previous[current]
        return [self.get_node(item) for item in reversed(path)]

    def find_dependencies(self, node_id: UUID) -> list[ResearchGraphNode]:
        return [node for node in self.ancestors(node_id)]

    def find_dependents(self, node_id: UUID) -> list[ResearchGraphNode]:
        return [node for node in self.descendants(node_id)]

    def trace_provenance(self, node_id: UUID) -> list[ResearchGraphNode]:
        node = self.get_node(node_id)
        ids = set(node.provenance.source_ids + node.provenance.evidence_ids + node.provenance.provenance_record_ids)
        return [self.get_node(UUID(item)) for item in ids if self._exists(item)]

    def trace_evidence(self, node_id: UUID) -> list[ResearchGraphNode]:
        node = self.get_node(node_id)
        evidence_ids = set(node.provenance.evidence_ids)
        evidence_ids.update(str(item.id) for item in self.ancestors(node_id) if item.type.value == "Evidence")
        return [self.get_node(UUID(item)) for item in evidence_ids if self._exists(item)]

    def _exists(self, value: str) -> bool:
        try:
            self.get_node(UUID(value))
            return True
        except (ValueError, GraphNotFoundError):
            return False

    def search_graph(self, request: GraphSearchRequest) -> list[ResearchGraphNode]:
        return self.store.search_nodes(
            request.query,
            node_type=request.node_type.value if request.node_type else None,
            project_id=request.project_id,
            epistemic_state=request.epistemic_state.value if request.epistemic_state else None,
            limit=request.limit,
        )

    def detect_knowledge_gaps(self, request: KnowledgeGapRequest) -> KnowledgeGap:
        question = self.get_node(request.question_id)
        connected = self.descendants(question.id)
        known = [node for node in connected if node.epistemic_state not in {ClaimStatus.UNKNOWN, ClaimStatus.UNVALIDATED}]
        unknown = [node for node in connected if node.epistemic_state == ClaimStatus.UNKNOWN]
        unvalidated = [node for node in connected if node.epistemic_state == ClaimStatus.UNVALIDATED]
        known_names = {node.name.casefold() for node in connected}
        missing = [name for name in request.required_names if name.casefold() not in known_names]
        missing.extend(type_.value for type_ in request.required_types if not any(node.type == type_ for node in connected))
        return KnowledgeGap(question_id=question.id, known=known, missing=missing, unknown=unknown, unvalidated=unvalidated)


__all__ = [
    "ClaimStatus",
    "DuplicateGraphError",
    "GraphNotFoundError",
    "InvalidGraphError",
    "RelationshipType",
    "ResearchGraph",
    "ResearchGraphEdge",
    "ResearchGraphNode",
    "SQLiteResearchGraphStore",
]
