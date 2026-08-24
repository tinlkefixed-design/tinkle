from collections.abc import Callable
from typing import Any
from tinkle.core.errors import ToolNotFoundError, ToolPermissionError
from tinkle.core.schemas import Permission, ToolSpec

class Tool:
    def __init__(self, spec: ToolSpec, handler: Callable[[dict[str, Any]], Any]):
        self.spec, self.handler = spec, handler

class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}
    def register(self, tool: Tool) -> None:
        if tool.spec.name in self._tools:
            raise ValueError(f"duplicate tool: {tool.spec.name}")
        self._tools[tool.spec.name] = tool
    def get(self, name: str) -> Tool:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise ToolNotFoundError(name) from exc
    def list(self) -> list[ToolSpec]:
        return [t.spec for t in self._tools.values()]
    def require(self, name: str, permissions: set[Permission]) -> Tool:
        tool = self.get(name)
        if not tool.spec.permissions.issubset(permissions) and Permission.admin not in permissions:
            raise ToolPermissionError(f"insufficient permissions for {name}")
        return tool
