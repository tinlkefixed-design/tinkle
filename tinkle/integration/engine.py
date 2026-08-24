from __future__ import annotations
from dataclasses import dataclass
from time import perf_counter
from typing import Any

from tinkle.core.events import EventBus
from tinkle.core.schemas import Event, MemoryType, Permission, Privacy, RoutingRequest, TaskType, ToolRequest
from tinkle.guardian.engine import Guardian
from tinkle.guardian.schemas import GuardianRequest
from tinkle.metamind.orchestrator import MetaMind
from tinkle.metamind.schemas import TaskRequest
from tinkle.multi_agent.engine import MultiAgentSystem
from tinkle.multi_agent.schemas import AgentRequest
from tinkle.planner.engine import Planner
from tinkle.planner.schemas import PlannerRequest
from tinkle.memory.service import MemoryService
from tinkle.observer.engine import TinkleObserver
from tinkle.observer.schemas import ObserverEventRequest
from tinkle.router.router import ModelRouter
from tinkle.tools.executor import ToolExecutor


@dataclass(frozen=True)
class PhaseContract:
    phase: int
    name: str


PHASES: tuple[PhaseContract, ...] = (
    PhaseContract(1, "Core System"),
    PhaseContract(2, "Model Router"),
    PhaseContract(3, "Tool System"),
    PhaseContract(4, "Memory System"),
    PhaseContract(5, "Knowledge Engine"),
    PhaseContract(6, "Provenance"),
    PhaseContract(7, "Meta-Mind"),
    PhaseContract(8, "Problem Reframing"),
    PhaseContract(9, "Cognitive Compiler"),
    PhaseContract(10, "Planner"),
    PhaseContract(11, "Multi-Agent System"),
    PhaseContract(12, "Guardian"),
    PhaseContract(13, "Mathematics Engine"),
    PhaseContract(14, "Science Engine"),
    PhaseContract(15, "Engineering Engine"),
    PhaseContract(16, "Simulation Engine"),
    PhaseContract(17, "Research Engine"),
    PhaseContract(18, "Hypothesis Universe"),
    PhaseContract(19, "Discovery Engine"),
    PhaseContract(20, "Failure Atlas"),
    PhaseContract(21, "Skill Evolution"),
    PhaseContract(22, "Self-Evaluation"),
    PhaseContract(23, "Tinkle Observer"),
    PhaseContract(24, "Controlled Self-Improvement"),
    PhaseContract(25, "Security Hardening"),
    PhaseContract(26, "Privacy System"),
    PhaseContract(27, "Complete UI"),
)


class ObserverEventBridge:
    """Translate concrete system events into Observer observations only when a metric is justified."""

    EVENT_METRICS = {
        "security.rate_limited": "Security Events",
        "auth.denied": "Security Events",
        "tool.error": "Tool Errors",
        "task.failed": "Failures",
    }

    def __init__(self, events: EventBus, observer: TinkleObserver) -> None:
        self.observer = observer
        self._events = events
        events.subscribe("*", self._handle)

    def _handle(self, event: Event) -> None:
        metric = self.EVENT_METRICS.get(event.type)
        if metric is None:
            return
        self.observer.observe(
            ObserverEventRequest(
                metric=metric,
                value=1.0,
                status="OBSERVED",
                source=f"event:{event.type}",
                details={"event_id": str(event.id)},
            )
        )


