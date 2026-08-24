from fastapi import APIRouter, Depends, HTTPException
import numpy as np
from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.cae_engine import CAEEngine, CAERequest
router=APIRouter(prefix='/api/v1/cae',tags=['cae'])
engine=CAEEngine()
@router.post('/analyze')
def analyze(req: CAERequest,p:Principal=Depends(principal_from_key)):
    require(p,Permission.execute)
    try:return engine.run(req).model_dump()
    except (ValueError,np.linalg.LinAlgError) as exc: raise HTTPException(422,str(exc)) from exc
