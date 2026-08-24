from __future__ import annotations
from itertools import product
from .schemas import InventionRequest, InventionResult, Invention, DesignGenome, NoveltyClass

class InventionGenerationEngine:
    """Deterministic design-space generator. It generates candidates; it never claims novelty as fact."""
    def generate(self, req: InventionRequest) -> InventionResult:
        architectures=req.architectures or ['modular_system']
        mechanisms=req.mechanisms or ['direct_conversion']
        materials=req.materials or ['unspecified_material']
        processes=req.processes or ['standard_manufacturing']
        algorithms=req.algorithms or [None]
        space=len(architectures)*len(mechanisms)*len(materials)*len(processes)*len(algorithms)
        candidates=[]
        seen=set()
        for a,m,mat,proc,algo in product(architectures,mechanisms,materials,processes,algorithms):
            key=(a.strip().lower(),m.strip().lower(),mat.strip().lower(),proc.strip().lower(),str(algo).strip().lower())
            if key in seen: continue
            seen.add(key)
            novelty=self._novelty(a,m,mat,proc,algo,req.known_designs)
            genome=DesignGenome(architecture=a,materials=[mat],mechanisms=[m],parameters={},energy_flow=[m],control=[algo] if algo else [],geometry=[a],interfaces=[a])
            candidates.append(Invention(title=f'{a} + {m}',problem=req.problem,architecture=a,mechanism=m,materials=[mat],process=proc,algorithm=algo,genome=genome,novelty=novelty,novelty_rationale=[f'Novelty class is a search classification, not a patentability determination.', f'Compared against {len(req.known_designs)} caller-supplied known designs.'],assumptions=req.constraints,status='CANDIDATE',provenance={'generator':'InventionGenerationEngine','source':'CALCULATED'}))
            if len(candidates)>=req.max_candidates: break
        return InventionResult(problem=req.problem,candidates=candidates,search_space_size=space,generated_count=len(candidates),limitations=['Candidates are generated from caller-supplied design primitives.','No candidate is asserted to be scientifically valid, novel in the world, or patentable.','Real engineering feasibility requires constraints, simulation, prior-art review and validation.'])

    def _novelty(self,a,m,mat,p,algo,known):
        text=' '.join([a,m,mat,p,str(algo)]).lower()
        exact=[x.lower() for x in known]
        if any(text==x or (a.lower() in x and m.lower() in x and mat.lower() in x) for x in exact): return NoveltyClass.KNOWN
        if any(a.lower() in x for x in exact): return NoveltyClass.IMPROVEMENT
        if len({a.lower(),m.lower(),mat.lower(),p.lower()})>=3: return NoveltyClass.COMBINATION
        return NoveltyClass.NOVEL_CANDIDATE
