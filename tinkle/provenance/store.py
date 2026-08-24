from datetime import datetime, timezone
from tinkle.provenance.schemas import ProvenanceRecord, ProvenanceStatus

class ProvenanceStore:
    def __init__(self):
        self.records: dict[str, ProvenanceRecord] = {}

    def add(self, record: ProvenanceRecord) -> ProvenanceRecord:
        self.records[str(record.id)] = record
        return record

    def all(self) -> list[ProvenanceRecord]:
        return list(self.records.values())

    def search(self, claim: str) -> list[ProvenanceRecord]:
        q = set(claim.lower().split())
        scored = []
        for r in self.records.values():
            tokens = set(r.claim.lower().split())
            overlap = len(q & tokens)
            if overlap:
                scored.append((overlap, r))
        scored.sort(key=lambda x: (-x[0], str(x[1].id)))
        return [r for _, r in scored]

    @staticmethod
    def effective_status(records: list[ProvenanceRecord]) -> ProvenanceStatus:
        if not records:
            return ProvenanceStatus.unknown
        if any(r.status == ProvenanceStatus.disputed for r in records):
            return ProvenanceStatus.disputed
        if any(r.status == ProvenanceStatus.verified for r in records):
            return ProvenanceStatus.verified
        if any(r.status == ProvenanceStatus.stale for r in records):
            return ProvenanceStatus.stale
        if any(r.status == ProvenanceStatus.provisional for r in records):
            return ProvenanceStatus.provisional
        return ProvenanceStatus.unknown

    @staticmethod
    def confidence(records: list[ProvenanceRecord]) -> float:
        if not records:
            return 0.0
        # Conservative aggregate: highest supported confidence, reduced by disputes.
        best = max(r.confidence for r in records)
        if any(r.status == ProvenanceStatus.disputed for r in records):
            best *= 0.5
        return round(best, 4)
