from tinkle.adversarial_science import AttackRequest, AttackMode, AdversarialScienceEngine, FailureSeverity
from tinkle.autonomous_discovery import AutonomousDiscoveryEngine, MissionRequest, ResourceBudget

def test_stage9_hidden_assumption_is_not_silently_passed():
    r=AdversarialScienceEngine().attack(AttackRequest(claim='x', attack_modes=[AttackMode.HIDDEN_ASSUMPTIONS]))
    assert r.overall=='FALSIFICATION_FOUND'
    assert r.findings[0].severity==FailureSeverity.MAJOR
    assert r.repair_candidates

def test_stage9_contradictory_data_detected():
    r=AdversarialScienceEngine().attack(AttackRequest(claim='x', expected={'y':1}, observed={'y':2}, attack_modes=[AttackMode.CONTRADICTORY_DATA]))
    assert not r.findings[0].passed

def test_stage10_checkpoint_and_budget():
    r=AutonomousDiscoveryEngine().run(MissionRequest(mission='test', hypotheses=[{'coverage':1,'cost':1}], budget=ResourceBudget(search_budget=2,compute_budget=10), max_iterations=2))
    assert r.checkpoints
    assert r.selected_actions
    assert r.provenance['orchestration']=='STAGE_10'

def test_stage10_discovery_tree_has_parent_links():
    r=AutonomousDiscoveryEngine().run(MissionRequest(mission='test', hypotheses=[{'coverage':1,'cost':1}], max_iterations=1))
    assert r.nodes[0].id=='root'
    assert all(n.parent_id=='root' for n in r.nodes[1:])
