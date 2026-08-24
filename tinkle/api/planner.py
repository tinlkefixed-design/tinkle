from fastapi import APIRouter, Depends
from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.planner.engine import Planner
from tinkle.planner.schemas import PlannerRequest, PlannerResult

router = APIRouter(prefix="/api/v1/planner", tags=["planner"])
planner = Planner()


@router.post("/plan", response_model=PlannerResult)
def create_plan(req: PlannerRequest, p: Principal = Depends(principal_from_key)):
    require(p, Permission.execute)
    return planner.plan(req)
