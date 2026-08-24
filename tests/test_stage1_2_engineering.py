from tinkle.engineering_brain import EngineeringBrain, EngineeringBrainRequest, DesignIntent
from tinkle.exoskeleton_engine import ExoskeletonEngine, ExoskeletonRequest


def test_engineering_brain_decomposes_exoskeleton_design():
    r = EngineeringBrain().analyze(EngineeringBrainRequest(
        problem="Design a wearable exoskeleton with motor torque assistance, battery power, IMU feedback and safe operation.",
        intent=DesignIntent.DESIGN,
    ))
    assert r.status == "ANALYSIS_COMPLETE"
    assert "Robotics" in r.domains
    assert "Mechanical Engineering" in r.domains
    assert any(x.name == "safety_limits" for x in r.requirements)
    assert r.verification_plan
    assert r.provenance["validated_design"] is False


def test_exoskeleton_engine_sizes_joints_and_energy():
    r = ExoskeletonEngine().design(ExoskeletonRequest(
        name="Atlas-X conceptual exoskeleton",
        user_mass_kg=75,
        assisted_load_kg=10,
        assistance_fraction=0.4,
        joints=[
            {"name":"knee_left", "degree_of_freedom":1, "lever_arm_m":0.04, "angular_speed_rad_s":4.0, "efficiency":0.85, "safety_factor":1.5},
            {"name":"knee_right", "degree_of_freedom":1, "lever_arm_m":0.04, "angular_speed_rad_s":4.0, "efficiency":0.85, "safety_factor":1.5},
        ],
        continuous_runtime_h=2,
    ))
    assert r.status == "PRELIMINARY_ENGINEERING_DESIGN"
    assert len(r.joints) == 2
    assert all(j.required_torque_nm > 0 for j in r.joints)
    assert r.power["nominal_battery_energy_wh"] > r.power["required_battery_energy_wh"]
    assert "Perform structural FEA" in r.verification_gates
