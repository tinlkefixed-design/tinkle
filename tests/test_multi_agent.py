from tinkle.multi_agent import AgentRequest, AgentRole, MultiAgentSystem


def test_multi_agent_registers_all_blueprint_roles_independently():
    result = MultiAgentSystem().run(AgentRequest(goal="Solve a difficult problem"))
    assert len(result.agents) == 10
    assert result.roles == list(AgentRole)
    assert {agent.role for agent in result.agents} == set(AgentRole)
    assert result.status in {"FAILED", "PARTIAL", "COMPLETED"}
    assert all(agent.status in {"FAILED", "COMPLETED"} for agent in result.agents)


def test_multi_agent_accepts_selected_roles_and_deduplicates():
    req = AgentRequest(goal="Analyze", roles=[AgentRole.engineer, AgentRole.engineer, AgentRole.skeptic])
    result = MultiAgentSystem().run(req)
    assert [a.role for a in result.agents] == [AgentRole.engineer, AgentRole.skeptic]


def test_multi_agent_preserves_explicit_role_objectives():
    result = MultiAgentSystem().run(AgentRequest(goal="Build", roles=[AgentRole.programmer]))
    assert result.agents[0].objective == "programming and tool building"
    assert result.agents[0].status in {"FAILED", "COMPLETED"}

from tinkle.core.schemas import ProviderResponse


class FakeRuntime:
    def __init__(self):
        self.calls = []

    def generate(self, request):
        self.calls.append(request)
        return ProviderResponse(model_id="fake-model", provider="fake", text=f"answer:{request.prompt[:20]}")


def test_multi_agent_executes_roles_and_synthesizes():
    runtime = FakeRuntime()
    system = MultiAgentSystem(runtime=runtime)
    result = system.run(AgentRequest(goal="Analyze a system", roles=[AgentRole.scientist, AgentRole.skeptic]))
    assert result.status == "COMPLETED"
    assert all(agent.status == "COMPLETED" for agent in result.agents)
    assert result.synthesis and "answer:" in result.synthesis
    assert len(runtime.calls) == 3
    assert runtime.calls[0].task_type.value == "reasoning"


def test_multi_agent_reports_provider_failure_without_fake_findings():
    class BrokenRuntime:
        def generate(self, request):
            raise RuntimeError("provider offline")

    result = MultiAgentSystem(runtime=BrokenRuntime()).run(
        AgentRequest(goal="Analyze", roles=[AgentRole.engineer])
    )
    assert result.status == "FAILED"
    assert result.agents[0].status == "FAILED"
    assert result.agents[0].findings == []
    assert "provider offline" in result.agents[0].error
