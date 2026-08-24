from collections import defaultdict
from collections.abc import Callable
from typing import Any
from .schemas import Event

Handler = Callable[[Event], Any]

class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[str, list[Handler]] = defaultdict(list)
        self.history: list[Event] = []

    def subscribe(self, event_type: str, handler: Handler) -> None:
        self._handlers[event_type].append(handler)

    def publish(self, event: Event) -> None:
        self.history.append(event)
        handlers = tuple(self._handlers[event.type]) + tuple(self._handlers["*"])
        for handler in handlers:
            handler(event)

class RouterAudit:
    def __init__(self):
        self.events = []
    def record(self, decision):
        self.events.append(decision)
