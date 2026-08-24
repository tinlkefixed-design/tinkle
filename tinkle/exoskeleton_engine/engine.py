from __future__ import annotations
import math
from .schemas import *

class ExoskeletonEngine:
    """Stage 2: deterministic first-pass exoskeleton architecture sizing.

    This is an engineering pre-sizing model, not a certified safety model or
    a substitute for FEA, human-subject testing, actuator datasheets, or lab validation.
    """
    G = 9.80665

    def design(self, req: ExoskeletonRequest) -> ExoskeletonDesign:
        joints=[]
        total_peak_power=0.0
        for raw in req.joints:
            try:
                name=str(raw["name"]); dof=int(raw.get("degree_of_freedom", 1))
                lever=float(raw["lever_arm_m"]); speed=float(raw["angular_speed_rad_s"])
                eff=float(raw.get("efficiency", 0.85)); sf=float(raw.get("safety_factor", 1.5))
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(f"Invalid joint specification: {raw!r}") from exc
            if lever <= 0 or speed <= 0 or not 0 < eff <= 1 or not 1 <= sf <= 5 or not 1 <= dof <= 3:
                raise ValueError(f"Invalid limits for joint {name}")
            supported_mass = req.user_mass_kg * req.assistance_fraction + req.assisted_load_kg
            force = supported_mass * self.G
            torque = force * lever * sf
            power = torque * speed / eff
            if not all(math.isfinite(x) for x in (force, torque, power)):
                raise ValueError(f"Non-finite result for joint {name}")
            joints.append(JointSpec(name=name, degree_of_freedom=dof, assist_force_n=force, lever_arm_m=lever, angular_speed_rad_s=speed, efficiency=eff, safety_factor=sf, required_torque_nm=torque, required_power_w=power))
            total_peak_power += power
        average_power = total_peak_power * 0.45
        required_wh = average_power * req.continuous_runtime_h / req.system_efficiency
        nominal_wh = required_wh / req.battery_usable_fraction
        warnings=["All actuator values are first-pass sizing estimates; select real components from manufacturer data.", "Human-contact loads, joint alignment and failure modes require dedicated biomechanical and safety validation."]
        if req.mass_budget_kg is None:
            warnings.append("No total mass budget was supplied; battery and actuator mass are not closed in the design.")
        return ExoskeletonDesign(
            name=req.name, status="PRELIMINARY_ENGINEERING_DESIGN",
            architecture={"type":"wearable_exoskeleton", "control":"closed-loop actuator architecture", "power_bus":"DC bus (abstract)", "sensors":["joint position", "IMU", "motor current"], "emergency_behavior":"torque-limited safe state"},
            joints=joints,
            power={"peak_actuator_power_w": total_peak_power, "estimated_average_power_w": average_power, "required_battery_energy_wh": required_wh, "nominal_battery_energy_wh": nominal_wh},
            mass_budget={"target_kg": req.mass_budget_kg, "user_mass_kg": req.user_mass_kg, "assisted_load_kg": req.assisted_load_kg},
            verification_gates=["Trace requirements to each joint", "Verify actuator torque and thermal limits", "Verify battery peak/continuous power", "Perform structural FEA", "Perform human-fit and range-of-motion validation", "Independent safety review before any physical test"],
            warnings=warnings,
            limitations=["No FEA/CFD solver is invoked.", "No manufacturer component database is assumed.", "No physical actuator or battery control is performed.", "Results must not be treated as proof of safe human use."],
            provenance={"engine":"EXOSKELETON_ENGINE_1.0", "deterministic":True, "validated_design":False}
        )
