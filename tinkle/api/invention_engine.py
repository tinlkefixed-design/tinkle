from fastapi import APIRouter, Depends
from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.invention_engine import InventionGenerationEngine, InventionRequest, InventionResult
router=APIRouter(prefix='/api/v1/inventions',tags=['invention-engine'])
system=InventionGenerationEngine()
@router.post('/generate',response_model=InventionResult)
def generate(req:InventionRequest,p:Principal=Depends(principal_from_key)):
    require(p,Permission.execute); return system.generate(req)
