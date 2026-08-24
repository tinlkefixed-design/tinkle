from tinkle.simulation_engine.advanced_engine import AdvancedSimulationEngine
from tinkle.simulation_engine.advanced_schemas import AdvancedSimulationRequest
from tinkle.evolution_engine import EvolutionEngine, EvolutionRequest

def test_ode_reproducible_and_provenance():
    r=AdvancedSimulationEngine().run(AdvancedSimulationRequest(kind='ode',initial=0,derivative=2,dt=.5,steps=4,seed=7))
    assert r.status=='SIMULATION_COMPLETE' and r.result[-1]['state']==4
    assert r.provenance['random_seed']==7 and r.provenance['input_hash']

def test_monte_carlo_seed_reproducible():
    e=AdvancedSimulationEngine(); q=AdvancedSimulationRequest(kind='monte_carlo_normal',mean=2,std=1,samples=100,seed=9)
    assert e.run(q).result==e.run(q).result

def test_parameter_sweep():
    r=AdvancedSimulationEngine().run(AdvancedSimulationRequest(kind='parameter_sweep',sweep={'x':[1,2],'y':[3,4]}))
    assert len(r.result)==4

def test_evolution_pareto():
    req=EvolutionRequest(seeds=[[0,0],[1,1],[-1,-1]],generations=4,population_size=8,seed=3,maximize=[True,True])
    r=EvolutionEngine().run(req)
    assert r.status=='EVOLUTION_COMPLETE' and r.pareto_front and r.evaluations>0

def test_evolution_rejects_mixed_genome_lengths():
    try: EvolutionEngine().run(EvolutionRequest(seeds=[[1],[1,2]],maximize=[True,True]))
    except ValueError: return
    assert False
