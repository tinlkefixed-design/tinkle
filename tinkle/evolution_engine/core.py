from __future__ import annotations
import random, math
from typing import Any
from pydantic import BaseModel, Field

class Candidate(BaseModel):
    genome: list[float]
    objectives: list[float] = Field(default_factory=list)
    feasible: bool = True

class EvolutionRequest(BaseModel):
    seeds: list[list[float]] = Field(min_length=1)
    generations: int = Field(10, ge=1, le=1000)
    population_size: int = Field(20, ge=2, le=5000)
    mutation_sigma: float = Field(0.1, gt=0, le=100)
    seed: int = 0
    maximize: list[bool] = Field(min_length=1)

class EvolutionResult(BaseModel):
    status: str
    pareto_front: list[Candidate]
    generation_count: int
    evaluations: int
    seed: int
    limitations: list[str] = Field(default_factory=list)

def dominates(a: Candidate,b: Candidate,maximize:list[bool])->bool:
    better=False
    for x,y,m in zip(a.objectives,b.objectives,maximize):
        if m:
            if x<y:return False
            better |= x>y
        else:
            if x>y:return False
            better |= x<y
    return better

def pareto(pop,maximize): return [x for x in pop if not any(dominates(y,x,maximize) for y in pop if y is not x)]

class EvolutionEngine:
    def run(self, req: EvolutionRequest)->EvolutionResult:
        rng=random.Random(req.seed)
        if any(len(g)!=len(req.seeds[0]) for g in req.seeds): raise ValueError('all genomes must have equal length')
        pop=[Candidate(genome=list(g)) for g in req.seeds]
        while len(pop)<req.population_size: pop.append(Candidate(genome=list(rng.choice(req.seeds))))
        evaluations=0
        def evaluate(c):
            # Generic multi-objective baseline: minimize squared magnitude and maximize diversity proxy.
            c.objectives=[-sum(x*x for x in c.genome), sum(abs(x) for x in c.genome)]
        for g in range(req.generations):
            for c in pop: evaluate(c); evaluations+=1
            front=pareto(pop,req.maximize)
            pool=front or pop
            children=[]
            while len(children)+len(front)<req.population_size:
                p=rng.choice(pool); genome=[x+rng.gauss(0,req.mutation_sigma) for x in p.genome]
                children.append(Candidate(genome=genome))
            pop=front+children
        for c in pop: evaluate(c); evaluations+=1
        front=pareto(pop,req.maximize)
        return EvolutionResult(status='EVOLUTION_COMPLETE',pareto_front=front,generation_count=req.generations,evaluations=evaluations,seed=req.seed,limitations=['Objective functions are generic defaults; scientific campaigns must supply domain-validated objectives and constraints.','This engine does not establish scientific novelty or physical validity.'])
