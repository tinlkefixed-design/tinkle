from __future__ import annotations
import json, sqlite3
from pathlib import Path
from uuid import UUID
from tinkle.memory.service import MemoryItem
from tinkle.core.schemas import MemoryType

class SQLiteMemoryStore:
    """Durable local memory store implementing the MemoryService persistence contract."""
    def __init__(self, path: str = "./data/tinkle.db") -> None:
        self.path = path
        if path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(path, check_same_thread=False)
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.execute("PRAGMA foreign_keys=ON")
        self._db.execute("""CREATE TABLE IF NOT EXISTS memory_items(
            id TEXT PRIMARY KEY, owner TEXT NOT NULL, type TEXT NOT NULL,
            content TEXT NOT NULL, project_id TEXT, task_id TEXT,
            metadata TEXT NOT NULL, created_at TEXT NOT NULL)""")
        self._db.execute("CREATE INDEX IF NOT EXISTS idx_memory_owner ON memory_items(owner)")
        self._db.commit()

    def write(self, item: MemoryItem) -> MemoryItem:
        self._db.execute("INSERT OR REPLACE INTO memory_items VALUES (?,?,?,?,?,?,?,?)",
            (str(item.id), item.owner, item.type.value, item.content,
             str(item.project_id) if item.project_id else None,
             str(item.task_id) if item.task_id else None,
             json.dumps(item.metadata, ensure_ascii=False), item.created_at.isoformat()))
        self._db.commit(); return item

    def list(self, owner: str, memory_type: MemoryType | None = None, project_id: UUID | None = None) -> list[MemoryItem]:
        q = "SELECT * FROM memory_items WHERE owner=?"; args: list[object] = [owner]
        if memory_type is not None: q += " AND type=?"; args.append(memory_type.value)
        if project_id is not None: q += " AND project_id=?"; args.append(str(project_id))
        q += " ORDER BY created_at ASC"
        rows = self._db.execute(q, args).fetchall()
        return [MemoryItem(id=UUID(r[0]), owner=r[1], type=MemoryType(r[2]), content=r[3],
                            project_id=UUID(r[4]) if r[4] else None,
                            task_id=UUID(r[5]) if r[5] else None,
                            metadata=json.loads(r[6]), created_at=r[7]) for r in rows]

    def delete(self, owner: str, item_id: UUID) -> bool:
        cur = self._db.execute("DELETE FROM memory_items WHERE owner=? AND id=?", (owner, str(item_id)))
        self._db.commit(); return cur.rowcount == 1

    def delete_owner(self, owner: str) -> int:
        cur = self._db.execute("DELETE FROM memory_items WHERE owner=?", (owner,)); self._db.commit(); return cur.rowcount
