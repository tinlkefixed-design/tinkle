from fastapi import APIRouter, Depends
from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.adversarial_science import AttackRequest, AdversarialResult, AdversarialScienceEngine
router=APIRouter(prefix='/api/v1/adversarial-science',tags=['adversarial-science'])
engine=AdversarialScienceEngine()
@router.post('/attack',response_model=AdversarialResult)
def attack(req:AttackRequest,p:Principal=Depends(principal_from_key)):
    require(p,Permission.execute); return engine.attack(req)