class IntegratedExecutionService:
    """End-to-end execution path: Meta-Mind -> Planner -> Agents -> Guardian.

    The service is deliberately explicit about provider failures. It never turns
    an unavailable model into a fabricated success.
    """

    def __init__(self, *, events: EventBus, memory: MemoryService, observer: TinkleObserver) -> None:
        self.events = events
        self.memory = memory
        self.observer = observer
        self.metamind = MetaMind()
        self.planner = Planner()
        self.multi_agent = MultiAgentSystem()
        self.guardian = Guardian()

    def execute(self, owner: str, prompt: str, permissions: set[Permission], *, context: dict[str, Any] | None = None) -> dict[str, Any]:
        if Permission.execute not in permissions and Permission.admin not in permissions:
            raise PermissionError("execute permission is required")
        started = perf_counter()
        context = dict(context or {})
        self.events.publish(Event(type="task.started", actor=owner, payload={"workflow": "metamind-planner-agents-guardian"}))
        memory_item = self.memory.write(owner=owner, memory_type=MemoryType.working, content=prompt, metadata={"source": "integrated.execution"})

        meta = self.metamind.plan(TaskRequest(prompt=prompt, context=context))
        planner_request = PlannerRequest(
            goal=meta.reframed_goal,
            context={**context, "tasks": [step.action for step in meta.steps]},
            resource_budget=context.get("resource_budget", {}),
            stop_conditions=meta.verification_strategy,
            retry_limit=int(context.get("retry_limit", 1)),
        )
        plan = self.planner.plan(planner_request)
        base_agent_context = {**context, "meta_mind": meta.model_dump(mode="json"), "plan": plan.model_dump(mode="json")}
        retry_limit = min(max(int(context.get("retry_limit", 1)), 0), 5)
        agent_context = dict(base_agent_context)
        attempts: list[dict[str, Any]] = []
        agent_result = self.multi_agent.run(AgentRequest(goal=meta.reframed_goal, context=agent_context))

        while True:
            evidence = []
            for agent in agent_result.agents:
                evidence.extend(agent.findings)
            if agent_result.synthesis:
                evidence.append(agent_result.synthesis)
            result_text = agent_result.synthesis or "No synthesis was produced."
            guardian = self.guardian.review(GuardianRequest(
                result=result_text, evidence=evidence,
                assumptions=[str(x) for x in context.get("assumptions", [])],
                known_limitations=[str(x) for x in context.get("known_limitations", [])],
            ))
            attempts.append({
                "attempt": len(attempts) + 1,
                "agent_status": agent_result.status,
                "guardian_conclusion": guardian.conclusion,
                "high_findings": [f.statement for f in guardian.findings if f.severity == "high"],
            })
            high_findings = [f for f in guardian.findings if f.severity == "high"]
            if not high_findings or len(attempts) > retry_limit or agent_result.status == "FAILED":
                break

            repair_feedback = "\n".join(
                f"- {f.category.value}: {f.statement} Basis: {f.basis}" for f in high_findings
            )
            agent_context = {
                **base_agent_context,
                "guardian_feedback": repair_feedback,
                "repair_attempt": len(attempts),
                "instruction": "Repair the previous result using Guardian findings. Do not merely explain the criticism; produce a revised result and explicitly address each finding.",
            }
            agent_result = self.multi_agent.run(
                AgentRequest(goal=meta.reframed_goal, context=agent_context)
            )

        status = "COMPLETED" if agent_result.status == "COMPLETED" and not any(f.severity == "high" for f in guardian.findings) else ("REVIEW_REQUIRED" if agent_result.status != "FAILED" else "FAILED")
        elapsed_ms = round((perf_counter() - started) * 1000, 3)
        self.observer.observe(ObserverEventRequest(metric="Latency", value=elapsed_ms, status="OBSERVED", source="integrated.execution", details={"status": status}))
        self.events.publish(Event(type="task.completed" if status != "FAILED" else "task.failed", actor=owner, payload={"workflow": "metamind-planner-agents-guardian", "status": status, "latency_ms": elapsed_ms}))
        return {
            "workflow": ["Meta-Mind", "Planner", "Multi-Agent", "Guardian"],
            "status": status,
            "memory_id": str(memory_item.id),
            "meta_mind": meta.model_dump(mode="json"),
            "plan": plan.model_dump(mode="json"),
            "multi_agent": agent_result.model_dump(mode="json"),
            "guardian": guardian.model_dump(mode="json"),
            "final_result": result_text,
            "guardian_iterations": attempts,
            "latency_ms": elapsed_ms,
            "limitations": [
                "A real final result requires at least one configured AI provider.",
                "Guardian reviews supplied output; it does not independently prove external truth.",
            ],
        }


