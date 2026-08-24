from tinkle.knowledge.engine import KnowledgeEngine
from tinkle.knowledge.schemas import KnowledgeDocument, KnowledgeQuery

def test_ingest_and_chunk():
    e=KnowledgeEngine()
    doc=KnowledgeDocument(title="T",source="test",content="Alpha science.\n\nBeta engineering.",metadata={"project_id":"p1"})
    chunks=e.ingest(doc)
    assert len(chunks)==2
    assert all(c.document_id==doc.id for c in chunks)

def test_retrieval_and_evidence():
    e=KnowledgeEngine()
    e.ingest(KnowledgeDocument(title="T",source="paper",content="Quantum computing uses qubits.",metadata={"project_id":"p"}))
    out=e.search(KnowledgeQuery(query="quantum qubits",top_k=3))
    assert out.status=="SUPPORTED"
    assert out.evidence[0].source=="paper"

def test_unknown_is_not_guess():
    e=KnowledgeEngine()
    out=e.search(KnowledgeQuery(query="unknown topic"))
    assert out.status=="UNKNOWN"
    assert out.confidence==0

def test_project_filter():
    e=KnowledgeEngine()
    e.ingest(KnowledgeDocument(title="A",source="a",content="shared science",metadata={"project_id":"a"}))
    e.ingest(KnowledgeDocument(title="B",source="b",content="shared science",metadata={"project_id":"b"}))
    out=e.search(KnowledgeQuery(query="science",project_id="b"))
    assert len(out.evidence)==1 and out.evidence[0].source=="b"
