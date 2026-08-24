from __future__ import annotations
from .schemas import *

_HIGH_RISK = {RiskLevel.HIGH, RiskLevel.CRITICAL}

class ExperimentEngine:
    """Safe experiment planning layer; it never executes real-world equipment."""
    def plan(self, req: ExperimentRequest) -> ExperimentPlan:
        approval = req.risk_level in _HIGH_RISK or bool(req.safety_requirements)
        procedure = [
            'Define controls and baseline',
            'Calibrate measurement path',
            'Set initial conditions',
            'Run controlled trial',
            'Record raw measurements and deviations',
            'Stop on any declared failure or safety condition',
        ]
        status = ExperimentStatus.APPROVAL_REQUIRED if approval else ExperimentStatus.PROPOSED
        return ExperimentPlan(
            objective=req.objective, hypotheses=req.hypotheses, variables=req.variables,
            controls=req.controls, measurements=req.measurements, equipment=req.equipment,
            procedure=procedure, expected_outcomes=req.expected_outcomes,
            failure_conditions=req.failure_conditions, safety_requirements=req.safety_requirements,
            risk_level=req.risk_level, status=status, human_approval_required=approval,
            provenance={'engine':'STAGE_11_EXPERIMENT_ENGINE','execution_policy':'planning_only','evidence_policy':'No measurements are fabricated.'}
        )

    def rank(self, requests: list[ExperimentRequest]) -> list[ExperimentCandidate]:
        out=[]
        for req in requests:
            plan=self.plan(req)
            # Deterministic proxy: more discriminating hypotheses/measurements increase information value.
            ig=min(100.0, 10.0*len(req.hypotheses)+5.0*len(req.measurements)+3.0*len(req.controls))
            value=ig + 2.0*len(req.expected_outcomes)
            denominator=max(1.0, req.estimated_cost + req.estimated_time_seconds/3600.0 + (5.0 if req.risk_level in _HIGH_RISK else 0.0))
            score=value/denominator
            out.append(ExperimentCandidate(plan=plan, information_gain=ig, value_score=value, cost_risk_time=denominator, priority_score=score))
        return sorted(out,key=lambda x:x.priority_score,reverse=True)

    def record_result(self, plan: ExperimentPlan, measurements: dict, deviations: list[str]|None=None) -> ExperimentResult:
        if plan.status not in {ExperimentStatus.APPROVED, ExperimentStatus.EXECUTED}:
            raise ValueError('Experiment must be approved before recording a real experimental result')
        return ExperimentResult(experiment_id=plan.id,status=ExperimentStatus.EXECUTED,measurements=measurements,deviations=deviations or [],provenance={'plan_id':str(plan.id),'evidence_class':'EXPERIMENTAL'})
