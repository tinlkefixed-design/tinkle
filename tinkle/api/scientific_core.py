from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.scientific_core import ScientificCore

router=APIRouter(prefix='/api/v1/scientific-core',tags=['scientific-core'])
core=ScientificCore()
class FormalizeRequest(BaseModel):
    prompt:str=Field(min_length=1,max_length=20000)
    context:dict=dict
@router.post('/formalize')
def formalize(req:FormalizeRequest,p:Principal=Depends(principal_from_key)):
    require(p,Permission.execute)
    try:
        problem,graph=core.formalize(req.prompt,req.context)
        return {'problem':problem,'graph':graph}
    except ValueError as exc: raise HTTPException(422,str(exc)) from exc
