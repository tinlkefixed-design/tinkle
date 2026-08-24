from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.container import memory
from tinkle.core.schemas import Permission
from tinkle.self_evaluation import SelfEvaluation, SelfEvaluationRequest, SelfEvaluationResult

router = APIRouter(prefix='/api/v1/self-evaluation', tags=['self-evaluation'])
system = SelfEvaluation(memory)


@router.post('/evaluate', response_model=SelfEvaluationResult)
def evaluate(req: SelfEvaluationRequest, p: Principal = Depends(principal_from_key)):
    require(p, Permission.write)
    if req.task_id is not None:
        try:
            from tinkle.core.container import tasks
            tasks.get(req.task_id, p.name)
        except Exception as exc:
            raise HTTPException(404, 'Task not found') from exc
    return system.evaluate(req, p.name)


@router.get('/{task_id}')
def get_evaluation(task_id: UUID, p: Principal = Depends(principal_from_key)):
    require(p, Permission.read)
    try:
        return system.get(task_id, p.name)
    except KeyError as exc:
        raise HTTPException(404, 'Self-evaluation not found') from exc
