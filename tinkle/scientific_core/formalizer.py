from __future__ import annotations
import re
from .schemas import ScientificProblem, ScientificProblemGraph, Variable, Constraint, ConstraintKind
from .domain_classifier import DomainClassifier

class ProblemFormalizer:
    def __init__(self, classifier: DomainClassifier | None = None): self.classifier=classifier or DomainClassifier()
    def formalize(self, prompt: str, *, context: dict | None = None) -> tuple[ScientificProblem, ScientificProblemGraph]:
        text=' '.join(prompt.split()); ctx=context or {}
        domains=ctx.get('domains') or self.classifier.classify(text)
        variables=[]
        for name, unit in re.findall(r'\b([A-Za-z][A-Za-z0-9_]*)\s*(?:\(|=)\s*[-+]?\d+(?:\.\d+)?\s*([A-Za-z]+)\b', text):
            variables.append(Variable(name=name, symbol=name, unit=unit, role='input'))
        assumptions=list(ctx.get('assumptions', [])); known=list(ctx.get('known_laws', []))
        constraints=[Constraint(expression=c, kind=ConstraintKind.unknown) for c in ctx.get('constraints', [])]
        problem=ScientificProblem(objective=text, domains=domains, variables=variables, inputs=variables.copy(), assumptions=assumptions, known_laws=known, constraints=constraints, provenance={'origin':'natural_language','raw_prompt':prompt})
        nodes=[{'id':str(problem.id),'type':'Goal','label':problem.objective}]
        edges=[]
        for v in variables:
            vid=str(v.id); nodes.append({'id':vid,'type':'Variable','label':v.name,'unit':v.unit}); edges.append({'source':str(problem.id),'target':vid,'relation':'depends_on'})
        for c in constraints:
            cid=str(c.id); nodes.append({'id':cid,'type':'Constraint','label':c.expression}); edges.append({'source':str(problem.id),'target':cid,'relation':'constrained_by'})
        graph=ScientificProblemGraph(problem_id=problem.id,nodes=nodes,edges=edges)
        return problem,graph
