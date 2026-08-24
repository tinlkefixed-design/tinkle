from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.self_improvement import ControlledSelfImprovement, ImprovementList, ImprovementResponse, ProposalRequest, StageUpdateRequest

router = APIRouter(prefix='/api/v1/self-improvement', tags=['controlled-self-improvement'])
system = ControlledSelfImprovement()

@router.post('/proposals', response_model=ImprovementResponse)
def propose(req: ProposalRequest, p: Principal = Depends(principal_from_key)):
    require(p, Permission.write)
    proposal = system.propose(req)
    return ImprovementResponse(proposal=proposal, next_stage=_next_stage(proposal.stage), limitations=_limitations())

@router.get('/proposals', response_model=ImprovementList)
def list_proposals(p: Principal = Depends(principal_from_key)):
    require(p, Permission.read)
    return ImprovementList(items=system.list())

@router.get('/proposals/{proposal_id}', response_model=ImprovementResponse)
def get_proposal(proposal_id: UUID, p: Principal = Depends(principal_from_key)):
    require(p, Permission.read)
    try:
        proposal = system.get(proposal_id)
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc
    return ImprovementResponse(proposal=proposal, next_stage=_next_stage(proposal.stage), limitations=_limitations())

@router.post('/proposals/{proposal_id}/advance', response_model=ImprovementResponse)
def advance(proposal_id: UUID, req: StageUpdateRequest, p: Principal = Depends(principal_from_key)):
    require(p, Permission.write)
    try:
        current = system.get(proposal_id)
        from tinkle.self_improvement.schemas import ImprovementStage
        if current.stage == ImprovementStage.HUMAN_APPROVAL and req.human_approved:
            require(p, Permission.admin)
        proposal = system.advance(proposal_id, req)
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
    return ImprovementResponse(proposal=proposal, next_stage=_next_stage(proposal.stage), limitations=_limitations())

def _next_stage(stage):
    from tinkle.self_improvement.schemas import STAGES
    idx = STAGES.index(stage)
    return STAGES[idx + 1] if idx + 1 < len(STAGES) else None

def _limitations():
    return [
        'The lifecycle is a governance boundary; it does not execute arbitrary code or deploy to production.',
        'Sandbox, tests, benchmarks, security review, and comparison results are recorded only when supplied by trusted execution infrastructure.',
        'Human approval is mandatory before the Production stage.',
        'Production stage records approval/readiness but never performs a direct production mutation.',
    ]
