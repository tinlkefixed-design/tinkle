from fastapi import APIRouter, Depends
from tinkle.api.deps import principal_from_key,require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.cad_engine import CADEngine,CADAssemblyRequest
router=APIRouter(prefix='/api/v1/cad',tags=['advanced-cad'])
engine=CADEngine()
@router.post('/assembly')
def assembly(req:CADAssemblyRequest,p:Principal=Depends(principal_from_key)):
    require(p,Permission.execute);return engine.build(req).model_dump()
