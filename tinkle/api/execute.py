from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from tinkle.api.deps import principal_from_key, require
from tinkle.api.main import integrated_execution
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission

router = APIRouter(prefix="/api/v1/execute", tags=["execution"])

class ExecuteRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=20000)
    context: dict = {}

@router.post("", response_model=dict)
def execute(req: ExecuteRequest, p: Principal = Depends(principal_from_key)):
    require(p, Permission.execute)
    return integrated_execution.execute(p.name, req.prompt, set(p.permissions), context=req.context)
