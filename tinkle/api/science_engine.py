from fastapi import APIRouter, Depends

from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.science_engine import ScienceEngine, ScienceRequest, ScienceResult, ScienceSolveRequest

router = APIRouter(prefix="/api/v1/science", tags=["science-engine"])
engine = ScienceEngine()


@router.post("/inspect", response_model=ScienceResult)
def inspect(req: ScienceRequest, p: Principal = Depends(principal_from_key)):
    require(p, Permission.execute)
    return engine.inspect(req)


@router.post("/solve", response_model=ScienceResult)
def solve(req: ScienceSolveRequest, p: Principal = Depends(principal_from_key)):
    require(p, Permission.execute)
    return engine.solve(req)


@router.get("/modules")
def modules(p: Principal = Depends(principal_from_key)):
    require(p, Permission.read)
    return {"modules": engine.modules()}
