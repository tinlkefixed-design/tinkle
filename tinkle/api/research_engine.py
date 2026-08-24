from fastapi import APIRouter, Depends, HTTPException
from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.core.schemas import Permission
from tinkle.api.knowledge import engine as knowledge_engine
from tinkle.api.provenance import service as provenance_service
from tinkle.api.guardian import system as guardian_system
from tinkle.api.simulation_engine import engine as simulation_engine
from tinkle.research_engine import ResearchEngine, ResearchRequest, ResearchResult, DuckDuckGoSearchProvider

router = APIRouter(prefix="/api/v1/research", tags=["research-engine"])
_search_provider = DuckDuckGoSearchProvider()
system = ResearchEngine(knowledge_engine, provenance_service, guardian_system, simulation_engine, external_search=_search_provider, external_fetch=_search_provider.fetch)

@router.post("/run", response_model=ResearchResult)
def run(req: ResearchRequest, p: Principal = Depends(principal_from_key)):
    require(p, Permission.execute)
    try:
        return system.research(req)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
