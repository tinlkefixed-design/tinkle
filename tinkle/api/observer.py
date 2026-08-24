from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse
from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.observer import TinkleObserver, ObserverEventRequest, ObserverEvent, ObserverSnapshot

router = APIRouter(prefix='/api/v1/observer', tags=['tinkle-observer'])
system = TinkleObserver()

@router.post('/observe', response_model=ObserverEvent)
def observe(req: ObserverEventRequest, p: Principal = Depends(principal_from_key)):
    require(p, Permission.write)
    return system.observe(req)

@router.get('/snapshot', response_model=ObserverSnapshot)
def snapshot(p: Principal = Depends(principal_from_key)):
    require(p, Permission.read)
    return system.snapshot()

@router.get('/events', response_model=list[ObserverEvent])
def events(metric: str | None = None, p: Principal = Depends(principal_from_key)):
    require(p, Permission.read)
    return system.events(metric)
