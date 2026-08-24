from fastapi import APIRouter, Depends
from tinkle.api.deps import principal_from_key, require
from tinkle.compiler import CognitiveCompiler
from tinkle.compiler_schemas import CognitiveCompileRequest, CognitiveCompileResult
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission

router = APIRouter(prefix="/api/v1/compiler", tags=["cognitive-compiler"])
compiler = CognitiveCompiler()

@router.post("/compile", response_model=CognitiveCompileResult)
def compile_problem(req: CognitiveCompileRequest, p: Principal = Depends(principal_from_key)):
    require(p, Permission.execute)
    return compiler.compile(req)
