from fastapi import APIRouter, Depends, HTTPException
from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.innovation_campaign import InnovationCampaignEngine, InnovationCampaignRequest, InnovationCampaignResult
router=APIRouter(prefix='/api/v1/innovation-campaign',tags=['innovation-campaign'])
engine=InnovationCampaignEngine()
@router.post('/run',response_model=InnovationCampaignResult)
def run(req:InnovationCampaignRequest,p:Principal=Depends(principal_from_key)):
    require(p,Permission.execute)
    try:return engine.run(req)
    except ValueError as exc: raise HTTPException(422,str(exc)) from exc
