import pytest
from tinkle.simulation_engine import SimulationEngine, SimulationRequest, SimulationStage

def test_simulation_follows_blueprint_stages():
    result = SimulationEngine().simulate(SimulationRequest(model={'state':'x','initial':1,'rate':2}, steps=3, dt=0.5))
    assert result.status == 'SIMULATION_COMPLETE'
    assert result.stages == list(SimulationStage)
    assert result.results[-1]['x'] == pytest.approx(4.0)
    assert result.visualization['x'] == 'time'

def test_optimization_is_explicit_boundary():
    result = SimulationEngine().simulate(SimulationRequest(model={'state':'x','rate':1}, steps=1, optimize=True))
    assert result.optimization['status'] == 'BOUNDARY_READY'
    assert result.limitations

def test_invalid_model_is_rejected():
    with pytest.raises(ValueError):
        SimulationEngine().simulate(SimulationRequest(model={'state':'x','rate':'unknown'}))
