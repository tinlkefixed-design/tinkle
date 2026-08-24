from __future__ import annotations
from tinkle.planner.schemas import PlannerPriority, PlannerRequest, PlannerResult, PlannerTask


class Planner:
    """Phase 10 Planner: deterministic decomposition with explicit control policies."""

    def plan(self, request: PlannerRequest) -> PlannerResult:
        tasks = list(request.tasks) if request.tasks else self._decompose(request.goal, request.context)
        self._validate_dependencies(tasks)

        verification = PlannerTask(
            id="VERIFICATION",
            name="VERIFICATION",
            objective=f"Verify completion of the goal: {request.goal.strip()}",
            dependencies=[task.id for task in tasks],
            priority=PlannerPriority.high,
            resource_budget=request.resource_budget,
            stop_conditions=request.stop_conditions or ["Stop when all planned tasks pass verification."],
            retry_limit=request.retry_limit,
            recovery=["Retry failed verification within the retry limit; otherwise stop and report failure."],
        )
        final = PlannerTask(
            id="FINAL_RESULT",
            name="FINAL RESULT",
            objective=f"Produce the final result for: {request.goal.strip()}",
            dependencies=[verification.id],
            priority=PlannerPriority.critical,
            resource_budget=request.resource_budget,
            stop_conditions=request.stop_conditions or ["Stop when the verified final result is produced."],
            retry_limit=request.retry_limit,
            recovery=["Return the verified result or an explicit failure state; never claim success without verification."],
        )
        dependencies = {task.id: list(task.dependencies) for task in tasks}
        dependencies[verification.id] = list(verification.dependencies)
        dependencies[final.id] = list(final.dependencies)
        priorities = {task.id: task.priority for task in tasks}
        priorities[verification.id] = verification.priority
        priorities[final.id] = final.priority
        budgets = {task.id: dict(task.resource_budget) for task in tasks}
        budgets[verification.id] = dict(verification.resource_budget)
        budgets[final.id] = dict(final.resource_budget)
        return PlannerResult(
            goal=request.goal.strip(),
            tasks=tasks,
            verification=verification,
            final_result=final,
            dependencies=dependencies,
            priorities=priorities,
            resource_budgets=budgets,
            stop_conditions=request.stop_conditions,
            retry_policy={"default_retry_limit": request.retry_limit, "strategy": "bounded"},
            recovery_policy={"strategy": "explicit", "on_exhaustion": "STOP_AND_REPORT"},
        )

    def _decompose(self, goal: str, context: dict) -> list[PlannerTask]:
        candidates = context.get("tasks") if isinstance(context, dict) else None
        if isinstance(candidates, list) and candidates:
            names = [str(item).strip() for item in candidates if str(item).strip()]
        else:
            names = ["TASK A", "TASK B", "TASK C", "TASK D"]
        tasks: list[PlannerTask] = []
        previous: list[str] = []
        for index, name in enumerate(names[:20], start=1):
            task_id = f"TASK_{index}"
            task = PlannerTask(
                id=task_id,
                name=name,
                objective=f"Complete {name} as a necessary part of: {goal.strip()}",
                dependencies=list(previous),
                priority=PlannerPriority.high if index == 1 else PlannerPriority.normal,
                resource_budget=dict(context.get("resource_budgets", {}).get(name, {})) if isinstance(context.get("resource_budgets", {}), dict) else {},
                stop_conditions=[f"Stop {name} when its acceptance condition is satisfied."],
                retry_limit=int(context.get("retry_limit", 0)) if str(context.get("retry_limit", "0")).isdigit() else 0,
                recovery=[f"Retry {name} using its available recovery path; otherwise mark it failed."],
            )
            tasks.append(task)
            previous.append(task_id)
        return tasks

    @staticmethod
    def _validate_dependencies(tasks: list[PlannerTask]) -> None:
        ids = {task.id for task in tasks}
        for task in tasks:
            unknown = [dep for dep in task.dependencies if dep not in ids]
            if unknown:
                raise ValueError(f"Unknown task dependencies: {unknown}")
            if task.id in task.dependencies:
                raise ValueError(f"Task cannot depend on itself: {task.id}")
