from __future__ import annotations
from itertools import combinations
from .schemas import CrossDomainRequest,CrossDomainResult,Principle

class CrossDomainInnovationEngine:
    """Extracts abstract functions/mechanisms and maps them across domains; analogy is never treated as proof."""
    def generate(self, req: CrossDomainRequest)->CrossDomainResult:
        obs=[o for o in req.observations if o.domain.strip() and o.mechanism.strip() and o.function.strip()]
        pairs=list(combinations(obs,2)); principles=[]; seen=set()
        for left,right in pairs:
            if left.domain.strip().lower()==right.domain.strip().lower(): continue
            key=tuple(sorted((left.function.strip().lower(),right.function.strip().lower())))
            if key in seen: continue
            seen.add(key)
            name=f'{left.function.strip()} ↔ {right.function.strip()}'
            abstract=f'Use the abstract function "{left.function.strip()}" as a transferable mechanism pattern, while preserving target-domain constraints.'
            mapping=f'Translate {left.domain} mechanism "{left.mechanism}" and {right.domain} mechanism "{right.mechanism}" into target domain {req.target_domain}.'
            constraints=list(dict.fromkeys(left.constraints+right.constraints))
            refs=list(dict.fromkeys(left.evidence_refs+right.evidence_refs))
            principles.append(Principle(name=name,abstract_principle=abstract,source_domains=[left.domain,right.domain],target_domain=req.target_domain,mapping=mapping,mechanism_mapping=f'{left.mechanism} -> abstract function -> {right.mechanism} -> target-domain mechanism',constraints=constraints,verification_required=['mechanism mapping','mathematical consistency','constraint analysis','simulation or experiment'],provenance={'source':'INFERRED','evidence_refs':refs,'analogy_is_not_proof':True}))
            if len(principles)>=req.max_principles: break
        return CrossDomainResult(problem=req.problem,principles=principles,domain_pairs_considered=len(pairs),limitations=['Cross-domain transfer is an inferred candidate principle, not proof of function.','Evidence is preserved but not upgraded by analogy.','Target-domain validation requires mathematical, constraint and simulation/experimental testing.'])
