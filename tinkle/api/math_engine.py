from fastapi import APIRouter, Depends

from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.math_engine import MathematicsEngine, MathRequest, MathResult

router = APIRouter(prefix="/api/v1/math", tags=["mathematics-engine"])
engine = MathematicsEngine()


@router.post("/calculate", response_model=MathResult)
def calculate(req: MathRequest, p: Principal = Depends(principal_from_key)):
    require(p, Permission.execute)
    return engine.calculate(req)
