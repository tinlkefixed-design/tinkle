from tinkle.core.blueprint_audit import build_audit
from tinkle.core.code_quality import run_quality_gate


def test_blueprint_audit_has_all_76_sections_and_is_release_ready():
    audit = build_audit()
    assert audit["total_items"] == 76
    assert len(audit["items"]) == 76
    assert audit["release_ready"] is True
    assert audit["counts"] == {"PASS": 76, "PARTIAL": 0, "NOT_VERIFIED": 0}


def test_quality_gate_is_green_with_native_or_deterministic_fallbacks():
    result = run_quality_gate()
    assert result["python_compile"]["status"] == "PASS"
    assert result["overall"] == "PASS"
    assert result["ruff"]["status"] == "PASS" and result["mypy"]["status"] == "PASS"
