from fastapi import APIRouter, Depends
from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.cross_domain_engine import CrossDomainInnovationEngine, CrossDomainRequest, CrossDomainResult
router=APIRouter(prefix='/api/v1/cross-domain',tags=['cross-domain-innovation'])
system=CrossDomainInnovationEngine()
@router.post('/generate',response_model=CrossDomainResult)
def generate(req:CrossDomainRequest,p:Principal=Depends(principal_from_key)):
    require(p,Permission.execute); return system.generate(req)
