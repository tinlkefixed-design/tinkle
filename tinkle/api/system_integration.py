from fastapi import APIRouter, Depends

from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.system_integration import SystemIntegrationEngine

router=APIRouter(prefix='/api/v1/system',tags=['system-integration']); engine=SystemIntegrationEngine()
@router.get('/health')
def health(p:Principal=Depends(principal_from_key)): # noqa: B008
    require(p,Permission.read);return engine.health()
@router.get('/capabilities')
def capabilities(p:Principal=Depends(principal_from_key)): # noqa: B008
    require(p,Permission.read);return engine.capabilities()
@router.get('/integrity')
def integrity(p:Principal=Depends(principal_from_key)): # noqa: B008
    require(p,Permission.read);return engine.integrity()
@router.get('/reproducibility')
def reproducibility(p:Principal=Depends(principal_from_key)): # noqa: B008
    require(p,Permission.read);return engine.reproducibility()
@router.get('/readiness')
def readiness(p:Principal=Depends(principal_from_key)): # noqa: B008
    require(p,Permission.read);return engine.readiness()
@router.get('/history')
def history(p:Principal=Depends(principal_from_key)): # noqa: B008
    require(p,Permission.read);return engine.history()
