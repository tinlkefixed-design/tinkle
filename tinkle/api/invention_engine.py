from fastapi import APIRouter, Depends, HTTPException

from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.invention_engine import (
    InventionAnalysis,
    InventionGenerationEngine,
    InventionRequest,
    InventionResult,
)

router=APIRouter(prefix='/api/v1/inventions',tags=['invention-engine'])
system=InventionGenerationEngine()
@router.post('/generate',response_model=InventionResult)
def generate(req:InventionRequest,p:Principal=Depends(principal_from_key)):
    require(p,Permission.execute); return system.generate(req)

@router.post('/analyze', response_model=InventionAnalysis)
def analyze(req:InventionRequest,p:Principal=Depends(principal_from_key)):
    require(p,Permission.execute)
    return system.analyze_invention_goal(req)

def _analysis(analysis_id: str) -> InventionAnalysis:
    try:
        return system.get_analysis(analysis_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

@router.get('/{analysis_id}', response_model=InventionAnalysis)
def get_analysis(analysis_id: str,p:Principal=Depends(principal_from_key)):
    require(p,Permission.read)
    return _analysis(analysis_id)

@router.get('/{analysis_id}/requirements')
def requirements(analysis_id: str,p:Principal=Depends(principal_from_key)):
    require(p,Permission.read); return _analysis(analysis_id).requirements

@router.get('/{analysis_id}/mechanisms')
def mechanisms(analysis_id: str,p:Principal=Depends(principal_from_key)):
    require(p,Permission.read); return _analysis(analysis_id).mechanisms

@router.get('/{analysis_id}/concepts')
def concepts(analysis_id: str,p:Principal=Depends(principal_from_key)):
    require(p,Permission.read); return _analysis(analysis_id).candidates

@router.get('/{analysis_id}/tradeoffs')
def tradeoffs(analysis_id: str,p:Principal=Depends(principal_from_key)):
    require(p,Permission.read); return _analysis(analysis_id).tradeoffs

@router.get('/{analysis_id}/failures')
def failures(analysis_id: str,p:Principal=Depends(principal_from_key)):
    require(p,Permission.read); return _analysis(analysis_id).failures

@router.get('/{analysis_id}/feasibility')
def feasibility(analysis_id: str,p:Principal=Depends(principal_from_key)):
    require(p,Permission.read); return _analysis(analysis_id).feasibility

@router.get('/{analysis_id}/research-gaps')
def research_gaps(analysis_id: str,p:Principal=Depends(principal_from_key)):
    require(p,Permission.read); return _analysis(analysis_id).research_gaps

@router.get('/{analysis_id}/graph')
def graph(analysis_id: str,p:Principal=Depends(principal_from_key)):
    require(p,Permission.read)
    result = _analysis(analysis_id)
    return {'node_ids': result.graph_node_ids}
