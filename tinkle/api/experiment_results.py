from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from tinkle.api.deps import principal_from_key, require
from tinkle.api.experiment_planning import system as planner_system
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.experiment_results import ExperimentResult, ExperimentResultsEngine

router=APIRouter(prefix='/api/v1/experiment-results',tags=['experiment-results'])
engine=ExperimentResultsEngine(planner=planner_system)
def err(exc:Exception): return HTTPException(422,str(exc))
@router.post('/results',response_model=ExperimentResult)
def create(result:ExperimentResult,p:Principal=Depends(principal_from_key)): # noqa: B008
    require(p,Permission.write)
    try:return engine.create_result(result)
    except (KeyError,ValueError) as exc:raise err(exc) from exc
@router.get('/results/{result_id}',response_model=ExperimentResult)
def get(result_id:UUID,p:Principal=Depends(principal_from_key)): # noqa: B008
    require(p,Permission.read)
    try:return engine.results[result_id]
    except KeyError as exc:raise HTTPException(404,'Experiment result not found') from exc
@router.post('/results/{result_id}/analyze')
def analyze(result_id:UUID,p:Principal=Depends(principal_from_key)): # noqa: B008
    require(p,Permission.execute)
    try:return engine.analyze(result_id)
    except (KeyError,ValueError) as exc:raise err(exc) from exc
@router.get('/results/{result_id}/analysis')
def analysis(result_id:UUID,p:Principal=Depends(principal_from_key)): # noqa: B008
    require(p,Permission.read)
    try:return engine.get_analysis(result_id)
    except (KeyError,ValueError) as exc:raise err(exc) from exc
@router.get('/results/{result_id}/comparisons')
def comparisons(result_id:UUID,p:Principal=Depends(principal_from_key)): # noqa: B008
    require(p,Permission.read);return engine.get_analysis(result_id).prediction_comparisons
@router.get('/results/{result_id}/hypothesis-impact')
def hypothesis_impact(result_id:UUID,p:Principal=Depends(principal_from_key)): # noqa: B008
    require(p,Permission.read);return engine.get_analysis(result_id).hypothesis_impacts
@router.get('/results/{result_id}/evidence-update')
def evidence_update(result_id:UUID,p:Principal=Depends(principal_from_key)): # noqa: B008
    require(p,Permission.read);return engine.get_analysis(result_id).evidence_updates
@router.get('/results/{result_id}/decision-impact')
def decision_impact(result_id:UUID,p:Principal=Depends(principal_from_key)): # noqa: B008
    require(p,Permission.read);return engine.get_analysis(result_id).decision_impacts
@router.get('/results/{result_id}/history')
def history(result_id:UUID,p:Principal=Depends(principal_from_key)): # noqa: B008
    require(p,Permission.read);return engine.history[result_id]
@router.get('/results/{result_id}/manifest')
def manifest(result_id:UUID,p:Principal=Depends(principal_from_key)): # noqa: B008
    require(p,Permission.read);return engine.get_analysis(result_id).reproducibility_manifest
@router.post('/results/{result_id}/invalidate',response_model=ExperimentResult)
def invalidate(result_id:UUID,reason:str,p:Principal=Depends(principal_from_key)): # noqa: B008
    require(p,Permission.write)
    try:return engine.invalidate(result_id,reason)
    except KeyError as exc:raise err(exc) from exc
