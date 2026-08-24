from fastapi import APIRouter, Depends, HTTPException
from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.simulation_engine import SimulationEngine, SimulationRequest, SimulationResult

router = APIRouter(prefix='/api/v1/simulation', tags=['simulation-engine'])
engine = SimulationEngine()

@router.post('/run', response_model=SimulationResult)
def run(req: SimulationRequest, p: Principal = Depends(principal_from_key)):
    require(p, Permission.execute)
    try:
        return engine.simulate(req)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
