from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.skill_evolution import SkillEvolution, SkillEvolutionRequest, SkillEvolutionResult, SkillListResult

router = APIRouter(prefix='/api/v1/skills', tags=['skill-evolution'])
system = SkillEvolution()


@router.post('/evolve', response_model=SkillEvolutionResult)
def evolve(req: SkillEvolutionRequest, p: Principal = Depends(principal_from_key)):
    require(p, Permission.write)
    try:
        return system.evolve(req)
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.get('', response_model=SkillListResult)
def list_skills(p: Principal = Depends(principal_from_key)):
    require(p, Permission.read)
    return system.list()


@router.get('/{skill_id}', response_model=object)
def get_skill(skill_id: UUID, p: Principal = Depends(principal_from_key)):
    require(p, Permission.read)
    try:
        return system.get(skill_id)
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc
