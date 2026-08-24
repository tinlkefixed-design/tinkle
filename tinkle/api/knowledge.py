from fastapi import APIRouter, Header, HTTPException
from tinkle.core.auth import AuthService
from tinkle.core.errors import AuthenticationError
from tinkle.knowledge.engine import KnowledgeEngine
from tinkle.knowledge.pipeline import KnowledgePipeline
from tinkle.knowledge.schemas import KnowledgeDocument, KnowledgeQuery

router = APIRouter(prefix="/api/v1/knowledge")
auth = AuthService()
engine = KnowledgeEngine()
pipeline = KnowledgePipeline(engine)

def principal(key):
    try: return auth.authenticate(key)
    except AuthenticationError as exc: raise HTTPException(401, "Invalid or missing API key") from exc

@router.post("/documents")
def ingest(doc: KnowledgeDocument, x_api_key: str|None = Header(default=None)):
    principal(x_api_key)
    chunks = engine.ingest(doc)
    return {"document": doc, "chunks": chunks}

@router.post("/search")
def search(q: KnowledgeQuery, x_api_key: str|None = Header(default=None)):
    principal(x_api_key)
    return engine.search(q)
