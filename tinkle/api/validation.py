from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from tinkle.api.deps import principal_from_key, require
from tinkle.api.engineering_decision import system as decision_system
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.validation import (
    DecisionTrace,
    EvidenceChain,
    InvalidationCondition,
    ReproducibilityManifest,
    ValidationEngine,
    ValidationGate,
    ValidationRecord,
    ValidationRequirement,
)

router = APIRouter(prefix="/api/v1/validation", tags=["validation"])
system = ValidationEngine(decisions=decision_system)


def _unprocessable(exc: Exception) -> HTTPException:
    return HTTPException(status_code=422, detail=str(exc))


@router.post("/requirements", response_model=ValidationRequirement)
def create_requirement(requirement: ValidationRequirement, p: Principal = Depends(principal_from_key)):  # noqa: B008
    require(p, Permission.write)
    try:
        return system.create_requirement(requirement)
    except (KeyError, ValueError) as exc:
        raise _unprocessable(exc) from exc


@router.get("/requirements/{requirement_id}", response_model=ValidationRequirement)
def get_requirement(requirement_id: str, p: Principal = Depends(principal_from_key)):  # noqa: B008
    require(p, Permission.read)
    try:
        return system.requirements[requirement_id]
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Validation requirement not found") from exc


@router.post("/records", response_model=ValidationRecord)
def create_record(record: ValidationRecord, p: Principal = Depends(principal_from_key)):  # noqa: B008
    require(p, Permission.write)
    try:
        return system.create_record(record)
    except (KeyError, ValueError) as exc:
        raise _unprocessable(exc) from exc


@router.get("/records/{record_id}", response_model=ValidationRecord)
def get_record(record_id: UUID, p: Principal = Depends(principal_from_key)):  # noqa: B008
    require(p, Permission.read)
    try:
        return system.records[record_id]
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Validation record not found") from exc


@router.post("/decisions/{decision_id}/gate", response_model=ValidationGate)
def validation_gate(decision_id: UUID, p: Principal = Depends(principal_from_key)):  # noqa: B008
    require(p, Permission.execute)
    try:
        return system.gate(decision_id)
    except KeyError as exc:
        raise _unprocessable(exc) from exc


@router.get("/decisions/{decision_id}/trace", response_model=DecisionTrace)
def decision_trace(decision_id: UUID, p: Principal = Depends(principal_from_key)):  # noqa: B008
    require(p, Permission.read)
    try:
        return system.trace(decision_id)
    except KeyError as exc:
        raise _unprocessable(exc) from exc


@router.get("/decisions/{decision_id}/evidence-chain", response_model=EvidenceChain)
def evidence_chain(decision_id: UUID, p: Principal = Depends(principal_from_key)):  # noqa: B008
    require(p, Permission.read)
    try:
        return system.evidence_chain(decision_id)
    except KeyError as exc:
        raise _unprocessable(exc) from exc


@router.get("/decisions/{decision_id}/reproducibility", response_model=ReproducibilityManifest)
def reproducibility(decision_id: UUID, p: Principal = Depends(principal_from_key)):  # noqa: B008
    require(p, Permission.read)
    try:
        return system.reproducibility(decision_id)
    except KeyError as exc:
        raise _unprocessable(exc) from exc


@router.post("/decisions/{decision_id}/invalidation-conditions", response_model=InvalidationCondition)
def add_invalidation(decision_id: UUID, condition: InvalidationCondition, p: Principal = Depends(principal_from_key)):  # noqa: B008
    require(p, Permission.write)
    if condition.decision_id != decision_id:
        raise HTTPException(status_code=422, detail="Condition decision ID does not match path")
    try:
        return system.add_invalidation_condition(condition)
    except (KeyError, ValueError) as exc:
        raise _unprocessable(exc) from exc


@router.get("/decisions/{decision_id}/history")
def validation_history(decision_id: UUID, p: Principal = Depends(principal_from_key)):  # noqa: B008
    require(p, Permission.read)
    try:
        return system.history(decision_id)
    except KeyError as exc:
        raise _unprocessable(exc) from exc
