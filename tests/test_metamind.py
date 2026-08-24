from tinkle.metamind.orchestrator import MetaMind
from tinkle.metamind.schemas import TaskRequest, TaskType

def test_coding_classification():
    p=MetaMind().plan(TaskRequest(prompt="write python code to parse a CSV"))
    assert p.task_type==TaskType.coding
    assert "code_execution" in p.tool_strategy

def test_research_plan():
    p=MetaMind().plan(TaskRequest(prompt="research the latest papers on fusion"))
    assert p.task_type==TaskType.research
    assert "search" in p.tool_strategy
    assert "verify" in [x.action for x in p.steps]

def test_reasoning_plan():
    p=MetaMind().plan(TaskRequest(prompt="solve the equation 2*x+1=9"))
    assert p.task_type==TaskType.reasoning
    assert p.model_strategy=="prefer_reasoning_capability"

def test_plan_has_full_lifecycle():
    actions=[x.action for x in MetaMind().plan(TaskRequest(prompt="analyze this problem")).steps]
    assert actions==["understand","classify","reframe","select_model","select_tools","execute","verify","synthesize"]
