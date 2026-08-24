from fastapi import APIRouter, Depends
from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.digital_twin_engine import DigitalTwinEngine, DigitalTwinRequest
router=APIRouter(prefix='/api/v1/digital-twin',tags=['digital-twin'])
engine=DigitalTwinEngine()
@router.post('/run')
def run(req:DigitalTwinRequest,p:Principal=Depends(principal_from_key)):
    require(p,Permission.execute); return engine.run(req)
