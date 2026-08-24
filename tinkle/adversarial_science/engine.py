from __future__ import annotations
from math import isfinite
from .schemas import AttackFinding, AttackMode, AttackRequest, AdversarialResult, FailureSeverity, RepairCandidate

class AdversarialScienceEngine:
    """Deterministic falsification boundary over supplied claims/data.

    It never invents measurements or evidence. A missing input is reported as
    UNKNOWN rather than treated as a pass.
    """
    def attack(self, req: AttackRequest) -> AdversarialResult:
        findings=[]
        for mode in req.attack_modes:
            findings.append(self._attack(mode, req))
        failures=[f for f in findings if not f.passed]
        repairs=[]
        if failures:
            repairs.append(RepairCandidate(
                failure_ids=[f'{i+1}' for i,f in enumerate(findings) if not f.passed],
                hypothesis='The candidate requires a repair or additional evidence before acceptance.',
                change='Address the highest-severity finding, then rerun the adversarial suite.',
            ))
        overall='FALSIFICATION_FOUND' if failures else 'NO_FAILURE_FOUND_IN_TESTED_ATTACKS'
        return AdversarialResult(
            claim=req.claim, findings=findings, overall=overall,
            repair_candidates=repairs,
            provenance={'kind':'ADVERSARIAL_TEST','evidence_is_caller_supplied':True,
                        'untested_modes':[m.value for m in AttackMode if m not in req.attack_modes]}
        )

    def _attack(self, mode: AttackMode, req: AttackRequest) -> AttackFinding:
        if mode == AttackMode.HIDDEN_ASSUMPTIONS:
            passed=bool(req.assumptions)
            return AttackFinding(mode=mode, passed=passed, severity=FailureSeverity.MINOR if passed else FailureSeverity.MAJOR,
                finding='Explicit assumptions were supplied.' if passed else 'No explicit assumptions supplied; hidden assumptions cannot be ruled out.',
                repair_hint=None if passed else 'Enumerate assumptions and retest.')
        if mode == AttackMode.ALTERNATIVE_EXPLANATIONS:
            passed=bool(req.alternatives)
            return AttackFinding(mode=mode, passed=passed, severity=FailureSeverity.MINOR if passed else FailureSeverity.MAJOR,
                finding='Alternative explanations were supplied for comparison.' if passed else 'No alternative explanation was supplied.',
                repair_hint=None if passed else 'Generate or collect independent alternative explanations.')
        if mode == AttackMode.CONTRADICTORY_DATA:
            if not req.expected or not req.observed:
                return AttackFinding(mode=mode, passed=False, severity=FailureSeverity.UNKNOWN, finding='Expected and observed values are required to test contradiction.')
            common=set(req.expected)&set(req.observed)
            contradictory=[k for k in common if req.expected[k] != req.observed[k]]
            return AttackFinding(mode=mode, passed=not contradictory, severity=FailureSeverity.MAJOR if contradictory else FailureSeverity.MINOR,
                finding='Contradictory values found: '+', '.join(sorted(contradictory)) if contradictory else 'No exact-value contradictions found in supplied fields.',
                repair_hint='Investigate measurement/model discrepancy.' if contradictory else None)
        if mode in {AttackMode.NOISE, AttackMode.MEASUREMENT_ERROR}:
            if not req.observed:
                return AttackFinding(mode=mode, passed=False, severity=FailureSeverity.UNKNOWN, finding='Observed data are required for perturbation testing.')
            vals=[float(v) for v in req.observed.values()]
            finite=all(isfinite(v) for v in vals)
            return AttackFinding(mode=mode, passed=finite, severity=FailureSeverity.FATAL if not finite else FailureSeverity.MINOR,
                finding='Observed values are finite and eligible for bounded perturbation testing.' if finite else 'Non-finite observed value detected.',
                repair_hint='Validate and sanitize measurements.' if not finite else None)
        if mode == AttackMode.EXTREME_PARAMETERS:
            if not req.expected:
                return AttackFinding(mode=mode, passed=False, severity=FailureSeverity.UNKNOWN, finding='Expected parameter values are required for extreme-value testing.')
            vals=[abs(float(v)) for v in req.expected.values()]
            finite=all(isfinite(v) for v in vals)
            extreme=any(v > 1e12 for v in vals)
            return AttackFinding(mode=mode, passed=finite and not extreme, severity=FailureSeverity.MAJOR if extreme else FailureSeverity.FATAL if not finite else FailureSeverity.MINOR,
                finding='No extreme/non-finite supplied parameters detected.' if finite and not extreme else 'Extreme or non-finite parameter detected.',
                repair_hint='Define valid operating bounds and test them explicitly.' if extreme or not finite else None)
        if mode == AttackMode.EDGE_CASES:
            keys=set(req.observed)|set(req.expected)
            passed=bool(keys)
            return AttackFinding(mode=mode, passed=passed, severity=FailureSeverity.UNKNOWN if not passed else FailureSeverity.MINOR,
                finding='At least one measurable variable exists for edge-case construction.' if passed else 'No measurable variables supplied.')
        if mode == AttackMode.MODEL_ERROR:
            passed=bool(req.evidence)
            return AttackFinding(mode=mode, passed=passed, severity=FailureSeverity.UNKNOWN if not passed else FailureSeverity.MINOR,
                finding='Evidence references exist for model-error review.' if passed else 'No evidence references supplied; model error remains unbounded.',
                repair_hint=None if passed else 'Attach model provenance and validation data.')
        if mode == AttackMode.ADVERSARIAL_INPUTS:
            passed=bool(req.claim.strip())
            return AttackFinding(mode=mode, passed=passed, severity=FailureSeverity.FATAL if not passed else FailureSeverity.MINOR,
                finding='Claim input is non-empty.' if passed else 'Empty claim.')
        return AttackFinding(mode=mode, passed=False, severity=FailureSeverity.UNKNOWN, finding='Attack mode not implemented.')
