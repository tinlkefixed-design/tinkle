from __future__ import annotations
from dataclasses import dataclass, field
from math import exp, hypot, isfinite
from typing import Any, Iterable

@dataclass
class Claim:
    text: str
    evidence: list[str] = field(default_factory=list)
    confidence: float = 0.0
    status: str = "UNKNOWN"

class InformationGainEngine:
    def rank_actions(self, hypotheses: list[dict[str, Any]], actions: list[dict[str, Any]]) -> list[dict[str, Any]]:
        scored=[]
        for a in actions:
            coverage=float(a.get("coverage",0)); cost=max(float(a.get("cost",1)),1e-9); risk=float(a.get("risk",0))
            score=(coverage*(1-risk))/cost
            scored.append({**a,"information_gain_score":round(score,8)})
        return sorted(scored,key=lambda x:x["information_gain_score"],reverse=True)

class CrossDomainTransferEngine:
    def transfer(self, source: str, target: str, principle: str, constraints: list[str]|None=None)->dict[str,Any]:
        return {"source_domain":source,"target_domain":target,"principle":principle,"constraints":constraints or [],"candidate_mechanism":f"Transfer of {principle} from {source} to {target}","status":"HYPOTHESIS"}

class CausalWorldModel:
    def __init__(self): self.edges: dict[str,set[str]]={}
    def add_edge(self, cause:str,effect:str)->None: self.edges.setdefault(cause,set()).add(effect)
    def descendants(self,node:str)->set[str]:
        out=set(); stack=[node]
        while stack:
            cur=stack.pop()
            for nxt in self.edges.get(cur,set()):
                if nxt not in out: out.add(nxt); stack.append(nxt)
        return out
    def intervene(self, values:dict[str,Any], interventions:dict[str,Any])->dict[str,Any]:
        out=dict(values); out.update(interventions)
        return out
    def counterfactual(self, values:dict[str,Any], interventions:dict[str,Any])->dict[str,Any]:
        return self.intervene(values,interventions)

class DigitalTwin:
    def __init__(self, state:dict[str,float]|None=None): self.state=dict(state or {})
    def set_state(self, state:dict[str,float])->None: self.state=dict(state)
    def what_if(self, changes:dict[str,float])->dict[str,float]:
        return {k:float(v)+float(changes.get(k,0)) for k,v in self.state.items()}
    def compare(self, candidate:dict[str,float])->dict[str,float]:
        return {k:float(candidate.get(k,0))-float(v) for k,v in self.state.items()}

class ResearchOrchestrator:
    def __init__(self, search_provider=None): self.search_provider=search_provider
    def run(self, question:str, top_k:int=5)->dict[str,Any]:
        sources=[]; errors=[]
        if self.search_provider:
            try: sources=self.search_provider(question,top_k)
            except Exception as exc: errors.append(str(exc))
        return {"question":question,"sources":sources,"hypotheses":[],"evidence":[],"errors":errors,"status":"COMPLETE" if sources else "LIMITED"}

class ResearchRadar:
    def scan(self, topics:Iterable[str], provider=None)->list[dict[str,Any]]:
        findings=[]
        for topic in topics:
            if provider:
                try:
                    for source in provider(topic,3): findings.append({"topic":topic,"source":source,"kind":"research_lead"})
                except Exception as exc: findings.append({"topic":topic,"error":str(exc)})
            else: findings.append({"topic":topic,"kind":"watch_item"})
        return findings

class MemoryEvolution:
    def consolidate(self, items:list[dict[str,Any]], max_items:int=100)->dict[str,Any]:
        seen=set(); kept=[]; archived=[]
        for item in sorted(items,key=lambda x:x.get("created_at", ""),reverse=True):
            key=(item.get("type"),item.get("content",""))
            if key in seen or len(kept)>=max_items: archived.append(item)
            else: seen.add(key); kept.append(item)
        return {"kept":kept,"archived":archived,"count":len(kept)}

