from __future__ import annotations
from tinkle.core.schemas import MemoryType
from tinkle.memory.service import MemoryService
from .schemas import SelfEvaluationRequest, SelfEvaluationResult, SelfEvaluationRecord


class SelfEvaluation:
    """Phase 22: structured post-task self-evaluation and lesson storage.

    The Blueprint defines seven evaluation questions. It does not specify an
    autonomous evaluator, so the engine records caller-supplied observations
    and stores explicit lessons without inventing verification or causality.
    """

    def __init__(self, memory: MemoryService) -> None:
        self._memory = memory
        self._evaluations: dict[tuple[str, str], SelfEvaluationRecord] = {}

    def evaluate(self, request: SelfEvaluationRequest, owner: str) -> SelfEvaluationResult:
        lessons: list[dict[str, object]] = []
        for lesson in request.improvements:
            item = self._memory.write(
                owner=owner,
                memory_type=MemoryType.reasoning,
                content=lesson,
                task_id=request.task_id,
                metadata={"source": "self-evaluation", "kind": "improvement"},
            )
            lessons.append({"id": str(item.id), "kind": "improvement", "content": lesson})
        for lesson in request.remember:
            item = self._memory.write(
                owner=owner,
                memory_type=MemoryType.reasoning,
                content=lesson,
                task_id=request.task_id,
                metadata={"source": "self-evaluation", "kind": "lesson"},
            )
            lessons.append({"id": str(item.id), "kind": "lesson", "content": lesson})
        for failure in request.failures:
            item = self._memory.write(
                owner=owner,
                memory_type=MemoryType.failure,
                content=failure,
                task_id=request.task_id,
                metadata={"source": "self-evaluation", "kind": "failure"},
            )
            lessons.append({"id": str(item.id), "kind": "failure", "content": failure})

        record = SelfEvaluationRecord(
            task_id=request.task_id,
            task_summary=request.task_summary,
            assumptions=list(request.assumptions),
            potential_errors=list(request.potential_errors),
            verified=list(request.verified),
            unknowns=list(request.unknowns),
            failures=list(request.failures),
            improvements=list(request.improvements),
            remember=list(request.remember),
            lessons_stored=len(lessons),
        )
        if request.task_id is not None:
            self._evaluations[(owner, str(request.task_id))] = record

        return SelfEvaluationResult(
            evaluation=record,
            lessons=lessons,
            limitations=[
                "The Blueprint specifies the seven self-evaluation questions but does not define an autonomous evaluator.",
                "Observations are caller-supplied; Tinkle does not fabricate verification, failures, or lessons.",
            ],
        )

    def get(self, task_id, owner: str) -> SelfEvaluationRecord:
        key = (owner, str(task_id))
        if key not in self._evaluations:
            raise KeyError("Self-evaluation not found")
        return self._evaluations[key]
