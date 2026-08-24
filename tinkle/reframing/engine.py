import re
from tinkle.reframing.schemas import ReframingRequest, ReframingResult, Representation, RepresentationCandidate

class ProblemReframingEngine:
    KEYWORDS = {
        Representation.mathematical: ["equation","calculate","formula","number","rate","probability","solve"],
        Representation.physical: ["force","mass","energy","motion","temperature","pressure","velocity"],
        Representation.causal: ["cause","why","effect","leads to","because","intervention"],
        Representation.graph: ["network","node","edge","relationship","dependency","graph"],
        Representation.information: ["information","signal","entropy","data","encoding","communication"],
        Representation.engineering: ["design","system","component","material","sensor","manufacture","prototype"],
        Representation.economic: ["cost","price","profit","budget","market","economic"],
        Representation.optimization: ["optimize","maximize","minimize","best","tradeoff"],
        Representation.constraint: ["constraint","limit","requirement","must","cannot","capacity"],
        Representation.algorithmic: ["algorithm","code","procedure","steps","complexity","compute"],
    }

    def _elements(self, problem: str) -> list[str]:
        parts = [x.strip() for x in re.split(r"[,;\n]", problem) if x.strip()]
        return parts[:12]

    def reframe(self, request: ReframingRequest) -> ReframingResult:
        p = request.problem.lower()
        candidates=[]
        elements=self._elements(request.problem)
        for rep, words in self.KEYWORDS.items():
            hits=sum(1 for w in words if w in p)
            score=min(1.0, hits/3)
            rationale=("keyword and semantic cues indicate this representation" if hits else "no strong direct cue; retained as an alternative")
            candidates.append(RepresentationCandidate(representation=rep,score=round(score,4),
                                                       rationale=rationale,extracted_elements=elements[:5]))
        # Deterministic tie-break priority favors representations that directly
        # express an explicit objective ("optimize", "maximize", "minimize").
        priority=[Representation.optimization, Representation.constraint,
                  Representation.mathematical, Representation.engineering,
                  Representation.causal, Representation.graph,
                  Representation.information, Representation.physical,
                  Representation.economic, Representation.algorithmic]
        candidates.sort(key=lambda x:(-x.score, priority.index(x.representation)))
        selected=candidates[0]
        if selected.score==0:
            selected=next(x for x in candidates if x.representation==Representation.algorithmic)
        assumptions=list(request.context.get("assumptions", []))
        constraints=list(request.context.get("constraints", []))
        reframed=f"Represent the problem as a {selected.representation.value} problem and make its objective, variables, constraints, and verification criteria explicit."
        return ReframingResult(
            original_problem=request.problem,
            reframed_problem=reframed,
            candidates=candidates,
            selected_representation=selected.representation,
            assumptions=assumptions,
            constraints=constraints
        )
