from fastapi import APIRouter, Depends
from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.discovery_engine import DiscoveryEngine, DiscoveryRequest, DiscoveryResult

router = APIRouter(prefix='/api/v1/discovery', tags=['discovery-engine'])
system = DiscoveryEngine()

@router.post('/discover', response_model=DiscoveryResult)
def discover(req: DiscoveryRequest, p: Principal = Depends(principal_from_key)):
    require(p, Permission.execute)
    return system.discover(req)
