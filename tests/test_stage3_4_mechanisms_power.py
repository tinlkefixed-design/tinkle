from tinkle.mechanism_engine import MechanismEngine, MechanismRequest
from tinkle.power_engine import PowerSystemEngine, PowerSystemRequest

def test_stage3_mechanism_sizing():
    r=MechanismEngine().design(MechanismRequest(
        name='concept actuator', mechanism='planetary_gear', required_output_torque_nm=120,
        output_speed_rad_s=3, ratio=20, efficiency=.9, safety_factor=1.5,
        motor_max_speed_rad_s=100, motor_max_torque_nm=15))
    assert r.status == 'PRELIMINARY_MECHANISM_DESIGN'
    assert r.input_requirements['torque_nm'] > 0
    assert r.input_requirements['speed_rad_s'] == 60
    assert r.checks['speed_within_motor_limit']

def test_stage4_power_budget():
    r=PowerSystemEngine().design(PowerSystemRequest(
        name='concept power system', loads_w={'actuators':500,'compute':40,'sensors':20},
        runtime_h=2, system_efficiency=.8, usable_battery_fraction=.8,
        nominal_voltage_v=48, specific_energy_wh_kg=200))
    assert r.status == 'PRELIMINARY_POWER_SYSTEM_DESIGN'
    assert r.energy['required_energy_wh'] > 0
    assert r.electrical['peak_current_a'] > r.electrical['nominal_current_a']
    assert r.battery['estimated_mass_kg'] > 0
