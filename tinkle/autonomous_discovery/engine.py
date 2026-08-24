from __future__ import annotations
from copy import deepcopy
from typing import Any
from tinkle.advanced.engines import InformationGainEngine
from tinkle.adversarial_science import AdversarialScienceEngine, AttackRequest
from .schemas import Checkpoint, DiscoveryNode, DiscoveryRun, MissionRequest, MissionStatus, ResourceBudget

class AutonomousDiscoveryEngine:
    """Long-horizon coordinator over existing Stage 1-8 engines.

    This is an executable orchestration loop, not a claim of unrestricted AGI:
    it operates on supplied hypotheses/designs and records every decision.
    """
    def __init__(self):
        self.info_gain=InformationGainEngine(); self.adversary=AdversarialScienceEngine()

    def run(self, req: MissionRequest) -> DiscoveryRun:
        budget=req.budget.model_copy(deep=True); nodes=[DiscoveryNode(id='root',kind='MISSION',label=req.mission)]
        checkpoints=[]; actions=[]; failures=[]; candidates=deepcopy(req.candidate_designs); hypotheses=deepcopy(req.hypotheses)
        status=MissionStatus.RUNNING; iteration=0
        for iteration in range(1, req.max_iterations+1):
            available=[]
            for i,h in enumerate(hypotheses):
                available.append({'id':f'h{i+1}','kind':'HYPOTHESIS_TEST','coverage':float(h.get('coverage',0.5)),'cost':float(h.get('cost',1)),'risk':float(h.get('risk',0))})
            for i,c in enumerate(candidates):
                available.append({'id':f'c{i+1}','kind':'CANDIDATE_ATTACK','coverage':float(c.get('coverage',0.5)),'cost':float(c.get('cost',1)),'risk':float(c.get('risk',0))})
            ranked=self.info_gain.rank_actions(hypotheses,available) if available else []
            if not ranked: break
            action=ranked[0]; actions.append(action); nodes.append(DiscoveryNode(id=f'node-{iteration}',parent_id='root',kind=action['kind'],label=action['id'],metadata={'information_gain_score':action['information_gain_score']}))
            budget.search_budget=max(0,budget.search_budget-1); budget.compute_budget=max(0,budget.compute_budget-action['cost'])
            if action['kind']=='CANDIDATE_ATTACK' and candidates:
                idx=max(0,int(action['id'][1:])-1); cand=candidates[idx]
                attack=self.adversary.attack(AttackRequest(claim=str(cand.get('claim',cand.get('description','candidate'))), assumptions=list(cand.get('assumptions',[])), expected=cand.get('expected',{}), observed=cand.get('observed',{}), evidence=list(cand.get('evidence',[]))))
                if attack.overall=='FALSIFICATION_FOUND':
                    failures.append({'iteration':iteration,'candidate':cand,'attack':attack.model_dump(mode='json')})
                    if req.stop_on_fatal and any(f['severity']=='FATAL' for f in attack.findings): status=MissionStatus.STOPPED; break
            cp=Checkpoint(iteration=iteration,status=MissionStatus.RUNNING,state={'actions':len(actions),'failures':len(failures),'candidate_count':len(candidates)},remaining_budget=budget.model_copy(deep=True))
            checkpoints.append(cp)
            if budget.search_budget<=0 or budget.compute_budget<=0: status=MissionStatus.STOPPED; break
        else: status=MissionStatus.COMPLETED
        if status==MissionStatus.RUNNING: status=MissionStatus.COMPLETED
        return DiscoveryRun(mission=req.mission,status=status,iteration=iteration,nodes=nodes,checkpoints=checkpoints,open_hypotheses=hypotheses,selected_actions=actions,failures=failures,best_candidates=candidates[:5],resource_used={'search':float(req.budget.search_budget-budget.search_budget),'compute':float(req.budget.compute_budget-budget.compute_budget)},provenance={'orchestration':'STAGE_10','long_horizon':True,'evidence_policy':'No evidence is invented; candidate attacks use caller-supplied fields.'})
