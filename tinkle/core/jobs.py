from __future__ import annotations
import json, sqlite3
from pathlib import Path
from threading import Lock
from uuid import UUID
from datetime import datetime, timezone
from .schemas import Job


def _now() -> datetime:
    return datetime.now(timezone.utc)


class JobQueue:
    """Durable job queue with restart recovery and explicit lifecycle states.

    Jobs are persisted locally so a process restart cannot silently lose queued or
    running work. A job observed as ``running`` on startup is recovered to
    ``queued`` and its attempt counter is incremented.
    """
    VALID = {'queued', 'running', 'completed', 'failed', 'cancelled'}

    def __init__(self, path: str = './data/tinkle_jobs.db') -> None:
        self.path = path
        if path != ':memory:':
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(path, check_same_thread=False)
        self._db.execute('PRAGMA journal_mode=WAL')
        self._db.execute('''CREATE TABLE IF NOT EXISTS jobs(
            id TEXT PRIMARY KEY, type TEXT NOT NULL, status TEXT NOT NULL,
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
            attempts INTEGER NOT NULL DEFAULT 0, error TEXT, payload TEXT NOT NULL DEFAULT '{}')''')
        self._db.execute('CREATE INDEX IF NOT EXISTS idx_jobs_status_created ON jobs(status, created_at)')
        self._db.commit()
        self._lock = Lock()
        self._recover_running()

    def _recover_running(self) -> None:
        with self._lock:
            now = _now().isoformat()
            self._db.execute("UPDATE jobs SET status='queued', updated_at=?, attempts=attempts+1 WHERE status='running'", (now,))
            self._db.commit()

    def enqueue(self, job_type: str) -> Job:
        job = Job(type=job_type)
        now = _now().isoformat()
        with self._lock:
            self._db.execute('INSERT INTO jobs(id,type,status,created_at,updated_at,attempts,error,payload) VALUES(?,?,?,?,?,?,?,?)',
                (str(job.id), job.type, 'queued', job.created_at.isoformat(), now, 0, None, '{}'))
            self._db.commit()
        return job

    def next(self) -> Job | None:
        with self._lock:
            row = self._db.execute("SELECT id,type,status,created_at FROM jobs WHERE status='queued' ORDER BY created_at LIMIT 1").fetchone()
            if not row:
                return None
            now = _now().isoformat()
            self._db.execute("UPDATE jobs SET status='running', updated_at=?, attempts=attempts+1 WHERE id=? AND status='queued'", (now, row[0]))
            self._db.commit()
            return Job(id=UUID(row[0]), type=row[1], status='running', created_at=datetime.fromisoformat(row[3]))

    def update(self, job_id: UUID, status: str, error: str | None = None) -> Job:
        if status not in self.VALID:
            raise ValueError(f'Invalid job status: {status}')
        with self._lock:
            row = self._db.execute('SELECT id,type,created_at FROM jobs WHERE id=?', (str(job_id),)).fetchone()
            if not row:
                raise KeyError(str(job_id))
            self._db.execute('UPDATE jobs SET status=?, updated_at=?, error=? WHERE id=?',
                             (status, _now().isoformat(), error, str(job_id)))
            self._db.commit()
            return Job(id=UUID(row[0]), type=row[1], status=status, created_at=datetime.fromisoformat(row[2]))

    def get(self, job_id: UUID) -> Job | None:
        with self._lock:
            row = self._db.execute('SELECT id,type,status,created_at FROM jobs WHERE id=?', (str(job_id),)).fetchone()
        return Job(id=UUID(row[0]), type=row[1], status=row[2], created_at=datetime.fromisoformat(row[3])) if row else None

    def size(self) -> int:
        with self._lock:
            return int(self._db.execute("SELECT COUNT(*) FROM jobs WHERE status='queued'").fetchone()[0])

    def recover(self) -> int:
        with self._lock:
            now = _now().isoformat()
            cur = self._db.execute("UPDATE jobs SET status='queued', updated_at=?, attempts=attempts+1 WHERE status='running'", (now,))
            self._db.commit()
            return cur.rowcount
