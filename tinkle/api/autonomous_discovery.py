from fastapi import APIRouter, Depends
from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.autonomous_discovery import AutonomousDiscoveryEngine, MissionRequest, DiscoveryRun
router=APIRouter(prefix='/api/v1/autonomous-discovery',tags=['autonomous-discovery'])
engine=AutonomousDiscoveryEngine()
@router.post('/run',response_model=DiscoveryRun)
def run(req:MissionRequest,p:Principal=Depends(principal_from_key)):
    require(p,Permission.execute); return engine.run(req)
