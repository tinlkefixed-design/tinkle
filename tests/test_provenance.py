from datetime import datetime, timezone
from tinkle.provenance.schemas import ProvenanceRecord, ProvenanceQuery, ProvenanceStatus
from tinkle.provenance.service import ProvenanceService
from tinkle.provenance.store import ProvenanceStore

def test_record_contains_required_provenance_fields():
    r=ProvenanceRecord(
        claim="water boils at standard pressure",
        source="test-source",
        author="tester",
        date=datetime.now(timezone.utc),
        location="lab",
        evidence=["measurement-1"],
        confidence=.95,
        status=ProvenanceStatus.verified,
        supporting_sources=["source-a"],
        opposing_sources=["source-b"],
    )
    assert r.source=="test-source"
    assert r.confidence==.95
    assert r.supporting_sources==["source-a"]

def test_report_supports_and_aggregates():
    s=ProvenanceService(ProvenanceStore())
    s.record(ProvenanceRecord(claim="alpha result",source="a",confidence=.8,status=ProvenanceStatus.verified))
    s.record(ProvenanceRecord(claim="alpha result",source="b",confidence=.4,status=ProvenanceStatus.provisional))
    out=s.report(ProvenanceQuery(claim="alpha result"))
    assert len(out.records)==2
    assert out.status==ProvenanceStatus.verified
    assert out.confidence==.8

def test_dispute_reduces_confidence():
    s=ProvenanceService(ProvenanceStore())
    s.record(ProvenanceRecord(claim="beta result",source="a",confidence=.9,status=ProvenanceStatus.verified))
    s.record(ProvenanceRecord(claim="beta result",source="b",confidence=.8,status=ProvenanceStatus.disputed))
    out=s.report(ProvenanceQuery(claim="beta result"))
    assert out.status==ProvenanceStatus.disputed
    assert out.confidence==.45

def test_unknown_claim():
    s=ProvenanceService(ProvenanceStore())
    out=s.report(ProvenanceQuery(claim="not found"))
    assert out.status==ProvenanceStatus.unknown
    assert out.confidence==0
