from __future__ import annotations
import re
from tinkle.constraint_engine.schemas import *
from tinkle.scientific_core.schemas import ConstraintKind, ScientificProblem

class ConstraintAnalysisEngine:
    """Separates physical impossibility from present-day engineering limits.

    It never emits an absolute impossibility proof merely from missing technology,
    cost, or current materials. Fundamental claims require an explicit law and scope.
    """
    _MARKERS = {
        ConstraintKind.fundamental: ["speed of light", "conservation", "second law", "thermodynamic", "causality", "charge conservation"],
        ConstraintKind.technology: ["current technology", "technology today", "available technology", "not possible with current"],
        ConstraintKind.material: ["material unavailable", "no material", "material limit", "yield strength"],
        ConstraintKind.energy: ["energy budget", "power budget", "energy required"],
        ConstraintKind.manufacturing: ["manufactur", "fabricat", "tolerance", "assembly"],
        ConstraintKind.economic: ["cost", "budget", "expensive", "price"],
        ConstraintKind.information: ["unknown parameter", "insufficient data", "missing data", "unknown"],
        ConstraintKind.assumption: ["assume", "assumption", "idealized", "neglect"],
        ConstraintKind.safety: ["hazard", "unsafe", "risk", "danger"],
        ConstraintKind.time: ["deadline", "time limit", "latency"],
        ConstraintKind.environmental: ["temperature range", "humidity", "environment", "radiation"],
    }

    def classify(self, expression: str, rationale: str = "") -> ConstraintAssessment:
        text = f"{expression} {rationale}".casefold()
        kind = ConstraintKind.unknown
        for candidate, markers in self._MARKERS.items():
            if any(m in text for m in markers):
                kind = candidate; break
        status = ConstraintStatus.UNKNOWN if kind == ConstraintKind.unknown else ConstraintStatus.BLOCKED
        if kind in {ConstraintKind.technology, ConstraintKind.material, ConstraintKind.manufacturing, ConstraintKind.economic, ConstraintKind.information, ConstraintKind.assumption}:
            status = ConstraintStatus.RELAXABLE
        if kind == ConstraintKind.fundamental:
            status = ConstraintStatus.BLOCKED
        reason = {
            ConstraintKind.fundamental: "Potentially fundamental; requires an explicit governing law, assumptions, evidence and scope before an impossibility claim.",
            ConstraintKind.technology: "Current capability limit, not evidence of physical impossibility.",
            ConstraintKind.material: "Current material availability/performance limit; alternative materials must be considered.",
            ConstraintKind.energy: "Energy requirement may be an engineering constraint; fundamental status requires a physical bound.",
            ConstraintKind.manufacturing: "Manufacturing limitation rather than a universal physical prohibition.",
            ConstraintKind.economic: "Economic constraint does not establish scientific impossibility.",
            ConstraintKind.information: "Knowledge/data limitation; acquisition or measurement may relax it.",
            ConstraintKind.assumption: "Model assumption can potentially be relaxed and recomputed.",
        }.get(kind, "Constraint could not be classified confidently.")
        return ConstraintAssessment(expression=expression, kind=kind, status=status, reason=reason, confidence=0.85 if kind != ConstraintKind.unknown else 0.2)

    def assess_problem(self, problem: ScientificProblem) -> ImpossibilityAssessment:
        assessments = [self.classify(c.expression, c.rationale or "") for c in problem.constraints]
        assumptions = list(problem.assumptions)
        if any(a.kind == ConstraintKind.fundamental for a in assessments):
            conclusion = "FUNDAMENTAL_CONSTRAINT_POSSIBLE_BUT_NOT_PROVED"
            proof = "LAW_REQUIRED"
        elif assessments:
            conclusion = "NO_ABSOLUTE_IMPOSSIBILITY_ESTABLISHED"
            proof = "NONE"
        else:
            conclusion = "INSUFFICIENT_CONSTRAINT_INFORMATION"
            proof = "NONE"
        return ImpossibilityAssessment(claim=problem.objective, conclusion=conclusion, assessments=assessments, assumptions=assumptions, scope="problem-defined scope", proof_level=proof)

    def relax_assumptions(self, problem: ScientificProblem) -> list[RelaxationCandidate]:
        candidates=[]
        for assumption in problem.assumptions:
            low=assumption.casefold()
            if any(k in low for k in ("ideal", "constant", "neglig", "fixed", "perfect")):
                alt=re.sub(r"\b(ideal|perfect|constant|fixed)\b", "non-ideal/variable", assumption, flags=re.I)
                candidates.append(RelaxationCandidate(original_assumption=assumption, alternative=alt, rationale="Test whether the result depends on an idealization.", expected_effect="Recompute the model with the relaxed parameter/behavior."))
        for c in problem.constraints:
            if c.kind in {ConstraintKind.technology, ConstraintKind.material, ConstraintKind.manufacturing, ConstraintKind.economic}:
                candidates.append(RelaxationCandidate(original_assumption=c.expression, alternative="Replace the present-day limitation with a broader design/resource envelope.", rationale="These constraints are contingent rather than fundamental by default.", expected_effect="Search alternative mechanisms, materials, processes or budgets."))
        return candidates
