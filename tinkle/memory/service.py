from datetime import datetime, timezone
from threading import RLock
from typing import Any, List
from uuid import UUID, uuid4
import json, sqlite3
from pathlib import Path
from pydantic import BaseModel, Field
from tinkle.core.schemas import MemoryType

class MemoryItem(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    owner: str
    type: MemoryType
    content: str = Field(min_length=1, max_length=50000)
    project_id: UUID | None = None
    task_id: UUID | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MemoryService:
    """Durable memory service with owner/project isolation and local persistence."""
    def __init__(self, path: str = ":memory:") -> None:
        self.path=path
        if path != ":memory:": Path(path).parent.mkdir(parents=True,exist_ok=True)
        self._db=sqlite3.connect(path,check_same_thread=False)
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.execute("CREATE TABLE IF NOT EXISTS memory(id TEXT PRIMARY KEY,owner TEXT,type TEXT,content TEXT,project_id TEXT,task_id TEXT,metadata TEXT,created_at TEXT)")
        self._db.execute("CREATE INDEX IF NOT EXISTS idx_memory_owner ON memory(owner)")
        self._db.commit(); self._lock=RLock()
    def write(self, *, owner:str,memory_type:MemoryType,content:str,project_id:UUID|None=None,task_id:UUID|None=None,metadata:dict[str,Any]|None=None)->MemoryItem:
        item=MemoryItem(owner=owner,type=memory_type,content=content,project_id=project_id,task_id=task_id,metadata=metadata or {})
        with self._lock:
            self._db.execute("INSERT INTO memory VALUES(?,?,?,?,?,?,?,?)",(str(item.id),owner,item.type.value,content,str(project_id) if project_id else None,str(task_id) if task_id else None,json.dumps(item.metadata,ensure_ascii=False),item.created_at.isoformat())); self._db.commit()
        return item
    def _rows(self,owner:str,memory_type:MemoryType|None=None,project_id:UUID|None=None):
        q="SELECT id,owner,type,content,project_id,task_id,metadata,created_at FROM memory WHERE owner=?"; args=[owner]
        if memory_type: q+=" AND type=?"; args.append(memory_type.value)
        if project_id: q+=" AND project_id=?"; args.append(str(project_id))
        q+=" ORDER BY created_at ASC"
        return self._db.execute(q,args).fetchall()
    @staticmethod
    def _item(row):
        return MemoryItem(id=UUID(row[0]),owner=row[1],type=MemoryType(row[2]),content=row[3],project_id=UUID(row[4]) if row[4] else None,task_id=UUID(row[5]) if row[5] else None,metadata=json.loads(row[6] or "{}"),created_at=datetime.fromisoformat(row[7]))
    def list(self,owner:str,memory_type:MemoryType|None=None,project_id:UUID|None=None)->List[MemoryItem]:
        with self._lock: return [self._item(r) for r in self._rows(owner,memory_type,project_id)]
    def search(self,owner:str,query:str,memory_type:MemoryType|None=None)->List[MemoryItem]:
        q=query.casefold().strip()
        if not q:return []
        return [x for x in reversed(self.list(owner,memory_type)) if q in x.content.casefold()]
    def delete(self,owner:str,item_id:UUID)->bool:
        with self._lock:
            cur=self._db.execute("DELETE FROM memory WHERE id=? AND owner=?",(str(item_id),owner)); self._db.commit(); return cur.rowcount==1
    def export_owner(self,owner:str)->List[MemoryItem]: return self.list(owner)
    def delete_owner(self,owner:str)->int:
        with self._lock:
            cur=self._db.execute("DELETE FROM memory WHERE owner=?",(owner,)); self._db.commit(); return cur.rowcount
