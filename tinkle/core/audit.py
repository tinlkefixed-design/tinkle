from .events import EventBus
from .schemas import Event

class AuditLog:
    IMPORTANT_EVENTS = {
        "project.created", "project.deleted",
        "task.created", "task.started", "task.completed", "task.failed",
        "data.exported", "data.deleted",
        "auth.denied", "permission.denied",
        "tool.executed", "tool.denied",
        "security.rate_limited", "security.policy_checked",
        "self_improvement.production_blocked",
    }

    def __init__(self, events: EventBus) -> None:
        self.entries: list[Event] = []
        events.subscribe("*", self._record_all)
        self.events = events

    def _record_all(self, event: Event) -> None:
        if event.type in self.IMPORTANT_EVENTS:
            self.entries.append(event)

    def record(self, event: Event) -> None:
        if event.type in self.IMPORTANT_EVENTS:
            self.entries.append(event)
