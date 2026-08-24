from __future__ import annotations
from tinkle.knowledge.engine import KnowledgeEngine
from tinkle.knowledge.ingestion import DocumentIngestor
from tinkle.knowledge.schemas import KnowledgeDocument, SourceProfile
class KnowledgePipeline:
    def __init__(self, engine: KnowledgeEngine, ingestor: DocumentIngestor | None = None): self.engine=engine; self.ingestor=ingestor or DocumentIngestor()
    def ingest_text(self,title,source,content,metadata=None,source_profile=None):
        doc=KnowledgeDocument(title=title,source=source,content=content,metadata=metadata or {},source_profile=source_profile or SourceProfile()); return self.engine.ingest(doc)
    def ingest_path(self,path,metadata=None): return self.engine.ingest(self.ingestor.ingest_path(path,metadata=metadata))
