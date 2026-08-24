from fastapi import APIRouter, Depends
from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.constraint_engine import ConstraintAnalysisEngine
from tinkle.scientific_core.schemas import ScientificProblem
router=APIRouter(prefix="/api/v1/constraints",tags=["constraint-analysis"])
engine=ConstraintAnalysisEngine()
@router.post("/assess")
def assess(problem:ScientificProblem,p:Principal=Depends(principal_from_key)):
    require(p,Permission.execute); return engine.assess_problem(problem)
@router.post("/relaxations")
def relax(problem:ScientificProblem,p:Principal=Depends(principal_from_key)):
    require(p,Permission.execute); return {"candidates":engine.relax_assumptions(problem)}