class IntegrationCoordinator:
    """Phase 28 integration boundary for cross-component execution.

    The Blueprint names Full Integration but does not prescribe a new algorithm.
    This coordinator therefore wires existing capabilities together and proves
    the boundaries with a bounded, auditable smoke workflow rather than inventing
    new autonomous behavior.
    """

    def __init__(
        self,
        *,
        events: EventBus,
        router: ModelRouter,
        tools: ToolExecutor,
        memory: MemoryService,
        observer: TinkleObserver,
    ) -> None:
        self.events = events
        self.router = router
        self.tools = tools
        self.memory = memory
        self.observer = observer
        self.observer_bridge = ObserverEventBridge(events, observer)

    def status(self) -> dict[str, Any]:
        return {
            "phase": 28,
            "integrated_phases": [p.phase for p in PHASES],
            "components": [{"phase": p.phase, "name": p.name} for p in PHASES],
            "boundaries": {
                "model_router": True,
                "tool_executor": True,
                "memory": True,
                "event_bus": True,
                "observer_bridge": True,
                "privacy": "enforced by caller/API boundary",
                "external_providers": "only when explicitly configured",
                "sandbox": "sensitive execution remains gated",
            },
        }

    def smoke(self, owner: str, prompt: str, permissions: set[Permission]) -> dict[str, Any]:
        started = perf_counter()
        self.events.publish(Event(type="integration.started", actor=owner, payload={"phase": 28}))
        memory_item = self.memory.write(
            owner=owner,
            memory_type=MemoryType.working,
            content=prompt,
            metadata={"source": "phase28.integration"},
        )
        decision = self.router.route(
            RoutingRequest(
                prompt=prompt,
                task_type=TaskType.general,
                privacy=Privacy.public,
                context_tokens=1000,
            )
        )
        tool_result = self.tools.execute(
            ToolRequest(tool="calculator", input={"expression": "2+2"}),
            permissions,
        )
        elapsed_ms = round((perf_counter() - started) * 1000, 3)
        self.observer.observe(
            ObserverEventRequest(
                metric="Latency",
                value=elapsed_ms,
                status="OBSERVED",
                source="phase28.integration",
                details={"workflow": "memory->router->tool"},
            )
        )
        self.events.publish(Event(
            type="integration.completed",
            actor=owner,
            payload={"phase": 28, "latency_ms": elapsed_ms},
        ))
        return {
            "workflow": ["Memory", "Model Router", "Tool System", "Observer", "Event Bus"],
            "memory_id": str(memory_item.id),
            "selected_model": decision.selected_model,
            "tool": {"name": tool_result.tool, "ok": tool_result.ok, "output": tool_result.output},
            "latency_ms": elapsed_ms,
            "observer_total_events": self.observer.snapshot().total_events,
            "limitations": [
                "This smoke workflow validates concrete cross-component integration; it is not a claim that every domain engine executes automatically for every request.",
                "External providers remain optional and are not fabricated.",
                "Sensitive tools remain Sandbox-gated.",
            ],
        }

class FinalSystemOrchestrator:
    """Final cross-domain orchestration layer for the Blueprint capabilities added after Phase 28."""
    def __init__(self):
        from tinkle.advanced.engines import (InformationGainEngine,CrossDomainTransferEngine,CausalWorldModel,DigitalTwin,ResearchOrchestrator,ResearchRadar,MemoryEvolution,AttentionAllocator,ParallelDesignWorlds,AdversarialReality,ObserverHealth,ControlledImprovementRuntime,KnowledgeGraph,DreamMode,LongTermProjectRuntime,SecurityCapabilityMatrix)
        self.information_gain=InformationGainEngine(); self.cross_domain=CrossDomainTransferEngine(); self.causal=CausalWorldModel(); self.twin=DigitalTwin(); self.research=ResearchOrchestrator(); self.radar=ResearchRadar(); self.memory_evolution=MemoryEvolution(); self.attention=AttentionAllocator(); self.designs=ParallelDesignWorlds(); self.adversarial=AdversarialReality(); self.observer_health=ObserverHealth(); self.self_improvement=ControlledImprovementRuntime(); self.graph=KnowledgeGraph(); self.dream=DreamMode(); self.long_term=LongTermProjectRuntime(); self.security=SecurityCapabilityMatrix()
    def run(self, goal:str, *, resources:dict[str,float]|None=None)->dict[str,Any]:
        resources=resources or {"cpu":1.0,"ram":1.0,"time":1.0}
        plan=[{"name":"research","priority":1.0,"coverage":.8,"cost":1.0},{"name":"simulate","priority":.9,"coverage":.7,"cost":1.5},{"name":"verify","priority":1.0,"coverage":.9,"cost":1.0}]
        allocation=self.attention.allocate(resources,plan)
        gain=self.information_gain.rank_actions([],plan)
        self.graph.add_node(goal)
        return {"goal":goal,"information_gain":gain,"resource_allocation":allocation,"knowledge_graph_nodes":len(self.graph.nodes),"status":"ORCHESTRATED","epistemic_status":"HYPOTHESIS"}
