from fastapi import APIRouter, Depends

from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.engineering_engine import EngineeringEngine, EngineeringRequest, EngineeringResult, EngineeringSolveRequest

router = APIRouter(prefix="/api/v1/engineering", tags=["engineering-engine"])
engine = EngineeringEngine()


@router.post("/inspect", response_model=EngineeringResult)
def inspect(req: EngineeringRequest, p: Principal = Depends(principal_from_key)):
    require(p, Permission.execute)
    return engine.inspect(req)


@router.post("/solve", response_model=EngineeringResult)
def solve(req: EngineeringSolveRequest, p: Principal = Depends(principal_from_key)):
    require(p, Permission.execute)
    return engine.solve(req)


@router.get("/modules")
def modules(p: Principal = Depends(principal_from_key)):
    require(p, Permission.read)
    return {"modules": engine.modules()}
