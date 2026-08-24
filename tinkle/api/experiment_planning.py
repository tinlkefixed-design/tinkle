from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from tinkle.api.deps import principal_from_key, require
from tinkle.api.engineering_decision import system as decision_system
from tinkle.api.validation import system as validation_system
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.experiment_planning import (
    ExperimentObjective,
    ExperimentPlan,
    ExperimentPlanningEngine,
    ExperimentPlanRequest,
    ExperimentResultReference,
    PlanComparison,
    PlanInvalidation,
    ResearchObjective,
)

router = APIRouter(prefix="/api/v1/experiments", tags=["experiment-planning"])
system = ExperimentPlanningEngine(decisions=decision_system, validation=validation_system)


def _unprocessable(exc: Exception) -> HTTPException:
    return HTTPException(status_code=422, detail=str(exc))


@router.post("/objectives", response_model=ResearchObjective)
def create_objective(objective: ResearchObjective, p: Principal = Depends(principal_from_key)):  # noqa: B008
    require(p, Permission.write)
    try:
        return system.create_research_objective(objective)
    except ValueError as exc:
        raise _unprocessable(exc) from exc


@router.get("/objectives/{objective_id}", response_model=ResearchObjective)
def get_objective(objective_id: UUID, p: Principal = Depends(principal_from_key)):  # noqa: B008
    require(p, Permission.read)
    try:
        return system.state.research_objectives[objective_id]
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Research objective not found") from exc


@router.post("/experiment-objectives", response_model=ExperimentObjective)
def create_experiment_objective(objective: ExperimentObjective, p: Principal = Depends(principal_from_key)):  # noqa: B008
    require(p, Permission.write)
    try:
        return system.create_experiment_objective(objective)
    except ValueError as exc:
        raise _unprocessable(exc) from exc


@router.post("/plans", response_model=ExperimentPlan)
def create_plan(request: ExperimentPlanRequest, p: Principal = Depends(principal_from_key)):  # noqa: B008
    require(p, Permission.write)
    try:
        return system.create_plan(request)
    except ValueError as exc:
        raise _unprocessable(exc) from exc


@router.get("/plans/{plan_id}", response_model=ExperimentPlan)
def get_plan(plan_id: UUID, p: Principal = Depends(principal_from_key)):  # noqa: B008
    require(p, Permission.read)
    try:
        return system.get_plan(plan_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/plans/{plan_id}/validate")
def validate_plan(plan_id: UUID, p: Principal = Depends(principal_from_key)):  # noqa: B008
    require(p, Permission.execute)
    try:
        return system.validate_plan(plan_id)
    except ValueError as exc:
        raise _unprocessable(exc) from exc


@router.post("/plans/{plan_id}/compare", response_model=PlanComparison)
def compare_plan(plan_id: UUID, other_plan_ids: list[UUID], p: Principal = Depends(principal_from_key)):  # noqa: B008
    require(p, Permission.execute)
    try:
        return system.compare([plan_id, *other_plan_ids])
    except ValueError as exc:
        raise _unprocessable(exc) from exc


@router.get("/plans/{plan_id}/trace")
def plan_trace(plan_id: UUID, p: Principal = Depends(principal_from_key)):  # noqa: B008
    require(p, Permission.read)
    try:
        plan = system.get_plan(plan_id)
        return {"plan_id": str(plan.id), "research_objective_id": str(plan.research_objective_id), "hypothesis_ids": plan.hypothesis_ids, "candidate_ids": [str(item) for item in plan.candidate_ids], "validation_requirement_ids": plan.validation_requirement_ids, "provenance": plan.provenance}
    except ValueError as exc:
        raise _unprocessable(exc) from exc


@router.get("/plans/{plan_id}/manifest")
def plan_manifest(plan_id: UUID, p: Principal = Depends(principal_from_key)):  # noqa: B008
    require(p, Permission.read)
    try:
        return system.get_plan(plan_id).reproducibility_manifest
    except ValueError as exc:
        raise _unprocessable(exc) from exc


@router.get("/plans/{plan_id}/history")
def plan_history(plan_id: UUID, p: Principal = Depends(principal_from_key)):  # noqa: B008
    require(p, Permission.read)
    try:
        return system.history(plan_id)
    except ValueError as exc:
        raise _unprocessable(exc) from exc


@router.post("/plans/{plan_id}/results/references", response_model=ExperimentResultReference)
def register_result(plan_id: UUID, result: ExperimentResultReference, p: Principal = Depends(principal_from_key)):  # noqa: B008
    require(p, Permission.write)
    if result.experiment_plan_id != plan_id:
        raise _unprocessable(ValueError("Result plan ID does not match path"))
    try:
        return system.register_result(result)
    except ValueError as exc:
        raise _unprocessable(exc) from exc


@router.post("/plans/{plan_id}/invalidate", response_model=ExperimentPlan)
def invalidate_plan(plan_id: UUID, request: PlanInvalidation, p: Principal = Depends(principal_from_key)):  # noqa: B008
    require(p, Permission.write)
    if request.plan_id != plan_id:
        raise _unprocessable(ValueError("Invalidation plan ID does not match path"))
    try:
        return system.invalidate(request)
    except ValueError as exc:
        raise _unprocessable(exc) from exc


@router.get("/plans/{plan_id}/missing-data")
def missing_data(plan_id: UUID, p: Principal = Depends(principal_from_key)):  # noqa: B008
    require(p, Permission.read)
    try:
        return {"plan_id": str(plan_id), "missing_data": system.missing_data(plan_id)}
    except ValueError as exc:
        raise _unprocessable(exc) from exc


@router.post("/plans/recommend", response_model=PlanComparison)
def recommend(plan_ids: list[UUID], p: Principal = Depends(principal_from_key)):  # noqa: B008
    require(p, Permission.execute)
    try:
        return system.recommend(plan_ids)
    except ValueError as exc:
        raise _unprocessable(exc) from exc
