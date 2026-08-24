from tinkle.ergonomics_engine import ErgonomicsEngine, ErgonomicsRequest, RangeOfMotion
from tinkle.control_engine import ControlEngine, ControlRequest, SensorSpec, ControlLoopSpec

def test_ergonomics_rom_and_mass():
    r=ErgonomicsEngine().analyze(ErgonomicsRequest(user_mass_kg=70,stature_m=1.75,segment_lengths_m={'torso':0.55,'thigh':0.45,'shank':0.4},suit_mass_kg=12,rom=[RangeOfMotion(name='knee',min_deg=0,max_deg=140,user_min_deg=5,user_max_deg=130)]))
    assert r.status.startswith('PRELIMINARY') and r.rom_checks[0]['compatible'] is True
    assert r.balance['total_system_mass_kg']==82

def test_control_architecture():
    r=ControlEngine().analyze(ControlRequest(sensors=[SensorSpec(name='imu',kind='imu',sample_hz=200,noise_std=0.02,max_latency_ms=2)],loops=[ControlLoopSpec(name='joint',rate_hz=100,kp=1,ki=.1,kd=.01,command_limit=10)],actuator_count=4))
    assert r.architecture['hardware_io_enabled'] is False
    assert r.loop_summary[0]['rate_hz']==100
