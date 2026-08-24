from fastapi import APIRouter, Depends
from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.hypothesis_universe import HypothesisUniverse, HypothesisRequest, HypothesisResult

router = APIRouter(prefix="/api/v1/hypothesis-universe", tags=["hypothesis-universe"])
system = HypothesisUniverse()

@router.post("/run", response_model=HypothesisResult)
def run(req: HypothesisRequest, p: Principal = Depends(principal_from_key)):
    require(p, Permission.execute)
    return system.run(req)
