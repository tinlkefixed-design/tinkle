from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.invention_design import (
    CandidateComparison,
    ComparisonRequest,
    DesignCandidate,
    DesignEvaluation,
    EngineeringRequirement,
    EvaluationRequest,
    InventionDesignEngine,
)

router = APIRouter(prefix="/api/v1/invention", tags=["invention-design"])
system = InventionDesignEngine()


def _unprocessable(exc: Exception) -> HTTPException:
    return HTTPException(status_code=422, detail=str(exc))


@router.post("/requirements", response_model=EngineeringRequirement)
def create_requirement(requirement: EngineeringRequirement, p: Principal = Depends(principal_from_key)):  # noqa: B008
    require(p, Permission.write)
    try:
        return system.create_requirement(requirement)
    except ValueError as exc:
        raise _unprocessable(exc) from exc


@router.post("/candidates", response_model=DesignCandidate)
def create_candidate(candidate: DesignCandidate, p: Principal = Depends(principal_from_key)):  # noqa: B008
    require(p, Permission.write)
    try:
        return system.create_candidate(candidate)
    except ValueError as exc:
        raise _unprocessable(exc) from exc


@router.get("/candidates/{candidate_id}", response_model=DesignCandidate)
def get_candidate(candidate_id: UUID, p: Principal = Depends(principal_from_key)):  # noqa: B008
    require(p, Permission.read)
    try:
        return system.get_candidate(candidate_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/candidates/{candidate_id}/evaluate", response_model=DesignEvaluation)
def evaluate_candidate(candidate_id: UUID, request: EvaluationRequest, p: Principal = Depends(principal_from_key)):  # noqa: B008
    require(p, Permission.execute)
    try:
        return system.evaluate(candidate_id, request)
    except (KeyError, ValueError) as exc:
        raise _unprocessable(exc) from exc


@router.post("/candidates/compare", response_model=CandidateComparison)
def compare_candidates(request: ComparisonRequest, p: Principal = Depends(principal_from_key)):  # noqa: B008
    require(p, Permission.execute)
    try:
        return system.compare(request.candidate_ids)
    except KeyError as exc:
        raise _unprocessable(exc) from exc


@router.get("/candidates/{candidate_id}/history")
def candidate_history(candidate_id: UUID, p: Principal = Depends(principal_from_key)):  # noqa: B008
    require(p, Permission.read)
    try:
        return system.history(candidate_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
