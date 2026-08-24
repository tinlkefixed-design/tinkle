from tinkle.provenance.schemas import ProvenanceQuery, ProvenanceRecord, ProvenanceReport
from tinkle.provenance.store import ProvenanceStore

class ProvenanceService:
    def __init__(self, store: ProvenanceStore):
        self.store = store

    def record(self, record: ProvenanceRecord) -> ProvenanceRecord:
        return self.store.add(record)

    def report(self, query: ProvenanceQuery) -> ProvenanceReport:
        records = self.store.search(query.claim)
        return ProvenanceReport(
            claim=query.claim,
            records=records,
            confidence=self.store.confidence(records),
            status=self.store.effective_status(records),
        )
