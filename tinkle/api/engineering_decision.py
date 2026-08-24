from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from tinkle.api.deps import principal_from_key, require
from tinkle.api.invention_design import system as invention_system
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.engineering_decision import (
    DecisionEvidence,
    DecisionRequest,
    EngineeringDecision,
    EngineeringDecisionEngine,
    Tradeoff,
)

router = APIRouter(prefix="/api/v1/engineering/decisions", tags=["engineering-decision"])
system = EngineeringDecisionEngine(invention=invention_system)


def _unprocessable(exc: Exception) -> HTTPException:
    return HTTPException(status_code=422, detail=str(exc))


@router.post("/evidence", response_model=DecisionEvidence)
def create_evidence(evidence: DecisionEvidence, p: Principal = Depends(principal_from_key)):  # noqa: B008
    require(p, Permission.write)
    try:
        return system.create_evidence(evidence)
    except ValueError as exc:
        raise _unprocessable(exc) from exc


@router.post("/requests", response_model=DecisionRequest)
def create_request(request: DecisionRequest, p: Principal = Depends(principal_from_key)):  # noqa: B008
    require(p, Permission.write)
    try:
        return system.create_request(request)
    except ValueError as exc:
        raise _unprocessable(exc) from exc


@router.post("/{request_id}/evaluate", response_model=EngineeringDecision)
def evaluate_request(request_id: UUID, p: Principal = Depends(principal_from_key)):  # noqa: B008
    require(p, Permission.execute)
    try:
        return system.evaluate(request_id)
    except (KeyError, ValueError) as exc:
        raise _unprocessable(exc) from exc


@router.post("/{request_id}/tradeoffs", response_model=list[Tradeoff])
def request_tradeoffs(request_id: UUID, p: Principal = Depends(principal_from_key)):  # noqa: B008
    require(p, Permission.execute)
    try:
        return system.tradeoffs(request_id)
    except (KeyError, ValueError) as exc:
        raise _unprocessable(exc) from exc


@router.post("/{request_id}/decide", response_model=EngineeringDecision)
def decide_request(request_id: UUID, selected_candidate: UUID | None = None, p: Principal = Depends(principal_from_key)):  # noqa: B008
    require(p, Permission.execute)
    try:
        return system.decide(request_id, selected_candidate)
    except (KeyError, ValueError) as exc:
        raise _unprocessable(exc) from exc


@router.get("/{request_id}", response_model=EngineeringDecision)
def get_decision(request_id: UUID, p: Principal = Depends(principal_from_key)):  # noqa: B008
    require(p, Permission.read)
    try:
        return system.decisions[request_id]
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Decision not found") from exc


@router.get("/{request_id}/history")
def decision_history(request_id: UUID, p: Principal = Depends(principal_from_key)):  # noqa: B008
    require(p, Permission.read)
    try:
        return system.history(request_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
