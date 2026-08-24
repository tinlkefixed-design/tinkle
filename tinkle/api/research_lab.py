from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.research_lab import (
    ComparisonRequest,
    MeasurementRequest,
    Prediction,
    ResearchExperiment,
    ResearchHypothesis,
    ResearchLab,
    ResearchQuestion,
)

router = APIRouter(prefix="/api/v1/research", tags=["research-lab"])
lab = ResearchLab()


def _error(exc: Exception) -> HTTPException:
    return HTTPException(status_code=422, detail=str(exc))


@router.post("/questions")
def create_question(question: ResearchQuestion, p: Principal = Depends(principal_from_key)):
    require(p, Permission.write)
    return question


@router.post("/workflows")
def create_workflow(question: ResearchQuestion, hypothesis: ResearchHypothesis, experiment: ResearchExperiment | None = None, prediction: Prediction | None = None, p: Principal = Depends(principal_from_key)):
    require(p, Permission.write)
    try:
        return lab.create_workflow(question, hypothesis, experiment, prediction)
    except ValueError as exc:
        raise _error(exc) from exc


@router.post("/workflows/{question_id}/predictions")
def create_prediction(question_id: UUID, prediction: Prediction, p: Principal = Depends(principal_from_key)):
    require(p, Permission.write)
    try:
        return lab.create_prediction(question_id, prediction)
    except (KeyError, ValueError) as exc:
        raise _error(exc) from exc


@router.post("/workflows/{question_id}/run")
def run_experiment(question_id: UUID, p: Principal = Depends(principal_from_key)):
    require(p, Permission.execute)
    try:
        return lab.run_simulation(question_id)
    except (KeyError, ValueError) as exc:
        raise _error(exc) from exc


@router.post("/workflows/{question_id}/measurements")
def record_measurement(question_id: UUID, request: MeasurementRequest, p: Principal = Depends(principal_from_key)):
    require(p, Permission.write)
    try:
        return lab.record_measurement(question_id, request.measurement)
    except (KeyError, ValueError) as exc:
        raise _error(exc) from exc


@router.post("/workflows/{question_id}/compare")
def compare(question_id: UUID, request: ComparisonRequest, p: Principal = Depends(principal_from_key)):
    require(p, Permission.execute)
    try:
        return lab.compare(question_id, request.predicted_range)
    except (KeyError, ValueError) as exc:
        raise _error(exc) from exc


@router.post("/workflows/{question_id}/update")
def update_hypothesis(question_id: UUID, p: Principal = Depends(principal_from_key)):
    require(p, Permission.execute)
    try:
        return lab.update_hypothesis(question_id)
    except (KeyError, ValueError) as exc:
        raise _error(exc) from exc


@router.get("/workflows/{question_id}/history")
def history(question_id: UUID, p: Principal = Depends(principal_from_key)):
    require(p, Permission.read)
    try:
        return lab.history(question_id)
    except KeyError as exc:
        raise _error(exc) from exc
