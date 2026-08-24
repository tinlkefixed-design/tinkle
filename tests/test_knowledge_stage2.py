from tinkle.knowledge.engine import KnowledgeEngine
from tinkle.knowledge.schemas import KnowledgeDocument, KnowledgeQuery, SearchMode, SourceProfile

def test_source_quality_is_part_of_evidence():
    e=KnowledgeEngine(); e.ingest(KnowledgeDocument(title='paper',source='doi:test',content='A reproducible experiment supports this result.',source_profile=SourceProfile(authority=.95,reproducibility=.95,evidence_quality=.9,independence=.9,relevance=.9)))
    out=e.search(KnowledgeQuery(query='reproducible experiment result'))
    assert out.evidence and out.evidence[0].source_profile.authority == .95
    assert out.claims and out.claims[0].evidence_refs

def test_failure_search_mode_prioritizes_failures():
    e=KnowledgeEngine(); e.ingest(KnowledgeDocument(title='a',source='a',content='The method failed under high pressure.')); e.ingest(KnowledgeDocument(title='b',source='b',content='The method works under normal pressure.'))
    out=e.search(KnowledgeQuery(query='method pressure',mode=SearchMode.failure))
    assert out.evidence and 'failed' in out.evidence[0].text.lower()

def test_contradiction_mode_can_surface_conflict():
    e=KnowledgeEngine(); e.ingest(KnowledgeDocument(title='a',source='a',content='The intervention supports performance.')); e.ingest(KnowledgeDocument(title='b',source='b',content='The intervention fails and has no effect.'))
    out=e.search(KnowledgeQuery(query='intervention performance',mode=SearchMode.contradiction,top_k=5))
    assert out.status == 'CONFLICTED'
