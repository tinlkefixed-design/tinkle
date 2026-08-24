from __future__ import annotations
from tinkle.hypothesis_universe.schemas import (
    Hypothesis, HypothesisRequest, HypothesisResult, HypothesisStatus,
)

class HypothesisUniverse:
    """Phase 18 bounded hypothesis lifecycle.

    The Blueprint defines a universe of multiple hypotheses and the lifecycle
    Generate -> Test -> Reject -> Modify -> Combine -> Retest. It does not
    prescribe an LLM generation algorithm or scientific truth oracle, so this
    engine performs explicit, auditable hypothesis operations supplied by the
    caller rather than inventing evidence or claiming validation.
    """
    def run(self, request: HypothesisRequest) -> HypothesisResult:
        hypotheses: list[Hypothesis] = [
            Hypothesis(id=f"H{i}", text=text.strip())
            for i, text in enumerate(request.hypotheses, 1) if text.strip()
        ]
        lifecycle = ["Generate"]
        by_id = {h.id: h for h in hypotheses}

        for test in request.tests:
            h = by_id.get(test.hypothesis_id)
            if not h:
                continue
            lifecycle.append("Test")
            if test.outcome == "reject":
                h.status = HypothesisStatus.REJECTED
            elif test.outcome == "support":
                h.status = HypothesisStatus.SUPPORTED
            else:
                h.status = HypothesisStatus.RETEST_REQUIRED
                h.metadata["test_evidence"] = test.evidence
                h.metadata["test_confidence"] = test.confidence

        for hypothesis_id, modified_text in request.modifications.items():
            h = by_id.get(hypothesis_id)
            if not h or not modified_text.strip():
                continue
            lifecycle.append("Modify")
            child_id = f"{hypothesis_id}M{sum(1 for x in hypotheses if x.id.startswith(hypothesis_id + 'M')) + 1}"
            child = Hypothesis(id=child_id, text=modified_text.strip(), status=HypothesisStatus.MODIFIED, parent_ids=[hypothesis_id])
            hypotheses.append(child)
            by_id[child_id] = child

        for pair in request.combinations:
            valid = [by_id[x] for x in pair if x in by_id]
            if len(valid) < 2:
                continue
            lifecycle.append("Combine")
            combo_id = f"HCOMB{len([x for x in hypotheses if x.id.startswith('HCOMB')]) + 1}"
            combo_text = " + ".join(h.text for h in valid)
            child = Hypothesis(id=combo_id, text=combo_text, status=HypothesisStatus.COMBINED, parent_ids=[h.id for h in valid])
            hypotheses.append(child)
            by_id[combo_id] = child

        retest_required: list[str] = []
        if request.retest:
            for h in hypotheses:
                if h.status in {HypothesisStatus.MODIFIED, HypothesisStatus.COMBINED, HypothesisStatus.RETEST_REQUIRED}:
                    h.status = HypothesisStatus.RETEST_REQUIRED
                    retest_required.append(h.id)
            if retest_required:
                lifecycle.append("Retest")

        counts = {status.value: sum(1 for h in hypotheses if h.status == status) for status in HypothesisStatus}
        return HypothesisResult(
            question=request.question,
            hypotheses=hypotheses,
            lifecycle=lifecycle,
            counts=counts,
            retest_required=retest_required,
            limitations=[
                "The Blueprint does not specify an autonomous hypothesis-generation algorithm.",
                "Testing requires explicit test outcomes/evidence; the engine does not invent scientific evidence.",
                "RETEST_REQUIRED means another verification step is required; it is not a claim that the hypothesis is true.",
            ],
        )
