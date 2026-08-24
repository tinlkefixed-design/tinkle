from fastapi import APIRouter, Depends
from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.prototype_engine import PrototypeEngine
from tinkle.prototype_engine.schemas import PrototypeRequest, PrototypeLevel
router=APIRouter(prefix='/api/v1/prototypes',tags=['prototypes'])
engine=PrototypeEngine()
@router.post('/plan')
def plan(req:PrototypeRequest, level:PrototypeLevel=PrototypeLevel.LOW_FIDELITY,p:Principal=Depends(principal_from_key)):
    require(p,Permission.execute); return engine.plan(req,level)
