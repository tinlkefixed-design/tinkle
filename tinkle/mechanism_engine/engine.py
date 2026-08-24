from __future__ import annotations
import math
from .schemas import MechanismRequest, MechanismDesign

class MechanismEngine:
    """Deterministic actuator/transmission sizing for conceptual engineering."""
    def design(self, req: MechanismRequest) -> MechanismDesign:
        effective_eff = req.efficiency
        load_torque = req.required_output_torque_nm * req.safety_factor * req.service_factor
        input_torque = load_torque / (req.ratio * effective_eff)
        input_speed = req.output_speed_rad_s * req.ratio
        output_power = req.required_output_torque_nm * req.output_speed_rad_s
        input_power = output_power / effective_eff
        checks = {
            'positive_finite_result': all(math.isfinite(x) for x in (load_torque,input_torque,input_speed,output_power,input_power)),
            'speed_within_motor_limit': req.motor_max_speed_rad_s is None or input_speed <= req.motor_max_speed_rad_s,
            'torque_within_motor_limit': req.motor_max_torque_nm is None or input_torque <= req.motor_max_torque_nm,
        }
        warnings=[]
        if not checks['speed_within_motor_limit']: warnings.append('Conceptual input speed exceeds the supplied motor limit.')
        if not checks['torque_within_motor_limit']: warnings.append('Conceptual input torque exceeds the supplied motor limit.')
        return MechanismDesign(
            name=req.name, status='PRELIMINARY_MECHANISM_DESIGN',
            architecture={'mechanism':req.mechanism,'ratio':req.ratio,'efficiency':req.efficiency},
            input_requirements={'torque_nm':input_torque,'speed_rad_s':input_speed,'power_w':input_power},
            output_requirements={'torque_nm':load_torque,'speed_rad_s':req.output_speed_rad_s,'power_w':output_power},
            sizing={'torque_margin_nm':(req.motor_max_torque_nm-input_torque) if req.motor_max_torque_nm is not None else 0.0,
                    'speed_margin_rad_s':(req.motor_max_speed_rad_s-input_speed) if req.motor_max_speed_rad_s is not None else 0.0},
            checks=checks,warnings=warnings,
            limitations=['Conceptual lumped model; excludes bearing losses, backlash, compliance, fatigue, thermal derating and manufacturer-specific limits.',
                         'Not a fabrication or human-use safety approval.'],
        )
