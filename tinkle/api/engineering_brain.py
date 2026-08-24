from fastapi import APIRouter, Depends
from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.engineering_brain import EngineeringBrain, EngineeringBrainRequest, EngineeringBrainResult
router=APIRouter(prefix='/api/v1/engineering-brain', tags=['engineering-brain'])
engine=EngineeringBrain()
@router.post('/analyze', response_model=EngineeringBrainResult)
def analyze(req: EngineeringBrainRequest, p: Principal=Depends(principal_from_key)):
    require(p, Permission.execute)
    return engine.analyze(req)
