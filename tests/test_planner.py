from tinkle.planner.engine import Planner
from tinkle.planner.schemas import PlannerRequest


def test_planner_decomposes_goal_with_required_control_fields():
    result = Planner().plan(PlannerRequest(goal="Build a verified solution"))
    assert [t.name for t in result.tasks] == ["TASK A", "TASK B", "TASK C", "TASK D"]
    assert result.tasks[1].dependencies == ["TASK_1"]
    assert result.verification.name == "VERIFICATION"
    assert result.final_result.dependencies == ["VERIFICATION"]
    assert result.retry_policy["default_retry_limit"] == 1
    assert result.recovery_policy["on_exhaustion"] == "STOP_AND_REPORT"


def test_planner_accepts_explicit_tasks_and_budgets():
    req = PlannerRequest(
        goal="Ship feature",
        context={"tasks": ["Design", "Implement"], "resource_budgets": {"Design": {"minutes": 10}}},
        resource_budget={"minutes": 30},
        stop_conditions=["Stop if safety gate fails"],
        retry_limit=2,
    )
    result = Planner().plan(req)
    assert result.tasks[0].name == "Design"
    assert result.tasks[0].resource_budget == {"minutes": 10}
    assert result.verification.stop_conditions == ["Stop if safety gate fails"]
    assert result.final_result.retry_limit == 2


def test_compiler_to_planner_integration():
    from tinkle.compiler import CognitiveCompiler
    from tinkle.compiler_schemas import CognitiveCompileRequest

    compiled = CognitiveCompiler().compile(CognitiveCompileRequest(problem="x = 10, solve x"))
    result = Planner().plan(PlannerRequest(goal=compiled.structured_problem.objective))
    assert result.goal.startswith("Solve the")
    assert result.status == "PLANNED"
    assert result.verification.dependencies == ["TASK_1", "TASK_2", "TASK_3", "TASK_4"]
