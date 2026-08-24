from fastapi import APIRouter, Depends
from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.guardian import Guardian, GuardianRequest, GuardianResult

router = APIRouter(prefix="/api/v1/guardian", tags=["guardian"])
system = Guardian()


@router.post("/review", response_model=GuardianResult)
def review(req: GuardianRequest, p: Principal = Depends(principal_from_key)):
    require(p, Permission.execute)
    return system.review(req)
