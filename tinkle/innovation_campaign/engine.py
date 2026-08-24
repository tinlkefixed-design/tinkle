from __future__ import annotations
from .schemas import *
from tinkle.design_optimization import DesignOptimizationEngine, OptimizationRequest
from tinkle.experiment_engine import ExperimentEngine, ExperimentRequest
from tinkle.prototype_engine import PrototypeEngine, PrototypeRequest, PrototypeLevel

class InnovationCampaignEngine:
    """Stage 12 orchestration: optimize digitally, then prepare evidence and prototype gates."""
    def __init__(self): self.opt=DesignOptimizationEngine(); self.exp=ExperimentEngine(); self.proto=PrototypeEngine()
    def run(self, req: InnovationCampaignRequest) -> InnovationCampaignResult:
        opt=self.opt.run(OptimizationRequest(design=req.design,variables=req.variables,objectives=req.objectives,max_peak_power_w=req.max_peak_power_w,max_battery_energy_wh=req.max_battery_energy_wh,min_efficiency=req.min_efficiency,evaluations=req.evaluations,seed=req.seed))
        best=opt.best
        er=ExperimentRequest(objective=f'Validate digital candidate for: {req.mission}',hypotheses=['Optimized candidate meets the declared digital objectives'],measurements=['peak_power_w','battery_energy_wh','efficiency'],risk_level=req.experiment_risk)
        ep=self.exp.plan(er)
        pr=PrototypeRequest(title='Digital candidate prototype',objective=req.mission,materials=['Engineering-grade materials selected after verification'],risk_level=req.prototype_risk)
        pp=self.proto.plan(pr,PrototypeLevel.DIGITAL)
        gates=['Review optimization objectives and constraints','Independent engineering review','Complete structural/thermal/controls verification','Obtain human approval before any high-risk physical experiment','Do not treat simulation as validation','Update the digital twin with measured evidence only']
        return InnovationCampaignResult(status='CAMPAIGN_PLAN_COMPLETE',mission=req.mission,optimization=opt.model_dump(),recommended_experiment=ep.model_dump(),prototype_plan=pp.model_dump(),decision_gates=gates,next_actions=['Review Pareto candidates','Select a candidate for controlled evidence collection','Record real measurements with provenance','Re-run optimization with validated measurements'],limitations=opt.limitations+['Campaign orchestration does not execute experiments or manufacture hardware.','A digital optimum is not a certified safe design.'])
