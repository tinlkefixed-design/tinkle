from __future__ import annotations

from collections import defaultdict
from typing import Any, Callable

from tinkle.reality_engine.schemas import (
    Assumption,
    Claim,
    ClaimKind,
    ClaimStatus,
    KnowledgeDependencyGraph,
    ParameterSweepRequest,
    RealityCheckRequest,
    ResearchProjectState,
    ValueProvenance,
)


class RealityEngine:
    """Epistemic state engine for claims, variables, assumptions, and parameter sensitivity."""

    @staticmethod
    def classify_claim(statement: str, *, kind: ClaimKind = ClaimKind.UNKNOWN) -> Claim:
        evidence_missing = not bool(statement.strip())
        status = ClaimStatus.UNVALIDATED
        confidence = 0.0
        if kind in {ClaimKind.FACT, ClaimKind.MEASUREMENT, ClaimKind.SOURCE} and not evidence_missing:
            status = ClaimStatus.KNOWN
            confidence = 0.9
        elif kind == ClaimKind.ESTIMATE:
            status = ClaimStatus.ESTIMATED
            confidence = 0.5
        elif kind == ClaimKind.ASSUMPTION:
            status = ClaimStatus.ASSUMED
            confidence = 0.4
        elif kind == ClaimKind.INFERENCE:
            status = ClaimStatus.INFERRED
            confidence = 0.6
        elif kind == ClaimKind.SIMULATION:
            status = ClaimStatus.SIMULATED
            confidence = 0.7
        elif kind == ClaimKind.HYPOTHESIS:
            status = ClaimStatus.UNVALIDATED
            confidence = 0.0
        elif kind == ClaimKind.SPECULATION:
            status = ClaimStatus.UNKNOWN
            confidence = 0.0
        return Claim(
            statement=statement,
            kind=kind,
            status=status,
            confidence=confidence,
            dependencies=[],
        )

    @staticmethod
    def classify_value(value: Any, *, source: str | None = None, notes: str | None = None) -> ValueProvenance:
        if value is None:
            return ValueProvenance(name="unknown", value=None, source=source, status=ClaimStatus.UNKNOWN, confidence=0.0, notes=notes)
        if source in {"measured", "measurement", "observed"}:
            return ValueProvenance(name="measured", value=value, source=source, status=ClaimStatus.MEASURED, confidence=0.95, notes=notes)
        if source in {"source", "source_backed", "backed"}:
            return ValueProvenance(name="source_backed", value=value, source=source, status=ClaimStatus.SOURCE_BACKED, confidence=0.85, notes=notes)
        if source in {"estimated", "estimate"}:
            return ValueProvenance(name="estimated", value=value, source=source, status=ClaimStatus.ESTIMATED, confidence=0.55, notes=notes)
        if source in {"assumption", "assumed"}:
            return ValueProvenance(name="assumed", value=value, source=source, status=ClaimStatus.ASSUMED, confidence=0.4, notes=notes)
        if source in {"simulated", "simulation"}:
            return ValueProvenance(name="simulated", value=value, source=source, status=ClaimStatus.SIMULATED, confidence=0.7, notes=notes)
        return ValueProvenance(name="unknown", value=value, source=source, status=ClaimStatus.UNVALIDATED, confidence=0.0, notes=notes)

    @staticmethod
    def validate_claim(
        claim: str,
        *,
        evidence: list[str],
        assumptions: list[str],
        required_parameters: list[str],
        known_values: dict[str, Any],
        simulation: dict[str, Any] | None,
    ) -> dict[str, Any]:
        unknown = [name for name in required_parameters if name not in known_values or known_values[name] is None]
        status = "UNVALIDATED"
        if not evidence:
            status = "UNVALIDATED"
        elif unknown:
            status = "UNVALIDATED"
        elif simulation is not None:
            status = "SIMULATED"
        else:
            status = "KNOWN"
        return {
            "claim": claim,
            "evidence": evidence,
            "assumptions": assumptions,
            "required_parameters": required_parameters,
            "known": sorted(known_values.keys()),
            "unknown": unknown,
            "simulation": simulation,
            "status": status,
        }

    @staticmethod
    def trace_provenance(*, claim: str, dependencies: list[str] | None = None) -> dict[str, Any]:
        return {
            "claim": claim,
            "dependencies": dependencies or [],
            "status": "TRACEABLE",
        }

    @staticmethod
    def propagate_uncertainty(values: dict[str, float]) -> dict[str, Any]:
        if not values:
            return {"status": "UNKNOWN", "mean": None, "spread": None}
        mean = sum(values.values()) / len(values)
        spread = max(values.values()) - min(values.values())
        return {"status": "ESTIMATED", "mean": mean, "spread": spread}

    @staticmethod
    def check_assumptions(assumptions: dict[str, Any]) -> dict[str, Any]:
        missing_values: list[str] = []
        for name, value in assumptions.items():
            if value is None:
                missing_values.append(name)
                continue
            if isinstance(value, ValueProvenance):
                if value.status in {ClaimStatus.UNKNOWN, ClaimStatus.UNVALIDATED}:
                    missing_values.append(name)
                continue
            if hasattr(value, "status") and getattr(value, "status") in {ClaimStatus.UNKNOWN, ClaimStatus.UNVALIDATED}:
                missing_values.append(name)
        if missing_values:
            return {"status": "UNKNOWN", "missing_values": missing_values, "assumptions": list(assumptions.keys())}
        return {"status": "KNOWN", "missing_values": [], "assumptions": list(assumptions.keys())}

    @staticmethod
    def build_dependency_graph(problem: str, domains: list[str] | None = None) -> KnowledgeDependencyGraph:
        labels = domains or ["physics", "materials", "control"]
        nodes = [
            {"id": "problem", "type": "problem", "label": problem},
        ]
        for idx, domain in enumerate(labels, start=1):
            nodes.append({"id": f"domain_{idx}", "type": "domain", "label": domain})
            nodes.append({"id": f"concept_{idx}", "type": "concept", "label": f"{domain} concept"})
        edges = []
        for idx, _ in enumerate(labels, start=1):
            edges.append({"source": "problem", "target": f"domain_{idx}", "relation": "relevant_to"})
            edges.append({"source": f"domain_{idx}", "target": f"concept_{idx}", "relation": "contains"})
        return KnowledgeDependencyGraph(nodes=[__import__('tinkle.reality_engine.schemas', fromlist=['DependencyNode']).DependencyNode(**node) for node in nodes], edges=[__import__('tinkle.reality_engine.schemas', fromlist=['DependencyEdge']).DependencyEdge(**edge) for edge in edges])

    @staticmethod
    def parameter_sweep(request: ParameterSweepRequest) -> dict[str, Any]:
        if request.model is None:
            raise ValueError("A model callable is required for parameter sweep.")

        results: list[dict[str, Any]] = []
        base = dict(request.base_values)
        for name, variations in request.variations.items():
            if not variations:
                continue
            for delta in variations:
                params = dict(base)
                params[name] = base.get(name, 1.0) * (1.0 + delta)
                output = request.model(params)
                results.append({
                    "parameter": name,
                    "variation": delta,
                    "output": output,
                    "relative_change": None if request.base_output is None else (output - request.base_output) / request.base_output if request.base_output != 0 else 0.0,
                })

        if not results:
            return {"results": [], "dominant_parameter": None}

        by_param: dict[str, list[float]] = defaultdict(list)
        for item in results:
            if item["relative_change"] is not None:
                by_param[item["parameter"]].append(abs(float(item["relative_change"])))
        dominant = None
        dominant_score = -1.0
        for name, values in by_param.items():
            score = max(values) if values else 0.0
            if score > dominant_score:
                dominant = name
                dominant_score = score
        return {"results": results, "dominant_parameter": dominant, "sensitivity": {k: max(v) for k, v in by_param.items()}}


__all__ = [
    "RealityEngine",
    "Claim",
    "ClaimKind",
    "ClaimStatus",
    "Assumption",
    "ParameterSweepRequest",
    "ResearchProjectState",
    "RealityCheckRequest",
    "ValueProvenance",
]