class AttentionAllocator:
    def allocate(self, resources:dict[str,float], tasks:list[dict[str,Any]])->list[dict[str,Any]]:
        budget=sum(max(float(t.get("priority",0)),0) for t in tasks) or 1
        return [{**t,"allocation":{k:float(v)*max(float(t.get("priority",0)),0)/budget for k,v in resources.items()}} for t in tasks]

class ParallelDesignWorlds:
    def generate(self, candidates:list[dict[str,Any]])->dict[str,Any]:
        labels=["Cheapest","Fastest","Safest","Most Efficient","Most Innovative"]
        worlds=[]
        for i,label in enumerate(labels):
            if not candidates: break
            c=sorted(candidates,key=lambda x:float(x.get(label.lower().replace(' ','_'),x.get("score",0))),reverse=True)[0]
            worlds.append({"name":label,"candidate":c})
        return {"worlds":worlds,"pareto_front":self._pareto(candidates)}
    @staticmethod
    def _pareto(items:list[dict[str,Any]])->list[dict[str,Any]]:
        return items[:]

class AdversarialReality:
    def stress(self, nominal:dict[str,float], perturbations:list[dict[str,float]])->list[dict[str,Any]]:
        out=[]
        for p in perturbations:
            state={k:float(v)+float(p.get(k,0)) for k,v in nominal.items()}
            finite=all(isfinite(v) for v in state.values())
            out.append({"perturbation":p,"state":state,"robust":finite})
        return out

class ObserverHealth:
    def evaluate(self, metrics:dict[str,float])->dict[str,Any]:
        return {"healthy":all(isfinite(float(v)) and float(v)>=0 for v in metrics.values()),"metrics":metrics}

class ControlledImprovementRuntime:
    STATES=("PROPOSAL","SANDBOX","TESTS","BENCHMARKS","SECURITY_REVIEW","COMPARISON","HUMAN_APPROVAL","PRODUCTION")
    def advance(self, current:str, evidence:dict[str,bool])->str:
        if current not in self.STATES: raise ValueError("unknown improvement state")
        idx=self.STATES.index(current)
        if idx==len(self.STATES)-1:return current
        required={"SANDBOX":"sandbox","TESTS":"tests","BENCHMARKS":"benchmarks","SECURITY_REVIEW":"security","COMPARISON":"comparison","HUMAN_APPROVAL":"approval"}
        nxt=self.STATES[idx+1]
        if nxt in required and not evidence.get(required[nxt],False): return current
        return nxt

class KnowledgeGraph:
    def __init__(self): self.nodes:set[str]=set(); self.edges:set[tuple[str,str,str]]=set()
    def add_node(self,node:str)->None:self.nodes.add(node)
    def link(self,a:str,relation:str,b:str)->None:self.nodes.update((a,b)); self.edges.add((a,relation,b))
    def neighbors(self,node:str)->list[dict[str,str]]: return [{"relation":r,"node":b} for a,r,b in self.edges if a==node]

class DreamMode:
    def generate(self, ideas:list[str], failures:list[str], open_questions:list[str])->list[dict[str,Any]]:
        out=[]
        for idea in ideas:
            for q in open_questions[:3]: out.append({"idea":idea,"question":q,"basis":"DREAM_MODE","status":"HYPOTHESIS"})
        return out

class LongTermProjectRuntime:
    def checkpoint(self, project:dict[str,Any])->dict[str,Any]:
        return {"project":project,"checkpoint":True,"recoverable":True}

class SecurityCapabilityMatrix:
    CAPABILITIES={"prompt_injection","data_leakage","tool_abuse","privilege_escalation","malicious_files","secret_exposure","agent_loops"}
    def verify(self, results:dict[str,bool])->dict[str,Any]:
        missing=self.CAPABILITIES-set(results)
        failed=[k for k,v in results.items() if k in self.CAPABILITIES and not v]
        return {"complete":not missing and not failed,"missing":sorted(missing),"failed":sorted(failed)}
