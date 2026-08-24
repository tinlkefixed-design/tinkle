from fastapi import APIRouter, Depends, HTTPException
from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.visual3d import Visual3DEngine, SceneRequest, Simulation3DRequest, CADRequest

router = APIRouter(prefix='/api/v1/visual3d', tags=['visual-3d'])
engine = Visual3DEngine()

@router.get('/catalog')
def catalog(p: Principal = Depends(principal_from_key)):
    require(p, Permission.read)
    return {'models': engine.catalog()}

@router.post('/scene')
def scene(req: SceneRequest, p: Principal = Depends(principal_from_key)):
    require(p, Permission.execute)
    try: return engine.scene(req).model_dump()
    except ValueError as exc: raise HTTPException(422, str(exc)) from exc

@router.post('/cad')
def cad(req: CADRequest, p: Principal = Depends(principal_from_key)):
    require(p, Permission.execute)
    try: return engine.scene(SceneRequest(kind='cad', name=req.primitive, parameters=req.parameters)).model_dump()
    except ValueError as exc: raise HTTPException(422, str(exc)) from exc

@router.post('/simulate')
def simulate(req: Simulation3DRequest, p: Principal = Depends(principal_from_key)):
    require(p, Permission.execute)
    try: return engine.simulate(req).model_dump()
    except ValueError as exc: raise HTTPException(422, str(exc)) from exc
