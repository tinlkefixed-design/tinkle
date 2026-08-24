from tinkle.self_improvement import ControlledSelfImprovement
from tinkle.self_improvement.schemas import ImprovementStage, ImprovementType, ProposalRequest, StageUpdateRequest


def req():
    return ProposalRequest(
        improvement_type=ImprovementType.workflow,
        title='Improve retrieval workflow',
        rationale='Observed retrieval misses',
        target='research workflow',
        expected_benefit='fewer missed relevant documents',
        risks=['regression'],
        evidence=['observer:event-1'],
    )


def test_lifecycle_requires_order_and_evidence():
    engine = ControlledSelfImprovement()
    item = engine.propose(req())
    assert item.stage == ImprovementStage.PROPOSAL
    try:
        engine.advance(item.id, StageUpdateRequest())
        assert False, 'sandbox reference should be required'
    except ValueError:
        pass
    item = engine.advance(item.id, StageUpdateRequest(sandbox_ref='sandbox://proposal-1'))
    assert item.stage == ImprovementStage.SANDBOX
    item = engine.advance(item.id, StageUpdateRequest())
    assert item.stage == ImprovementStage.IMPLEMENTATION


def test_production_requires_human_approval_and_is_not_applied():
    engine = ControlledSelfImprovement()
    item = engine.propose(req())
    for result, ref in [
        (None, 'sandbox://p1'),
        (None, None),
        ('tests-pass', None),
        ('bench-pass', None),
        ('security-pass', None),
        ('comparison-pass', None),
        ('comparison-reviewed', None),
    ]:
        item = engine.advance(item.id, StageUpdateRequest(result=result, sandbox_ref=ref))
    assert item.stage == ImprovementStage.HUMAN_APPROVAL
    try:
        engine.advance(item.id, StageUpdateRequest())
        assert False, 'human approval should be required'
    except ValueError:
        pass
    item = engine.advance(item.id, StageUpdateRequest(human_approved=True))
    assert item.stage == ImprovementStage.PRODUCTION
    assert item.production_applied is False
