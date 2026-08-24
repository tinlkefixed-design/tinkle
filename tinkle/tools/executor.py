import json,time
from tinkle.core.errors import ToolExecutionError
from tinkle.core.events import EventBus
from tinkle.core.schemas import Event, ToolRequest, ToolResult
from tinkle.security.policy import SecurityPolicy
from tinkle.sandbox.runner import SandboxRunner
from .registry import ToolRegistry

class ToolExecutor:
    def __init__(self,registry:ToolRegistry,events:EventBus|None=None,policy:SecurityPolicy|None=None):
        self.registry=registry; self.audit=[]; self.events=events; self.policy=policy or SecurityPolicy(); self.sandbox=SandboxRunner()
    def execute(self,request:ToolRequest,permissions)->ToolResult:
        start=time.perf_counter(); tool_name=request.tool
        try:
            if len(json.dumps(request.input,ensure_ascii=False,default=str).encode())>self.policy.max_tool_input_bytes: raise ToolExecutionError("Tool input exceeds the security size limit")
            tool=self.registry.require(tool_name,permissions)
            if tool.spec.requires_sandbox and self.policy.require_sandbox_for_sensitive_tools and tool_name in {"python","code_execution"}:
                output=tool.handler(request.input)
            else:
                output=tool.handler(request.input)
            result=ToolResult(tool=tool_name,ok=True,output=output,duration_ms=(time.perf_counter()-start)*1000)
        except Exception as exc:
            result=ToolResult(tool=tool_name,ok=False,error=str(exc),duration_ms=(time.perf_counter()-start)*1000)
        self.audit.append(result)
        if self.events:
            self.events.publish(Event(type="tool.executed" if result.ok else "tool.denied",actor="tool_executor",payload={"tool":tool_name,"ok":result.ok,"duration_ms":round(result.duration_ms,3)}))
        return result
