from tinkle.reality_engine import (
    ClaimKind,
    ClaimStatus,
    ParameterSweepRequest,
    ResearchProjectState,
    RealityEngine,
)


def test_claim_classification_marks_unvalidated_when_evidence_missing():
    engine = RealityEngine()
    claim = engine.classify_claim("This design can support 500 kg.", kind=ClaimKind.HYPOTHESIS)
    assert claim.kind == ClaimKind.HYPOTHESIS
    assert claim.status == ClaimStatus.UNVALIDATED
    assert claim.confidence == 0.0


def test_unknown_values_remain_unknown_and_are_propagated():
    engine = RealityEngine()
    value = engine.classify_value(None, source="missing", notes="No measurement available")
    assert value.status == ClaimStatus.UNKNOWN
    report = engine.check_assumptions({"material_density": value})
    assert report["missing_values"]
    assert report["status"] == "UNKNOWN"


def test_parameter_sweep_detects_dominant_parameter():
    engine = RealityEngine()
    sweep = engine.parameter_sweep(
        ParameterSweepRequest(
            base_values={"A": 1.0, "B": 2.0},
            variations={
                "A": [-0.05, 0.0, 0.05],
                "B": [-0.10, 0.0, 0.10],
            },
            base_output=2.1,
            model=lambda params: params["A"] * params["B"] + 0.1,
        )
    )
    assert sweep["dominant_parameter"] in {"A", "B"}
    assert len(sweep["results"]) >= 2


def test_project_state_serializes_and_recovers():
    project = ResearchProjectState(idea="Design a compact exosuit")
    data = project.model_dump()
    restored = ResearchProjectState.model_validate(data)
    assert restored.idea == "Design a compact exosuit"
    assert restored.claims == []


def test_reality_check_reveals_missing_evidence_and_assumptions():
    engine = RealityEngine()
    result = engine.validate_claim(
        "The structure supports 500 kg.",
        evidence=[],
        assumptions=["material strength is constant"],
        required_parameters=["yield_strength", "mass"],
        known_values={"mass": 120.0},
        simulation=None,
    )
    assert result["status"] == "UNVALIDATED"
    assert "yield_strength" in result["unknown"]
    assert result["assumptions"]
