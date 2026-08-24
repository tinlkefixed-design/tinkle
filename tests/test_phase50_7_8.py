from tinkle.engineering_engine import EngineeringEngine, EngineeringDomain, EngineeringSolveRequest
from tinkle.observer import TinkleObserver, ObserverEventRequest

def test_engineering_provider_solves_ohms_law():
    r=EngineeringEngine().solve(EngineeringSolveRequest(domain=EngineeringDomain.electrical_engineering, problem="Ohm", model="ohms_law_v1", inputs={"voltage_v":12,"resistance_ohm":6}))
    assert r.status=="CALCULATED"
    assert r.calculation["outputs"]["current_a"]==2

def test_engineering_provider_rejects_unknown_model():
    try:
        EngineeringEngine().solve(EngineeringSolveRequest(domain=EngineeringDomain.robotics, problem="x", model="nope", inputs={}))
        assert False
    except ValueError as e:
        assert "Unsupported engineering model" in str(e)

def test_observer_prometheus_snapshot():
    o=TinkleObserver(); o.observe(ObserverEventRequest(metric="Latency", value=12.5, source="test"))
    text=o.prometheus()
    assert "tinkle_observer_events_total 1" in text
    assert 'metric="latency"' in text
