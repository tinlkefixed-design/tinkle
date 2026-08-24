from tinkle.metamind.classifier import TaskClassifier
from tinkle.metamind.schemas import MetaMindPlan, PlanStep, TaskRequest, TaskType

class MetaMindPlanner:
    def __init__(self):
        self.classifier = TaskClassifier()

    def plan(self, request: TaskRequest) -> MetaMindPlan:
        t = self.classifier.classify(request.prompt)
        goal = request.prompt.strip()
        steps = [
            PlanStep(action="understand", reason="Parse the user's objective and constraints"),
            PlanStep(action="classify", reason=f"Classify task as {t.value}", dependencies=["understand"]),
            PlanStep(action="reframe", reason="Turn the request into an explicit verifiable goal", dependencies=["classify"]),
            PlanStep(action="select_model", reason="Delegate model choice to the Model Router", dependencies=["reframe"]),
            PlanStep(action="select_tools", reason="Select only tools required by the plan", dependencies=["reframe"]),
            PlanStep(action="execute", reason="Execute planned work through available components", dependencies=["select_model","select_tools"]),
            PlanStep(action="verify", reason="Check outputs against constraints and evidence", dependencies=["execute"]),
            PlanStep(action="synthesize", reason="Produce the final coherent result", dependencies=["verify"]),
        ]
        model_strategy = {
            TaskType.simple:"prefer_fast_low_cost",
            TaskType.reasoning:"prefer_reasoning_capability",
            TaskType.research:"prefer_research_and_evidence",
            TaskType.coding:"prefer_coding_capability",
            TaskType.data_analysis:"prefer_data_analysis_capability",
            TaskType.scientific:"prefer_reasoning_and_scientific_tools",
            TaskType.creative:"prefer_generation_capability",
        }.get(t, "router_decides")
        tool_strategy = {
            TaskType.reasoning:["calculator"],
            TaskType.research:["search","web_retrieval","knowledge"],
            TaskType.coding:["code_execution"],
            TaskType.data_analysis:["data_analysis","file_reader"],
            TaskType.scientific:["scientific_tools","calculator"],
        }.get(t, [])
        verification = ["check completion", "check constraints", "check evidence when applicable"]
        return MetaMindPlan(
            prompt=request.prompt, task_type=t, reframed_goal=goal,
            constraints=list(request.context.get("constraints", [])),
            steps=steps, model_strategy=model_strategy,
            tool_strategy=tool_strategy, verification_strategy=verification
        )
