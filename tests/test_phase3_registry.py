import pytest
from tinkle.core.schemas import Permission, ToolSpec, ToolRequest
from tinkle.tools.registry import Tool, ToolRegistry
from tinkle.tools.builtins import register_builtin_tools
from tinkle.tools.executor import ToolExecutor

def test_registry_has_required_tools():
    r=ToolRegistry(); register_builtin_tools(r)
    names={x.name for x in r.list()}
    assert {"calculator","python","search","web_retrieval","file_reader","document_reader",
            "code_execution","visualization","data_analysis","math","file_processing",
            "scientific_tools"} <= names

def test_calculator():
    r=ToolRegistry(); register_builtin_tools(r)
    out=ToolExecutor(r).execute(ToolRequest(tool="calculator",input={"expression":"2+3*4"}), set(Permission))
    assert out.ok and out.output["value"] == 14

def test_calculator_rejects_code():
    r=ToolRegistry(); register_builtin_tools(r)
    out=ToolExecutor(r).execute(ToolRequest(tool="calculator",input={"expression":"__import__('os')"}), set(Permission))
    assert not out.ok

def test_sensitive_execution_uses_sandbox():
    r=ToolRegistry(); register_builtin_tools(r)
    out=ToolExecutor(r).execute(ToolRequest(tool="python",input={"code":"print(1)"}), set(Permission))
    assert out.ok and out.output["stdout"].strip() == "1"

def test_sandbox_rejects_restricted_files():
    r=ToolRegistry(); register_builtin_tools(r)
    out=ToolExecutor(r).execute(ToolRequest(tool="python",input={"code":"open('/etc/passwd').read()"}), set(Permission))
    assert not out.ok

def test_duplicate_rejected():
    r=ToolRegistry()
    spec=ToolSpec(name="x",description="x",input_schema={},output_schema={},
                  permissions={Permission.execute},timeout_ms=1,cpu_limit_ms=1,memory_limit_mb=1)
    r.register(Tool(spec, lambda x:x))
    with pytest.raises(ValueError): r.register(Tool(spec, lambda x:x))
