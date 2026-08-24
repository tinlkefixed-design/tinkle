from tinkle.metamind.planner import MetaMindPlanner
from tinkle.metamind.schemas import TaskRequest, MetaMindPlan

class MetaMind:
    def __init__(self):
        self.planner = MetaMindPlanner()

    def plan(self, request: TaskRequest) -> MetaMindPlan:
        return self.planner.plan(request)

    def route_hint(self, plan: MetaMindPlan) -> dict:
        return {
            "task_type": plan.task_type.value,
            "model_strategy": plan.model_strategy,
            "tool_strategy": plan.tool_strategy,
            "verification_strategy": plan.verification_strategy,
        }
