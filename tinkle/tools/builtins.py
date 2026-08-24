import ast, json, math
from pathlib import Path
from typing import Any
from tinkle.core.schemas import Permission, ToolSpec
from tinkle.sandbox.runner import SandboxRunner
from tinkle.knowledge.ingestion import DocumentIngestor
from tinkle.knowledge.retrieval import BM25Index
from tinkle.research_engine.web_provider import DuckDuckGoSearchProvider
from .registry import Tool, ToolRegistry

_SANDBOX = SandboxRunner()
_INGESTOR = DocumentIngestor()
_SEARCH = DuckDuckGoSearchProvider()

def calculator(data: dict[str, Any]) -> dict[str, Any]:
    expr = str(data.get("expression", ""))
    if len(expr) > 200: raise ValueError("expression too long")
    tree = ast.parse(expr, mode="eval")
    allowed=(ast.Expression,ast.BinOp,ast.UnaryOp,ast.Add,ast.Sub,ast.Mult,ast.Div,ast.Pow,ast.Mod,ast.USub,ast.UAdd,ast.Constant)
    if not all(isinstance(n,allowed) for n in ast.walk(tree)): raise ValueError("unsupported expression")
    return {"value": eval(compile(tree,"<calculator>","eval"),{"__builtins__":{}},{})}

def python_exec(data):
    result=_SANDBOX.run_python(str(data.get("code","")),inputs=data.get("inputs") or {})
    if not result.ok:
        raise RuntimeError(result.error or "Sandbox execution failed")
    return result.__dict__

def search(data):
    q=str(data.get("query","")).strip(); k=max(1,min(int(data.get("top_k",5)),10))
    if not q: raise ValueError("query is required")
    return {"results":[r.model_dump() if hasattr(r,"model_dump") else r for r in _SEARCH(q,k)]}

def web_retrieval(data): return search(data)

def file_reader(data):
    p=Path(str(data.get("path","")).strip()).expanduser().resolve()
    root=Path.cwd().resolve()
    if root not in p.parents and p!=root: raise PermissionError("file path outside workspace")
    if not p.is_file(): raise FileNotFoundError(str(p))
    if p.stat().st_size>2*1024*1024: raise ValueError("file too large")
    return {"path":str(p),"content":p.read_text(encoding="utf-8",errors="replace")}

def document_reader(data):
    doc=_INGESTOR.ingest_path(str(data.get("path","")),metadata=data.get("metadata") or {})
    return doc.model_dump()

def data_analysis(data):
    values=[float(x) for x in data.get("values",[])]
    if not values: raise ValueError("values required")
    mean=sum(values)/len(values); variance=sum((x-mean)**2 for x in values)/len(values)
    return {"count":len(values),"mean":mean,"variance":variance,"min":min(values),"max":max(values)}

def math_tool(data):
    from sympy import sympify, N
    expr=str(data.get("expression","")); obj=sympify(expr)
    return {"expression":expr,"exact":str(obj),"numeric":str(N(obj,16))}

def visualization(data):
    series=data.get("series",[])
    if not isinstance(series,list): raise ValueError("series must be a list")
    return {"type":data.get("type","line"),"series":series,"interactive":True}

def file_processing(data):
    p=Path(str(data.get("path",""))).expanduser().resolve()
    if not p.is_file(): raise FileNotFoundError(str(p))
    return _INGESTOR.ingest_path(p).model_dump()

def scientific_tools(data):
    from tinkle.science_engine.engine import ScienceEngine
    from tinkle.science_engine.schemas import ScienceSolveRequest
    return ScienceEngine().solve(ScienceSolveRequest(**data)).model_dump()

def code_execution(data): return python_exec(data)

def register_builtin_tools(registry: ToolRegistry) -> None:
    handlers={
      "calculator":calculator,"python":python_exec,"search":search,"web_retrieval":web_retrieval,
      "file_reader":file_reader,"document_reader":document_reader,"code_execution":code_execution,
      "visualization":visualization,"data_analysis":data_analysis,"math":math_tool,"file_processing":file_processing,
      "scientific_tools":scientific_tools,
    }
    for name,handler in handlers.items():
        sensitive=name in {"python","code_execution","scientific_tools"}
        registry.register(Tool(ToolSpec(name=name,description=f"Tinkle {name} tool",input_schema={"type":"object"},output_schema={"type":"object"},permissions={Permission.execute},timeout_ms=10000,cpu_limit_ms=2000,memory_limit_mb=256,audit_log=True,requires_sandbox=sensitive),handler))
