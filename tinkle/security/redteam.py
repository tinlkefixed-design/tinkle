from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Any
from tinkle.core.schemas import Permission, ToolRequest
from tinkle.security.policy import SecurityPolicy, RateLimiter

@dataclass(frozen=True)
class RedTeamCase:
    name: str
    run: Callable[[], bool]
    threat: str

@dataclass(frozen=True)
class RedTeamResult:
    name: str
    threat: str
    passed: bool
    error: str | None = None


def run_red_team(*, executor: Any, registry: Any, sandbox: Any) -> list[RedTeamResult]:
    policy = SecurityPolicy(max_tool_input_bytes=64_000, require_sandbox_for_sensitive_tools=True)
    limiter = RateLimiter(SecurityPolicy(max_requests_per_minute=2), enabled=True)

    def rate_limit() -> bool:
        return limiter.allow("attacker") and limiter.allow("attacker") and not limiter.allow("attacker")

    def oversized_tool_input() -> bool:
        result = executor.execute(ToolRequest(tool="calculator", input={"expression": "x", "payload": "a" * (policy.max_tool_input_bytes + 1)}), {Permission.execute})
        return not result.ok and "size limit" in (result.error or "")

    def permission_bypass() -> bool:
        result = executor.execute(ToolRequest(tool="file_reader", input={"path": "/etc/passwd"}), {Permission.read})
        return not result.ok

    def sensitive_tool_gate() -> bool:
        specs = {s.name: s for s in registry.list()}
        sensitive = [s for s in specs.values() if s.requires_sandbox]
        if not sensitive:
            return True
        result = executor.execute(ToolRequest(tool=sensitive[0].name, input={}), {Permission.execute})
        return not result.ok and "Sandbox" in (result.error or "")

    def sandbox_file_escape() -> bool:
        r = sandbox.run_python("open('/etc/passwd').read()")
        # The local runner's isolation contract is that failure is acceptable; a successful read is a fail.
        return not r.ok

    def sandbox_secret_exposure() -> bool:
        r = sandbox.run_python("import os; print(os.environ.get('OPENAI_API_KEY', ''))")
        return r.ok and not r.stdout.strip() or (not r.ok)

    cases = [
        RedTeamCase("rate-limit-bypass", rate_limit, "abuse/rate exhaustion"),
        RedTeamCase("oversized-tool-input", oversized_tool_input, "resource exhaustion"),
        RedTeamCase("permission-bypass", permission_bypass, "privilege escalation"),
        RedTeamCase("sensitive-tool-gate", sensitive_tool_gate, "tool abuse"),
        RedTeamCase("sandbox-file-escape", sandbox_file_escape, "sandbox escape"),
        RedTeamCase("sandbox-secret-exposure", sandbox_secret_exposure, "secret leakage"),
    ]
    results: list[RedTeamResult] = []
    for case in cases:
        try:
            results.append(RedTeamResult(case.name, case.threat, bool(case.run())))
        except Exception as exc:
            results.append(RedTeamResult(case.name, case.threat, False, f"{type(exc).__name__}: {exc}"))
    return results
