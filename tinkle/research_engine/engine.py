from __future__ import annotations
from typing import Any, Callable
from tinkle.guardian import Guardian, GuardianRequest
from tinkle.knowledge.engine import KnowledgeEngine
from tinkle.knowledge.schemas import KnowledgeQuery, SearchMode
from tinkle.provenance.service import ProvenanceService
from tinkle.provenance.schemas import ProvenanceQuery
from tinkle.research_engine.schemas import ResearchEvidence,ResearchRequest,ResearchResult,ResearchSource,ResearchStage
from tinkle.simulation_engine import SimulationEngine,SimulationRequest

class ResearchEngine:
    def __init__(self,knowledge,provenance,guardian,simulation,external_search=None,external_fetch=None):
        self.knowledge=knowledge; self.provenance=provenance; self.guardian=guardian; self.simulation=simulation; self.external_search=external_search; self.external_fetch=external_fetch
    def research(self,request):
        stages=list(ResearchStage); provider_error=None; search_sources=[]
        if self.external_search:
            try: search_sources=self.external_search(request.question,request.top_k)
            except Exception as exc: provider_error=f'External search provider failed: {type(exc).__name__}: {exc}'
        sources=list(search_sources); source_ids={s.source:s.id for s in sources}; evidence=[]
        # Local knowledge is the first evidence layer.
        ka=self.knowledge.search(KnowledgeQuery(query=request.question,top_k=request.top_k,mode=request.search_mode))
        for item in ka.evidence:
            sid=source_ids.get(item.source)
            if sid is None:
                src=ResearchSource(source=item.source,title=item.source,metadata=item.metadata,profile=item.source_profile); sources.append(src); source_ids[item.source]=src.id; sid=src.id
            evidence.append(ResearchEvidence(source_id=sid,source=item.source,text=item.text,score=item.score,status='SUPPORTED',evidence_type='SOURCE',metadata=item.metadata))
        # Deep/negative/prior-art modes may fetch public search leads. Fetched text is not auto-verified.
        if self.external_fetch and request.search_mode in {SearchMode.deep,SearchMode.contradiction,SearchMode.failure,SearchMode.prior_art,SearchMode.negative}:
            for src in list(sources)[:request.top_k]:
                if src.fetched: continue
                try:
                    text=self.external_fetch(src); src.fetched=True
                    if text:
                        evidence.append(ResearchEvidence(source_id=src.id,source=src.source,text=text[:12000],score=round(src.profile.evidence_quality*src.profile.relevance,4),status='UNVERIFIED',evidence_type='SOURCE',metadata={'fetched':True,'search_mode':request.search_mode.value}))
                except Exception as exc: src.metadata['fetch_error']=f'{type(exc).__name__}: {exc}'
        knowledge=[e.text for e in evidence]; hypotheses=list(request.hypotheses); analysis=self._analyze(request.question,evidence,hypotheses,request.search_mode); simulation=self._simulate(request)
        criticism_result=self.guardian.review(GuardianRequest(result='\n'.join(analysis) or 'No analysis was produced.',evidence=[e.text for e in evidence],assumptions=hypotheses,known_limitations=self._limitations(simulation)))
        verification=self._verify(evidence,sources,request.question); confidence=self._confidence(evidence,verification); status='VERIFIED' if verification['status']=='VERIFIED' else ('SUPPORTED' if evidence else 'UNKNOWN')
        report=self._report(request.question,evidence,hypotheses,analysis,simulation,criticism_result,verification,request.search_mode)
        return ResearchResult(question=request.question,stages=stages,sources=sources,evidence=evidence,knowledge=knowledge,hypotheses=hypotheses,analysis=analysis,simulation=simulation,criticism=criticism_result.model_dump(mode='json'),verification=verification,report=report,confidence=confidence,status=status,limitations=self._limitations(simulation)+(['No external search provider is configured.'] if not self.external_search else [])+([provider_error] if provider_error else []))
    @staticmethod
    def _analyze(question,evidence,hypotheses,mode):
        if not evidence:return [f'No indexed or fetched evidence matched the research question: {question}']
        out=[f'Found {len(evidence)} evidence item(s) using {mode.value} search.','Evidence sources represented: '+str(len({e.source for e in evidence}))+'.']
        if hypotheses:out.append(f'The research includes {len(hypotheses)} hypothesis/hypotheses requiring verification.')
        if mode==SearchMode.contradiction:out.append('Contradiction mode explicitly preserves disagreement rather than selecting a winner.')
        if mode in {SearchMode.failure,SearchMode.negative}:out.append('Failure/negative mode prioritizes evidence containing limitations, failed outcomes, or null results.')
        if mode==SearchMode.prior_art:out.append('Prior-art mode is a discovery aid, not a legal novelty or patentability opinion.')
        return out
    def _simulate(self,request):
        if not request.simulate:return {'status':'NOT_REQUESTED','reason':'Simulation was not requested for this research task.'}
        if not request.simulation:return {'status':'UNAVAILABLE','reason':'Simulation was requested but no simulation model/parameters were supplied.'}
        try:return {'status':'COMPLETE','result':self.simulation.simulate(SimulationRequest(**request.simulation)).model_dump(mode='json')}
        except (TypeError,ValueError) as exc:return {'status':'FAILED','reason':str(exc)}
    @staticmethod
    def _limitations(simulation):return [] if simulation.get('status')=='COMPLETE' else ['No completed simulation result is part of this research report.']
    def _verify(self,evidence,sources,question):
        records=[]
        for e in evidence: records.extend(self.provenance.report(ProvenanceQuery(claim=e.text)).records)
        if any(r.status.value=='disputed' for r in records):return {'status':'DISPUTED','reason':'At least one matching provenance record is disputed.','sources':len(sources)}
        if any(r.status.value=='verified' for r in records):return {'status':'VERIFIED','reason':'At least one matching provenance record is verified.','sources':len(sources)}
        return ({'status':'SUPPORTED','reason':'Evidence exists, but no matching verified provenance record was found.','sources':len(sources)} if evidence else {'status':'UNKNOWN','reason':'No evidence was found.','question':question})
    @staticmethod
    def _confidence(evidence,verification):
        if not evidence:return 0.0
        base=max(e.score for e in evidence)
        return round(min(1,base+.15) if verification['status']=='VERIFIED' else base*.5 if verification['status']=='DISPUTED' else base,4)
    @staticmethod
    def _report(question,evidence,hypotheses,analysis,simulation,criticism,verification,mode):
        lines=[f'Research question: {question}',f'Search mode: {mode.value}',f'Verification status: {verification["status"]}',f'Evidence items: {len(evidence)}']; lines.extend(f'Analysis: {x}' for x in analysis)
        if hypotheses:lines.append('Hypotheses remain hypotheses unless appropriate evidence promotes them.')
        lines += [f'Simulation status: {simulation.get("status")}',f'Criticism: {criticism.conclusion}']; return '\n'.join(lines)
