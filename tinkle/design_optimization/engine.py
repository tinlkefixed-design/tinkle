from __future__ import annotations
import math, random
from .schemas import *
from tinkle.exoskeleton_engine import ExoskeletonEngine

class DesignOptimizationEngine:
    """Bounded design-space optimization. It only evaluates digital designs."""
    def __init__(self): self.exo = ExoskeletonEngine()

    def _evaluate(self, req: OptimizationRequest, vals: dict[str,float]) -> OptimizationCandidate:
        d = req.design.model_copy(deep=True)
        # Variable names are global design multipliers; unknown names are ignored safely.
        speed_scale = vals.get('speed_scale', 1.0)
        lever_scale = vals.get('lever_scale', 1.0)
        eff_gain = vals.get('efficiency', 0.0)
        raw = []
        for j in d.joints:
            raw.append({'name':j['name'],'degree_of_freedom':j.get('degree_of_freedom',1),'lever_arm_m':float(j['lever_arm_m'])*lever_scale,'angular_speed_rad_s':float(j['angular_speed_rad_s'])*speed_scale,'efficiency':min(0.99,max(0.01,float(j.get('efficiency',0.85))+eff_gain)),'safety_factor':float(j.get('safety_factor',1.5))})
        d.joints = raw
        design = self.exo.design(d)
        peak=design.power['peak_actuator_power_w']; battery=design.power['nominal_battery_energy_wh']
        avg_eff=sum(x.efficiency for x in design.joints)/len(design.joints)
        total_torque=sum(x.required_torque_nm for x in design.joints)
        metrics={'peak_power_w':peak,'battery_energy_wh':battery,'average_efficiency':avg_eff,'total_torque_nm':total_torque}
        violations=[]
        if req.max_peak_power_w is not None and peak>req.max_peak_power_w: violations.append('max_peak_power_w')
        if req.max_battery_energy_wh is not None and battery>req.max_battery_energy_wh: violations.append('max_battery_energy_wh')
        if req.min_efficiency is not None and avg_eff<req.min_efficiency: violations.append('min_efficiency')
        score=0.0
        for obj in req.objectives:
            if obj=='minimize_peak_power': score -= peak
            elif obj=='minimize_battery': score -= battery
            elif obj=='maximize_efficiency': score += avg_eff*1000
            elif obj=='minimize_torque': score -= total_torque
            else: raise ValueError(f'Unsupported objective: {obj}')
        if violations: score -= 1e9*len(violations)
        return OptimizationCandidate(variables=vals,metrics=metrics,feasible=not violations,constraint_violations=violations,score=score)

    def run(self, req: OptimizationRequest) -> OptimizationResult:
        rng=random.Random(req.seed)
        for v in req.variables:
            if v.maximum < v.minimum: raise ValueError(f'Invalid range for {v.name}')
        candidates=[]
        for i in range(req.evaluations):
            vals={v.name: (v.minimum if i==0 else rng.uniform(v.minimum,v.maximum)) for v in req.variables}
            candidates.append(self._evaluate(req,vals))
        feasible=[c for c in candidates if c.feasible]
        pool=feasible or candidates
        best=max(pool,key=lambda c:c.score)
        front=[]
        for c in pool:
            dominated=False
            for other in pool:
                if other is c: continue
                no_worse=True; better=False
                for o in req.objectives:
                    key={'minimize_peak_power':'peak_power_w','minimize_battery':'battery_energy_wh','maximize_efficiency':'average_efficiency','minimize_torque':'total_torque_nm'}[o]
                    a,b=c.metrics[key],other.metrics[key]
                    if o.startswith('minimize'):
                        if b>a: no_worse=False
                        if b<a: better=True
                    else:
                        if b<a: no_worse=False
                        if b>a: better=True
                if no_worse and better: dominated=True; break
            if not dominated: front.append(c)
        return OptimizationResult(status='OPTIMIZATION_COMPLETE',best=best,pareto_front=front[:50],evaluations=len(candidates),seed=req.seed,limitations=['Optimization is digital and bounded; it does not prove physical feasibility.','Objective definitions and constraints require domain validation before engineering release.','No real actuator, battery, human subject, or hardware is controlled.'],provenance={'engine':'DESIGN_OPTIMIZATION_1.0','deterministic_seed':req.seed,'physical_validation':False})
