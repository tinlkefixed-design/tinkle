from __future__ import annotations

import re
from tinkle.guardian.schemas import GuardianCategory, GuardianFinding, GuardianRequest, GuardianResult


class Guardian:
    """Phase 12 Guardian: deterministic critical review boundary.

    Guardian does not invent external evidence. It inspects the supplied result,
    evidence, assumptions and known limitations, and reports review items that
    require validation or attention.
    """

    def review(self, request: GuardianRequest) -> GuardianResult:
        categories = request.requested_categories or list(GuardianCategory)
        findings: list[GuardianFinding] = []
        for category in categories:
            findings.extend(self._check(category, request))
        findings = self._deduplicate(findings)
        conclusion = self._conclusion(findings)
        return GuardianResult(
            result=request.result.strip(),
            findings=findings,
            categories_checked=categories,
            status="REVIEW_READY",
            conclusion=conclusion,
        )

    def _check(self, category: GuardianCategory, request: GuardianRequest) -> list[GuardianFinding]:
        text = request.result.strip()
        lower = text.lower()
        evidence = [str(item).strip() for item in request.evidence if str(item).strip()]
        assumptions = [str(item).strip() for item in request.assumptions if str(item).strip()]
        limitations = [str(item).strip() for item in request.known_limitations if str(item).strip()]

        if category is GuardianCategory.errors:
            markers = ["error", "exception", "failed", "failure", "incorrect", "bug"]
            hits = [m for m in markers if re.search(rf"\b{re.escape(m)}\b", lower)]
            if hits:
                return [GuardianFinding(category=category, severity="high", statement="Potential error indicators are present.", basis=f"Detected terms: {', '.join(hits)}")]
            return [GuardianFinding(category=category, severity="review", statement="No explicit error marker was detected; absence of a marker is not proof of correctness.", basis="Text scan only.")]

        if category is GuardianCategory.contradictions:
            contradiction_terms = ["however", "contradiction", "contradicts", "inconsistent", "conflicts"]
            hits = [m for m in contradiction_terms if m in lower]
            if hits:
                return [GuardianFinding(category=category, severity="high", statement="Potential contradiction language is present and should be resolved.", basis=f"Detected terms: {', '.join(hits)}")]
            return [GuardianFinding(category=category, severity="review", statement="No explicit contradiction marker was detected; independent verification is still required.", basis="Text scan only.")]

        if category is GuardianCategory.hidden_assumptions:
            if assumptions:
                return [GuardianFinding(category=category, severity="review", statement=f"Supplied assumptions require validation: {a}", basis="User-supplied assumption list.") for a in assumptions]
            markers = ["assume", "assuming", "we assume", "presume"]
            hits = [m for m in markers if m in lower]
            if hits:
                return [GuardianFinding(category=category, severity="review", statement="The result contains assumption language that should be surfaced explicitly.", basis=f"Detected terms: {', '.join(hits)}")]
            return [GuardianFinding(category=category, severity="review", statement="No explicit assumptions were supplied; hidden assumptions remain possible.", basis="No assumption inventory was provided.")]

        if category is GuardianCategory.missing_data:
            if not evidence:
                return [GuardianFinding(category=category, severity="high", statement="No supporting evidence was supplied for review.", basis="Evidence list is empty.")]
            if any(term in lower for term in ["missing data", "insufficient data", "not enough information", "unknown"]):
                return [GuardianFinding(category=category, severity="high", statement="The result itself signals missing or unknown information.", basis="Text indicates missing/unknown data.")]
            return [GuardianFinding(category=category, severity="review", statement="Evidence was supplied, but completeness was not established.", basis=f"{len(evidence)} evidence item(s) supplied.")]

        if category is GuardianCategory.edge_cases:
            edge_markers = ["edge case", "boundary", "empty", "null", "zero", "negative", "timeout", "overflow"]
            hits = [m for m in edge_markers if m in lower]
            if hits:
                return [GuardianFinding(category=category, severity="review", statement="Some edge-case considerations are mentioned and should be tested explicitly.", basis=f"Detected terms: {', '.join(hits)}")]
            return [GuardianFinding(category=category, severity="review", statement="No explicit edge-case analysis was supplied.", basis="No edge-case markers detected in supplied result.")]

        if category is GuardianCategory.failure_modes:
            failure_markers = ["failure mode", "fallback", "retry", "recovery", "degraded", "fails"]
            hits = [m for m in failure_markers if m in lower]
            if hits:
                return [GuardianFinding(category=category, severity="review", statement="Failure-handling language is present and should be validated against actual behavior.", basis=f"Detected terms: {', '.join(hits)}")]
            return [GuardianFinding(category=category, severity="review", statement="No explicit failure-mode analysis was supplied.", basis="No failure-mode markers detected in supplied result.")]

        if category is GuardianCategory.model_limitations:
            if limitations:
                return [GuardianFinding(category=category, severity="review", statement=f"Known limitation: {l}", basis="Supplied limitations list.") for l in limitations]
            limitation_markers = ["limitation", "cannot", "not supported", "boundary", "not claimed"]
            hits = [m for m in limitation_markers if m in lower]
            if hits:
                return [GuardianFinding(category=category, severity="review", statement="The result includes capability/limitation boundary language that should remain explicit.", basis=f"Detected terms: {', '.join(hits)}")]
            return [GuardianFinding(category=category, severity="review", statement="No explicit model limitation inventory was supplied.", basis="No limitation list or marker detected.")]

        return []

    @staticmethod
    def _deduplicate(findings: list[GuardianFinding]) -> list[GuardianFinding]:
        seen: set[tuple[str, str]] = set()
        result: list[GuardianFinding] = []
        for finding in findings:
            key = (finding.category.value, finding.statement)
            if key not in seen:
                seen.add(key)
                result.append(finding)
        return result

    @staticmethod
    def _conclusion(findings: list[GuardianFinding]) -> str:
        if any(f.severity == "high" for f in findings):
            return "REVIEW_REQUIRED: high-priority concerns or missing support were identified."
        return "REVIEW_REQUIRED: no high-priority marker was detected, but Guardian does not certify correctness."
