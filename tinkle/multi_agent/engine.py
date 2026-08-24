from __future__ import annotations

from typing import Protocol

from tinkle.core.schemas import ProviderResponse, Privacy, RoutingRequest, TaskType
from tinkle.multi_agent.schemas import AgentRequest, AgentResult, AgentRole, MultiAgentResult, ROLE_OBJECTIVES
from tinkle.router.runtime import ModelRuntime
from tinkle.router.router import ModelRouter
from tinkle.router.catalog import default_catalog


class TextGenerator(Protocol):
    def generate(self, request: RoutingRequest) -> ProviderResponse: ...


class MultiAgentSystem:
    """Executable role-based multi-agent orchestration.

    Each agent gets an isolated role prompt and is routed independently. The
    system never fabricates findings: if a provider is unavailable, that role
    is reported as FAILED instead of producing placeholder content.
    """

    def __init__(self, runtime: TextGenerator | None = None) -> None:
        self.runtime = runtime or ModelRuntime(ModelRouter(default_catalog()))

    def run(self, request: AgentRequest) -> MultiAgentResult:
        roles = request.roles or list(AgentRole)
        if not roles:
            raise ValueError("At least one agent role is required")
        unique_roles = list(dict.fromkeys(roles))
        agents: list[AgentResult] = []
        for role in unique_roles:
            agents.append(self._run_agent(request, role))
        successful = [a for a in agents if a.status == "COMPLETED"]
        status = "COMPLETED" if successful and len(successful) == len(agents) else (
            "PARTIAL" if successful else "FAILED"
        )
        synthesis = self._synthesize(request, successful) if successful else None
        return MultiAgentResult(
            goal=request.goal.strip(), agents=agents, roles=unique_roles,
            status=status, synthesis=synthesis,
        )

    def _run_agent(self, request: AgentRequest, role: AgentRole) -> AgentResult:
        prompt = self._build_prompt(request, role)
        routing = RoutingRequest(
            prompt=prompt,
            task_type=self._task_type(role),
            difficulty=request.difficulty,
            privacy=request.privacy,
            context_tokens=min(max(len(prompt) // 4, 1000), 120000),
            require_reasoning=role in {AgentRole.scientist, AgentRole.mathematician, AgentRole.engineer, AgentRole.skeptic, AgentRole.verifier, AgentRole.judge},
            require_coding=role == AgentRole.programmer,
            require_tool_use=role in {AgentRole.researcher, AgentRole.programmer, AgentRole.data_scientist},
        )
        try:
            response = self.runtime.generate(routing)
            return AgentResult(
                role=role,
                objective=ROLE_OBJECTIVES[role],
                input_summary=request.goal.strip(),
                findings=[response.text],
                status="COMPLETED",
                model_id=response.model_id,
                provider=response.provider,
            )
        except Exception as exc:
            return AgentResult(
                role=role,
                objective=ROLE_OBJECTIVES[role],
                input_summary=request.goal.strip(),
                findings=[],
                status="FAILED",
                error=f"{type(exc).__name__}: {exc}",
            )

    @staticmethod
    def _build_prompt(request: AgentRequest, role: AgentRole) -> str:
        context = request.context or {}
        return (
            "You are one specialist agent inside Tinkle.\n"
            f"Role: {role.value}\n"
            f"Objective: {ROLE_OBJECTIVES[role]}\n\n"
            f"Goal:\n{request.goal.strip()}\n\n"
            f"Context:\n{context}\n\n"
            "Produce a concise, evidence-aware result. Separate facts, calculations, "
            "assumptions, and hypotheses. Do not claim external verification you did not perform."
        )

    @staticmethod
    def _task_type(role: AgentRole) -> TaskType:
        if role == AgentRole.programmer:
            return TaskType.coding
        if role == AgentRole.mathematician:
            return TaskType.math
        if role == AgentRole.researcher:
            return TaskType.research
        if role in {AgentRole.scientist, AgentRole.engineer, AgentRole.skeptic, AgentRole.verifier, AgentRole.judge}:
            return TaskType.reasoning
        return TaskType.general

    def _synthesize(self, request: AgentRequest, successful: list[AgentResult]) -> str:
        evidence = "\n\n".join(
            f"[{agent.role.value}]\n{agent.findings[0]}" for agent in successful if agent.findings
        )
        prompt = (
            "You are Tinkle's synthesis judge. Combine the independent specialist results below. "
            "Identify agreements, contradictions, assumptions, and unresolved uncertainty. "
            "Do not invent evidence. End with a concise recommended conclusion.\n\n"
            f"Goal:\n{request.goal.strip()}\n\nResults:\n{evidence}"
        )
        routing = RoutingRequest(
            prompt=prompt,
            task_type=TaskType.reasoning,
            difficulty=max(request.difficulty, .7),
            privacy=request.privacy,
            context_tokens=min(max(len(prompt) // 4, 1000), 120000),
            require_reasoning=True,
        )
        try:
            return self.runtime.generate(routing).text
        except Exception as exc:
            return f"Synthesis unavailable: {type(exc).__name__}: {exc}"
