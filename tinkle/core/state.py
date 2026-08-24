from copy import deepcopy
from threading import RLock
from typing import Any

class StateStore:
    def __init__(self) -> None:
        self._state: dict[str, Any] = {}
        self._lock = RLock()

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            return deepcopy(self._state.get(key, default))

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            self._state[key] = deepcopy(value)

    def delete(self, key: str) -> None:
        with self._lock:
            self._state.pop(key, None)

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return deepcopy(self._state)
