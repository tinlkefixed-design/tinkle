from __future__ import annotations
from .advanced import euler_ode, monte_carlo_normal, parameter_sweep, provenance
from .advanced_schemas import AdvancedSimulationRequest, AdvancedSimulationResult

class AdvancedSimulationEngine:
    def run(self, req: AdvancedSimulationRequest) -> AdvancedSimulationResult:
        payload=req.model_dump()
        if req.kind=='ode':
            result=euler_ode(req.initial, lambda _t,_x:req.derivative, req.dt, req.steps)
            limitation=['Uses explicit Euler integration; domain-specific solvers require validation against the target domain.']
        elif req.kind=='monte_carlo_normal':
            result=monte_carlo_normal(req.mean,req.std,req.samples,req.seed)
            limitation=['Monte Carlo output is stochastic but reproducible for the recorded seed.']
        else:
            if req.objective!='sum_squares': raise ValueError('unsupported objective')
            result=parameter_sweep(req.sweep, lambda p: sum(v*v for v in p.values()))
            limitation=['Parameter sweep is a generic exploration primitive, not a domain model.']
        return AdvancedSimulationResult(status='SIMULATION_COMPLETE',kind=req.kind,result=result,provenance=provenance(payload,req.seed),limitations=limitation)
