from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.math_engine import EquationDiscoveryEngine

router=APIRouter(prefix="/api/v1/math-discovery", tags=["mathematical-law-discovery"])
engine=EquationDiscoveryEngine()
class DiscoveryRequest(BaseModel):
    rows:list[dict[str,float]]=Field(min_length=6,max_length=50000)
    target:str=Field(min_length=1,max_length=128)
    variables:list[str]|None=None
    units:dict[str,str]={}
    top_k:int=Field(default=10,ge=1,le=50)
    seed:int=0
class ODERequest(BaseModel):
    times:list[float]=Field(min_length=8,max_length=50000)
    series:list[float]=Field(min_length=8,max_length=50000)
    max_degree:int=Field(default=3,ge=1,le=8)
@router.post("/symbolic-regression")
def symbolic(req:DiscoveryRequest,p:Principal=Depends(principal_from_key)):
    require(p,Permission.execute)
    try:return {"status":"CANDIDATE","models":engine.symbolic_regression(**req.model_dump())}
    except ValueError as exc: raise HTTPException(422,str(exc)) from exc
@router.post("/differential-equation")
def differential(req:ODERequest,p:Principal=Depends(principal_from_key)):
    require(p,Permission.execute)
    try:return {"status":"CANDIDATE","models":engine.differential_equation_discovery(**req.model_dump())}
    except ValueError as exc: raise HTTPException(422,str(exc)) from exc
