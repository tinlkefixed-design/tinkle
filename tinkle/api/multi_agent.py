from fastapi import APIRouter, Depends
from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.multi_agent import AgentRequest, MultiAgentResult, MultiAgentSystem

router = APIRouter(prefix="/api/v1/multi-agent", tags=["multi-agent"])
system = MultiAgentSystem()


@router.post("/run", response_model=MultiAgentResult)
def run_multi_agent(req: AgentRequest, p: Principal = Depends(principal_from_key)):
    require(p, Permission.execute)
    return system.run(req)
