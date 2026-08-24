from datetime import datetime, timezone
from uuid import UUID
from .errors import InvalidStateTransitionError, TaskNotFoundError
from .events import EventBus
from .schemas import Event, Task, TaskCreate, TaskStatus

class TaskService:
    def __init__(self, events: EventBus) -> None:
        self._tasks: dict[UUID, Task] = {}
        self._events = events

    def create(self, data: TaskCreate, owner: str) -> Task:
        task = Task(prompt=data.prompt, project_id=data.project_id, owner=owner)
        self._tasks[task.id] = task
        self._events.publish(Event(
            type="task.created", actor=owner, payload={"task_id": str(task.id)}
        ))
        return task

    def get(self, task_id: UUID, owner: str) -> Task:
        task = self._tasks.get(task_id)
        if task is None or task.owner != owner:
            raise TaskNotFoundError(str(task_id))
        return task

    def run(self, task_id: UUID, owner: str) -> Task:
        task = self.get(task_id, owner)
        if task.status not in {TaskStatus.pending, TaskStatus.failed}:
            raise InvalidStateTransitionError("Only pending or failed tasks may run")
        task.status = TaskStatus.running
        task.updated_at = datetime.now(timezone.utc)
        self._events.publish(Event(
            type="task.started", actor=owner, payload={"task_id": str(task.id)}
        ))
        try:
            # Phase 1 has no model execution. Core execution is a deterministic
            # lifecycle operation; Model Router is Phase 2.
            task.result = "Task accepted by Tinkle Core System; model execution is deferred to Phase 2."
            task.status = TaskStatus.completed
            task.updated_at = datetime.now(timezone.utc)
            self._events.publish(Event(
                type="task.completed", actor=owner, payload={"task_id": str(task.id)}
            ))
        except Exception as exc:
            task.status = TaskStatus.failed
            task.error = str(exc)
            task.updated_at = datetime.now(timezone.utc)
            self._events.publish(Event(
                type="task.failed", actor=owner,
                payload={"task_id": str(task.id), "error": str(exc)}
            ))
            raise
        return task

    def all_for(self, owner: str) -> list[Task]:
        return [t for t in self._tasks.values() if t.owner == owner]

    def delete_for(self, owner: str) -> None:
        for task_id in [t.id for t in self.all_for(owner)]:
            del self._tasks[task_id]
