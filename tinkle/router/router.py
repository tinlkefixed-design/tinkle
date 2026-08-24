from tinkle.core.errors import NoCompatibleModelError
from tinkle.core.schemas import ModelProfile, Privacy, RoutingDecision, RoutingRequest, TaskType
from tinkle.core.events import RouterAudit

class ModelRouter:
    def __init__(self, catalog: list[ModelProfile], audit: RouterAudit | None = None):
        self.catalog = catalog
        self.audit = audit or RouterAudit()

    def route(self, request: RoutingRequest) -> RoutingDecision:
        candidates: list[tuple[float, ModelProfile, list[str]]] = []
        for model in self.catalog:
            if request.privacy == Privacy.private and not model.local:
                continue
            if request.context_tokens > model.capabilities.context_size:
                continue
            if request.max_cost_per_1k_tokens is not None and model.cost_per_1k_tokens > request.max_cost_per_1k_tokens:
                continue
            if request.max_latency_ms is not None and model.latency_ms > request.max_latency_ms:
                continue
            if request.require_reasoning and model.capabilities.reasoning < .70:
                continue
            if request.require_coding and model.capabilities.coding < .70:
                continue
            if request.require_vision and model.capabilities.vision < .70:
                continue
            if request.require_tool_use and model.capabilities.tool_use < .70:
                continue

            score, reasons = self._score(request, model)
            candidates.append((score, model, reasons))

        if not candidates:
            raise NoCompatibleModelError("No model satisfies the requested constraints")

        candidates.sort(key=lambda x: (-x[0], x[1].id))
        score, selected, reasons = candidates[0]
        decision = RoutingDecision(
            selected_model=selected.id,
            provider=selected.provider,
            score=round(score, 4),
            reasons=reasons,
            fallback_models=[m.id for _, m, _ in candidates[1:]],
            policy="constraint-filter + weighted capability/cost/latency scoring",
        )
        self.audit.record(decision)
        return decision

    def _score(self, r: RoutingRequest, m: ModelProfile) -> tuple[float, list[str]]:
        reasons: list[str] = []
        score = 0.0

        if r.task_type == TaskType.simple:
            score += (1 - m.latency_ms / 1000) * .35
            score += (1 - m.cost_per_1k_tokens / .02) * .25
            reasons.append("simple task favors speed and low cost")
        elif r.task_type == TaskType.reasoning:
            score += m.capabilities.reasoning * .55
            reasons.append("reasoning capability prioritized")
        elif r.task_type == TaskType.coding:
            score += m.capabilities.coding * .55
            reasons.append("coding capability prioritized")
        elif r.task_type == TaskType.research:
            score += m.capabilities.tool_use * .25 + m.capabilities.reasoning * .35
            reasons.append("research favors reasoning and tool use")
        elif r.task_type == TaskType.math:
            score += m.capabilities.reasoning * .55
            reasons.append("math favors reasoning capability")
        elif r.task_type == TaskType.vision:
            score += m.capabilities.vision * .65
            reasons.append("vision capability prioritized")
        else:
            score += m.capabilities.reasoning * .20 + m.capabilities.tool_use * .20

        score += min(m.capabilities.context_size / max(r.context_tokens, 1), 10) * .01
        score += m.capabilities.reasoning * r.difficulty * .25
        if r.privacy == Privacy.private and m.local:
            score += .50
            reasons.append("private data favors local execution")
        return score, reasons
