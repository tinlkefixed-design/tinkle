from pathlib import Path
from tinkle.sandbox.runner import SandboxRunner, SandboxPolicy
from tinkle.persistence.sqlite_memory import SQLiteMemoryStore
from tinkle.memory.service import MemoryItem
from tinkle.core.schemas import MemoryType


def test_sandbox_runs_and_is_bounded():
    r = SandboxRunner(SandboxPolicy(timeout_ms=2000, cpu_seconds=1, memory_mb=128)).run_python("print(2+3)")
    assert r.ok and r.stdout.strip() == "5"


def test_sandbox_does_not_receive_environment_secrets(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "secret")
    r = SandboxRunner().run_python("import os; print(os.getenv('OPENAI_API_KEY'))")
    assert r.ok and "secret" not in r.stdout


def test_sandbox_timeout():
    r = SandboxRunner(SandboxPolicy(timeout_ms=100, cpu_seconds=1)).run_python("while True: pass")
    assert not r.ok and r.error


def test_persistent_memory_survives_restart(tmp_path: Path):
    db = tmp_path / "memory.db"
    s1 = SQLiteMemoryStore(str(db))
    item = MemoryItem(owner="u", type=MemoryType.semantic, content="durable fact")
    s1.write(item)
    s1._db.close()
    s2 = SQLiteMemoryStore(str(db))
    assert [x.content for x in s2.list("u")] == ["durable fact"]


def test_persistent_memory_delete_is_owner_scoped(tmp_path: Path):
    s = SQLiteMemoryStore(str(tmp_path / "m.db"))
    item = MemoryItem(owner="u", type=MemoryType.semantic, content="x")
    s.write(item)
    assert not s.delete("other", item.id)
    assert s.delete("u", item.id)
