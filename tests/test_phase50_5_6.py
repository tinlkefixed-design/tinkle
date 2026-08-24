from pathlib import Path
from tinkle.knowledge.engine import KnowledgeEngine
from tinkle.knowledge.pipeline import KnowledgePipeline
from tinkle.research_engine.web_provider import DuckDuckGoSearchProvider


def test_knowledge_chunking_and_bm25():
    engine = KnowledgeEngine()
    KnowledgePipeline(engine).ingest_text("Doc", "memory://doc", "Alpha beta gamma.\n\nDelta beta system.")
    result = engine.search(__import__('tinkle.knowledge.schemas', fromlist=['KnowledgeQuery']).KnowledgeQuery(query="beta system"))
    assert result.evidence
    assert result.status == "SUPPORTED"


def test_pdf_ingestion(tmp_path: Path):
    import fitz
    path = tmp_path / "sample.pdf"
    doc = fitz.open(); page = doc.new_page(); page.insert_text((72,72), "Tinkle scientific evidence"); doc.save(path); doc.close()
    chunks = KnowledgePipeline(KnowledgeEngine()).ingest_path(str(path))
    assert chunks and "Tinkle" in chunks[0].text


def test_web_provider_parses_mock_html(monkeypatch):
    from io import BytesIO
    class Resp:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def read(self): return b'<a href="https://example.com/a">Example result</a><a href="https://example.com/b">Second</a>'
    monkeypatch.setattr('tinkle.research_engine.web_provider.urlopen', lambda *a, **k: Resp())
    results = DuckDuckGoSearchProvider()("test", 2)
    assert len(results) == 2
    assert results[0].metadata["external"] is True
