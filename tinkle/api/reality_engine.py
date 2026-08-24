from fastapi import APIRouter, Depends, HTTPException

from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.reality_engine import RealityEngine, ParameterSweepRequest, ResearchProjectState

router = APIRouter(prefix="/api/v1/reality", tags=["reality-engine"])
engine = RealityEngine()


@router.post("/classify-claim")
def classify_claim(statement: str, kind: str, p: Principal = Depends(principal_from_key)):
    require(p, Permission.execute)
    return engine.classify_claim(statement, kind=__import__('tinkle.reality_engine', fromlist=['ClaimKind']).ClaimKind(kind)).model_dump(mode="json")


@router.post("/validate-claim")
def validate_claim(req: dict, p: Principal = Depends(principal_from_key)):
    require(p, Permission.execute)
    try:
        return engine.validate_claim(
            req.get("claim", ""),
            evidence=req.get("evidence", []),
            assumptions=req.get("assumptions", []),
            required_parameters=req.get("required_parameters", []),
            known_values=req.get("known_values", {}),
            simulation=req.get("simulation"),
        )
    except Exception as exc:  # pragma: no cover - API boundary only
        raise HTTPException(422, str(exc)) from exc


@router.post("/sweep")
def parameter_sweep(req: ParameterSweepRequest, p: Principal = Depends(principal_from_key)):
    require(p, Permission.execute)
    return engine.parameter_sweep(req)


@router.post("/project")
def create_project(req: dict, p: Principal = Depends(principal_from_key)):
    require(p, Permission.write)
    project = ResearchProjectState(**req)
    return project.model_dump(mode="json")
