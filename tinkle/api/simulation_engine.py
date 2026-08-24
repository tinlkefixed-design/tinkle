from fastapi import APIRouter, Depends, HTTPException

from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.simulation_engine import (
    AnalysisRequest,
    MechanicsSimulationRequest,
    MechanicsSimulationResult,
    OptimizationRequest,
    PhysicsLabEngine,
    SimulationEngine,
    SimulationRequest,
    SimulationResult,
    UncertaintyEngine,
)

router = APIRouter(prefix='/api/v1/simulation', tags=['simulation-engine'])
engine = SimulationEngine()
physics_engine = PhysicsLabEngine()
uncertainty_engine = UncertaintyEngine(physics_engine)

@router.post('/run', response_model=SimulationResult)
def run(req: SimulationRequest, p: Principal = Depends(principal_from_key)):
    require(p, Permission.execute)
    try:
        return engine.simulate(req)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.post('/mechanics/run', response_model=MechanicsSimulationResult)
def run_mechanics(req: MechanicsSimulationRequest, p: Principal = Depends(principal_from_key)):
    require(p, Permission.execute)
    try:
        return physics_engine.simulate(req)
    except (KeyError, ValueError) as exc:
        raise HTTPException(422, str(exc)) from exc


@router.post('/mechanics/kinetic-energy')
def kinetic_energy(req: MechanicsSimulationRequest, p: Principal = Depends(principal_from_key)):
    require(p, Permission.execute)
    try:
        return PhysicsLabEngine.kinetic_energy(req.mass, req.initial_velocity)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.post('/mechanics/potential-energy')
def potential_energy(req: MechanicsSimulationRequest, p: Principal = Depends(principal_from_key)):
    require(p, Permission.execute)
    try:
        return PhysicsLabEngine.potential_energy(req.mass, req.gravity, req.initial_position)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.post('/mechanics/momentum')
def momentum(req: MechanicsSimulationRequest, p: Principal = Depends(principal_from_key)):
    require(p, Permission.execute)
    try:
        return PhysicsLabEngine.momentum(req.mass, req.initial_velocity)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.post('/mechanics/spring-force')
def spring_force(req: MechanicsSimulationRequest, p: Principal = Depends(principal_from_key)):
    require(p, Permission.execute)
    if req.spring_constant is None or req.spring_displacement is None:
        raise HTTPException(422, 'spring_constant and spring_displacement are required')
    try:
        return PhysicsLabEngine.spring_force(req.spring_constant, req.spring_displacement)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.post('/analysis/sweep')
def sweep(req: AnalysisRequest, p: Principal = Depends(principal_from_key)):
    require(p, Permission.execute)
    try:
        return uncertainty_engine.sweep(req)
    except (KeyError, ValueError) as exc:
        raise HTTPException(422, str(exc)) from exc


@router.post('/analysis/sensitivity')
def sensitivity(req: AnalysisRequest, p: Principal = Depends(principal_from_key)):
    require(p, Permission.execute)
    try:
        return uncertainty_engine.sensitivity(req)
    except (KeyError, ValueError) as exc:
        raise HTTPException(422, str(exc)) from exc


@router.post('/analysis/uncertainty')
def uncertainty(req: AnalysisRequest, p: Principal = Depends(principal_from_key)):
    require(p, Permission.execute)
    try:
        return uncertainty_engine.uncertainty(req)
    except (KeyError, ValueError) as exc:
        raise HTTPException(422, str(exc)) from exc


@router.post('/analysis/robustness')
def robustness(req: AnalysisRequest, p: Principal = Depends(principal_from_key)):
    require(p, Permission.execute)
    try:
        return uncertainty_engine.robustness(req)
    except (KeyError, ValueError) as exc:
        raise HTTPException(422, str(exc)) from exc


@router.post('/analysis/optimize')
def optimize(req: OptimizationRequest, p: Principal = Depends(principal_from_key)):
    require(p, Permission.execute)
    try:
        return uncertainty_engine.optimize(req)
    except (KeyError, ValueError) as exc:
        raise HTTPException(422, str(exc)) from exc
