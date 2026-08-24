from __future__ import annotations
from datetime import datetime, timezone
from uuid import UUID
from .schemas import ImprovementProposal, ImprovementStage, ProposalRequest, StageUpdateRequest, STAGES

class ControlledSelfImprovement:
    """Governed self-improvement lifecycle.

    This phase records and gates proposals through the Blueprint's mandatory
    lifecycle. It never edits production directly; the final stage records
    human approval and production readiness only.
    """
    def __init__(self) -> None:
        self._items: dict[UUID, ImprovementProposal] = {}

    def propose(self, req: ProposalRequest) -> ImprovementProposal:
        proposal = ImprovementProposal(**req.model_dump())
        self._items[proposal.id] = proposal
        return proposal

    def get(self, proposal_id: UUID) -> ImprovementProposal:
        try:
            return self._items[proposal_id]
        except KeyError as exc:
            raise KeyError('Improvement proposal not found') from exc

    def list(self) -> list[ImprovementProposal]:
        return list(self._items.values())

    def advance(self, proposal_id: UUID, req: StageUpdateRequest) -> ImprovementProposal:
        item = self.get(proposal_id)
        idx = STAGES.index(item.stage)
        if idx >= len(STAGES) - 1:
            raise ValueError('Improvement lifecycle is already at Production')
        next_stage = STAGES[idx + 1]

        if next_stage == ImprovementStage.SANDBOX and not req.sandbox_ref:
            raise ValueError('Sandbox reference is required before entering Sandbox')
        if next_stage in {ImprovementStage.TESTS, ImprovementStage.BENCHMARKS,
                           ImprovementStage.SECURITY_REVIEW, ImprovementStage.COMPARISON} and not req.result:
            raise ValueError(f'Result is required before entering {next_stage.value}')
        if next_stage == ImprovementStage.HUMAN_APPROVAL and not req.result:
            raise ValueError('Comparison result is required before Human Approval')
        if next_stage == ImprovementStage.PRODUCTION and not req.human_approved:
            raise ValueError('Explicit human approval is required before Production')

        item.stage = next_stage
        item.stage_history.append(next_stage)
        item.updated_at = datetime.now(timezone.utc)
        if req.sandbox_ref:
            item.sandbox_ref = req.sandbox_ref
        if next_stage == ImprovementStage.TESTS:
            item.test_result = req.result
        elif next_stage == ImprovementStage.BENCHMARKS:
            item.benchmark_result = req.result
        elif next_stage == ImprovementStage.SECURITY_REVIEW:
            item.security_result = req.result
        elif next_stage == ImprovementStage.COMPARISON:
            item.comparison_result = req.result
        elif next_stage == ImprovementStage.HUMAN_APPROVAL:
            item.human_approved = True
        elif next_stage == ImprovementStage.PRODUCTION:
            item.human_approved = True
            # Deliberately not applied: core principles prohibit direct AI production mutation.
            item.production_applied = False
        return item
