from fastapi import APIRouter, Depends
from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.failure_atlas import FailureAtlas, FailureAtlasRequest, FailureAtlasResult

router = APIRouter(prefix="/api/v1/failure-atlas", tags=["failure-atlas"])
system = FailureAtlas()


@router.post("/record", response_model=FailureAtlasResult)
def record(req: FailureAtlasRequest, p: Principal = Depends(principal_from_key)):
    require(p, Permission.write)
    return system.record(req)
