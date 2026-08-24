from fastapi import APIRouter, Depends, HTTPException
from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.ergonomics_engine import ErgonomicsEngine, ErgonomicsRequest, ErgonomicsResult
router=APIRouter(prefix='/api/v1/ergonomics',tags=['ergonomics'])
engine=ErgonomicsEngine()
@router.post('/analyze',response_model=ErgonomicsResult)
def analyze(req:ErgonomicsRequest,p:Principal=Depends(principal_from_key)):
    require(p,Permission.execute)
    try:return engine.analyze(req)
    except ValueError as exc:raise HTTPException(422,str(exc)) from exc
