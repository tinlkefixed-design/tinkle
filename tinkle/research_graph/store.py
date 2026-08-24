from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from threading import RLock
from typing import Any
from uuid import UUID

from tinkle.research_graph.schemas import ResearchGraphEdge, ResearchGraphNode


class GraphNotFoundError(KeyError):
    pass


class DuplicateGraphError(ValueError):
    pass


class InvalidGraphError(ValueError):
    pass


class SQLiteResearchGraphStore:
    """Local durable storage for typed research nodes and semantic edges."""

    def __init__(self, path: str = "./data/research_graph.db") -> None:
        self.path = path
        if path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(path, check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        self._lock = RLock()
        self._db.execute(
            """CREATE TABLE IF NOT EXISTS research_nodes(
                id TEXT PRIMARY KEY, type TEXT NOT NULL, name TEXT NOT NULL,
                payload TEXT NOT NULL, project_id TEXT, created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL)"""
        )
        self._db.execute(
            """CREATE TABLE IF NOT EXISTS research_edges(
                id TEXT PRIMARY KEY, source_id TEXT NOT NULL, target_id TEXT NOT NULL,
                relationship TEXT NOT NULL, payload TEXT NOT NULL,
                created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                UNIQUE(source_id, target_id, relationship),
                FOREIGN KEY(source_id) REFERENCES research_nodes(id) ON DELETE CASCADE,
                FOREIGN KEY(target_id) REFERENCES research_nodes(id) ON DELETE CASCADE)"""
        )
        self._db.execute("CREATE INDEX IF NOT EXISTS idx_research_nodes_project ON research_nodes(project_id)")
        self._db.execute("CREATE INDEX IF NOT EXISTS idx_research_edges_source ON research_edges(source_id)")
        self._db.execute("CREATE INDEX IF NOT EXISTS idx_research_edges_target ON research_edges(target_id)")
        self._db.commit()

    @staticmethod
    def _node(row: sqlite3.Row) -> ResearchGraphNode:
        return ResearchGraphNode.model_validate(json.loads(row["payload"]))

    @staticmethod
    def _edge(row: sqlite3.Row) -> ResearchGraphEdge:
        return ResearchGraphEdge.model_validate(json.loads(row["payload"]))

    def create_node(self, node: ResearchGraphNode) -> ResearchGraphNode:
        with self._lock:
            try:
                self._db.execute(
                    "INSERT INTO research_nodes VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (str(node.id), node.type.value, node.name, node.model_dump_json(),
                     str(node.project_id) if node.project_id else None,
                     node.created_at.isoformat(), node.updated_at.isoformat()),
                )
                self._db.commit()
            except sqlite3.IntegrityError as exc:
                raise DuplicateGraphError(f"Node already exists: {node.id}") from exc
        return node

    def get_node(self, node_id: UUID) -> ResearchGraphNode:
        row = self._db.execute("SELECT * FROM research_nodes WHERE id=?", (str(node_id),)).fetchone()
        if row is None:
            raise GraphNotFoundError(f"Node not found: {node_id}")
        return self._node(row)

    def update_node(self, node: ResearchGraphNode) -> ResearchGraphNode:
        with self._lock:
            if self._db.execute("SELECT 1 FROM research_nodes WHERE id=?", (str(node.id),)).fetchone() is None:
                raise GraphNotFoundError(f"Node not found: {node.id}")
            self._db.execute(
                "UPDATE research_nodes SET type=?, name=?, payload=?, project_id=?, updated_at=? WHERE id=?",
                (node.type.value, node.name, node.model_dump_json(),
                 str(node.project_id) if node.project_id else None,
                 node.updated_at.isoformat(), str(node.id)),
            )
            self._db.commit()
        return node

    def delete_node(self, node_id: UUID) -> None:
        with self._lock:
            cur = self._db.execute("DELETE FROM research_nodes WHERE id=?", (str(node_id),))
            if cur.rowcount != 1:
                raise GraphNotFoundError(f"Node not found: {node_id}")
            self._db.commit()

    def create_edge(self, edge: ResearchGraphEdge) -> ResearchGraphEdge:
        with self._lock:
            for node_id in (edge.source_id, edge.target_id):
                if self._db.execute("SELECT 1 FROM research_nodes WHERE id=?", (str(node_id),)).fetchone() is None:
                    raise GraphNotFoundError(f"Node not found: {node_id}")
            try:
                self._db.execute(
                    "INSERT INTO research_edges VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (str(edge.id), str(edge.source_id), str(edge.target_id), edge.relationship.value,
                     edge.model_dump_json(), edge.created_at.isoformat(), edge.updated_at.isoformat()),
                )
                self._db.commit()
            except sqlite3.IntegrityError as exc:
                raise DuplicateGraphError("Equivalent graph edge already exists") from exc
        return edge

    def get_edge(self, edge_id: UUID) -> ResearchGraphEdge:
        row = self._db.execute("SELECT * FROM research_edges WHERE id=?", (str(edge_id),)).fetchone()
        if row is None:
            raise GraphNotFoundError(f"Edge not found: {edge_id}")
        return self._edge(row)

    def get_edges(self, node_id: UUID | None = None, relationship: str | None = None) -> list[ResearchGraphEdge]:
        query = "SELECT * FROM research_edges"
        clauses: list[str] = []
        args: list[Any] = []
        if node_id is not None:
            clauses.append("(source_id=? OR target_id=?)")
            args.extend([str(node_id), str(node_id)])
        if relationship is not None:
            clauses.append("relationship=?")
            args.append(relationship)
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY created_at, id"
        return [self._edge(row) for row in self._db.execute(query, args).fetchall()]

    def remove_edge(self, edge_id: UUID) -> None:
        with self._lock:
            cur = self._db.execute("DELETE FROM research_edges WHERE id=?", (str(edge_id),))
            if cur.rowcount != 1:
                raise GraphNotFoundError(f"Edge not found: {edge_id}")
            self._db.commit()

    def search_nodes(self, query: str, *, node_type: str | None = None,
                     project_id: UUID | None = None, epistemic_state: str | None = None,
                     limit: int = 50) -> list[ResearchGraphNode]:
        terms = [f"%{part}%" for part in query.casefold().split()]
        clauses = ["(lower(name) LIKE ? OR lower(payload) LIKE ?)"] * len(terms)
        args: list[Any] = [value for term in terms for value in (term, term)]
        if node_type:
            clauses.append("type=?")
            args.append(node_type)
        if project_id:
            clauses.append("project_id=?")
            args.append(str(project_id))
        rows = self._db.execute(
            "SELECT * FROM research_nodes WHERE " + " AND ".join(clauses) + " ORDER BY updated_at DESC LIMIT ?",
            [*args, limit],
        ).fetchall()
        nodes = [self._node(row) for row in rows]
        if epistemic_state:
            nodes = [node for node in nodes if node.epistemic_state.value == epistemic_state]
        return nodes
