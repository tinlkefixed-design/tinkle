from uuid import uuid4
from tinkle.memory.service import MemoryService
from tinkle.core.schemas import MemoryType
from tinkle.self_evaluation import SelfEvaluation, SelfEvaluationRequest


def test_self_evaluation_covers_blueprint_questions_and_stores_lessons():
    memory = MemoryService()
    engine = SelfEvaluation(memory)
    task_id = uuid4()
    result = engine.evaluate(SelfEvaluationRequest(
        task_id=task_id,
        task_summary='test task',
        assumptions=['input is complete'],
        potential_errors=['edge case'],
        verified=['unit test'],
        unknowns=['external provider'],
        failures=['timeout'],
        improvements=['add timeout test'],
        remember=['external provider is not configured'],
    ), 'doctor')
    record = result.evaluation
    assert record.task_id == task_id
    assert record.assumptions == ['input is complete']
    assert record.potential_errors == ['edge case']
    assert record.verified == ['unit test']
    assert record.unknowns == ['external provider']
    assert record.failures == ['timeout']
    assert record.improvements == ['add timeout test']
    assert record.remember == ['external provider is not configured']
    assert record.lessons_stored == 3
    assert len(memory.search('doctor', 'external provider')) == 1
    assert len(memory.search('doctor', 'timeout', MemoryType.failure)) == 1


def test_self_evaluation_does_not_invent_lessons():
    engine = SelfEvaluation(MemoryService())
    result = engine.evaluate(SelfEvaluationRequest(task_summary='empty observations'), 'doctor')
    assert result.lessons == []
    assert result.evaluation.lessons_stored == 0
