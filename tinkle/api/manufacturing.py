from fastapi import APIRouter, Depends
from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.manufacturing_engine import ManufacturingEngine, ManufacturingRequest
router=APIRouter(prefix='/api/v1/manufacturing',tags=['manufacturing'])
engine=ManufacturingEngine()
@router.post('/plan')
def plan(req:ManufacturingRequest,p:Principal=Depends(principal_from_key)):
    require(p,Permission.execute); return engine.plan(req)
