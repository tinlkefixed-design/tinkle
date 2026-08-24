from tinkle.guardian import Guardian, GuardianCategory, GuardianRequest


def test_guardian_checks_all_blueprint_categories():
    result = Guardian().review(GuardianRequest(result="A proposed result", evidence=["source-a"]))
    assert result.status == "REVIEW_READY"
    assert result.categories_checked == list(GuardianCategory)
    assert {f.category for f in result.findings} == set(GuardianCategory)
    assert "does not certify correctness" in result.conclusion


def test_guardian_flags_missing_evidence_and_supplied_limitations():
    result = Guardian().review(
        GuardianRequest(result="Build system", known_limitations=["external model not configured"])
    )
    by_category = {f.category: f for f in result.findings}
    assert by_category[GuardianCategory.missing_data].severity == "high"
    assert "external model not configured" in by_category[GuardianCategory.model_limitations].statement


def test_guardian_preserves_explicit_assumptions():
    result = Guardian().review(
        GuardianRequest(result="Compute X", assumptions=["input is complete"], evidence=["dataset"]),
    )
    assert any("input is complete" in f.statement for f in result.findings if f.category is GuardianCategory.hidden_assumptions)
