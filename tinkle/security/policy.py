from dataclasses import dataclass
from time import monotonic
from collections import defaultdict, deque

@dataclass(frozen=True)
class SecurityPolicy:
    max_requests_per_minute: int = 120
    max_tool_input_bytes: int = 64_000
    require_sandbox_for_sensitive_tools: bool = True

class RateLimiter:
    def __init__(self, policy: SecurityPolicy, enabled: bool = False):
        self.enabled = enabled
        self.policy = policy
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str) -> bool:
        if not self.enabled:
            return True
        now = monotonic()
        window = self._hits[key]
        while window and now - window[0] >= 60:
            window.popleft()
        if len(window) >= self.policy.max_requests_per_minute:
            return False
        window.append(now)
        return True
