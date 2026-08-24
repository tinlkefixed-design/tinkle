from uuid import uuid4
import pytest
from tinkle.core.auth import AuthService
from tinkle.core.config import settings
from tinkle.core.events import EventBus
from tinkle.core.errors import (
    AuthenticationError, InvalidStateTransitionError, TaskNotFoundError
)
from tinkle.core.schemas import Event, Permission, ProjectCreate, TaskCreate, TaskStatus
from tinkle.core.projects import ProjectService
from tinkle.core.state import StateStore
from tinkle.core.tasks import TaskService

def test_event_bus_and_history():
    bus = EventBus()
    received = []
    bus.subscribe("test.event", lambda e: received.append(e.payload))
    bus.publish(Event(type="test.event", payload={"x": 1}))
    assert received == [{"x": 1}]
    assert len(bus.history) == 1

def test_state_isolated_copy():
    state = StateStore()
    value = {"a": [1]}
    state.set("x", value)
    value["a"].append(2)
    assert state.get("x") == {"a": [1]}

def test_project_and_task_lifecycle():
    bus = EventBus()
    projects = ProjectService()
    tasks = TaskService(bus)
    project = projects.create(ProjectCreate(name="P"), "default")
    task = tasks.create(TaskCreate(prompt="Hello", project_id=project.id), "default")
    assert task.status == TaskStatus.pending
    result = tasks.run(task.id, "default")
    assert result.status == TaskStatus.completed
    assert "deferred to Phase 2" in result.result

def test_missing_task():
    tasks = TaskService(EventBus())
    with pytest.raises(TaskNotFoundError):
        tasks.get(uuid4(), "default")

def test_invalid_transition():
    bus = EventBus()
    tasks = TaskService(bus)
    task = tasks.create(TaskCreate(prompt="x"), "default")
    tasks.run(task.id, "default")
    with pytest.raises(InvalidStateTransitionError):
        tasks.run(task.id, "default")

def test_authentication():
    auth = AuthService()
    assert auth.authenticate(next(iter(settings.valid_api_keys))).name == "default"
    with pytest.raises(AuthenticationError):
        auth.authenticate("wrong-key")
