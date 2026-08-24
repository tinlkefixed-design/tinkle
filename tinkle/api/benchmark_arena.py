from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.benchmark_arena import BenchmarkArena, CATEGORIES

router=APIRouter(prefix='/api/v1/benchmark-arena', tags=['benchmark-arena'])
arena=BenchmarkArena('2.5.0')

class BenchmarkRequest(BaseModel):
    version: str|None=None
    checks: dict[str, object]=Field(default_factory=dict)

class CompareRequest(BaseModel):
    from_version: str
    to_version: str

@router.get('/categories')
def categories(p: Principal=Depends(principal_from_key)):
    require(p, Permission.read)
    return {'categories':CATEGORIES}

@router.post('/run')
def run(req: BenchmarkRequest, p: Principal=Depends(principal_from_key)):
    require(p, Permission.execute)
    unknown=set(req.checks)-set(CATEGORIES)
    if unknown:
        raise HTTPException(422, f'Unknown benchmark categories: {sorted(unknown)}')
    return arena.run(req.checks, req.version)

@router.get('/history')
def history(p: Principal=Depends(principal_from_key)):
    require(p, Permission.read)
    return {'runs':arena.history()}

@router.post('/compare')
def compare(req: CompareRequest, p: Principal=Depends(principal_from_key)):
    require(p, Permission.read)
    runs={r['version']:r for r in arena.history()}
    if req.from_version not in runs or req.to_version not in runs:
        raise HTTPException(404,'Both benchmark versions must have completed runs')
    return arena.compare(runs[req.from_version],runs[req.to_version])
