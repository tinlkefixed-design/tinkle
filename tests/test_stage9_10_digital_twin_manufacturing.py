from tinkle.digital_twin_engine import DigitalTwinEngine, DigitalTwinRequest, TwinSignal
from tinkle.manufacturing_engine import ManufacturingEngine, ManufacturingRequest

def test_digital_twin_produces_snapshots_and_comparison():
    r=DigitalTwinEngine().run(DigitalTwinRequest(name='exo',parameters={'mass_kg':80},duration_s=1,sample_rate_hz=5,signals=[TwinSignal(name='joint_torque',value=10,expected=10,tolerance=.1)]))
    assert len(r.snapshots)==6
    assert r.comparisons and r.comparisons[0].within_tolerance
    assert r.provenance['real_hardware_control'] is False

def test_manufacturing_plan_has_routing_and_inspection():
    r=ManufacturingEngine().plan(ManufacturingRequest(product='exo-frame',material='7075-T6',target_quantity=2,preferred_method='CNC',machine_rate_per_hour=30,material_cost=20))
    assert len(r.operations)==4
    assert r.estimated_total_min > 0
    assert r.inspection_gates
    assert r.provenance['real_world_execution'] is False
