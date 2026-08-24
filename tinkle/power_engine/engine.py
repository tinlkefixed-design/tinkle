from __future__ import annotations
import math
from .schemas import PowerSystemRequest, PowerSystemDesign

class PowerSystemEngine:
    """Conceptual power-budget and battery sizing engine."""
    def design(self, req: PowerSystemRequest) -> PowerSystemDesign:
        loads={k:float(v) for k,v in req.loads_w.items()}
        if any(v < 0 or not math.isfinite(v) for v in loads.values()): raise ValueError('loads_w must contain finite non-negative values')
        total=sum(loads.values())
        if total <= 0: raise ValueError('total load must be positive')
        input_power=total/req.system_efficiency
        peak_power=input_power*req.peak_multiplier
        required_wh=input_power*req.runtime_h
        nominal_wh=required_wh/req.usable_battery_fraction
        current_a=input_power/req.nominal_voltage_v
        peak_current_a=peak_power/req.nominal_voltage_v
        battery_mass=(nominal_wh/req.specific_energy_wh_kg) if req.specific_energy_wh_kg else 0.0
        checks={'finite':all(math.isfinite(v) for v in (total,input_power,peak_power,required_wh,nominal_wh,current_a,peak_current_a)),'positive_voltage':req.nominal_voltage_v>0}
        warnings=[]
        if req.specific_energy_wh_kg is None: warnings.append('Battery mass cannot be estimated without a supplied specific-energy value.')
        warnings.append('Peak current is a sizing estimate; transient response, BMS limits, wiring and thermal derating require separate validation.')
        return PowerSystemDesign(name=req.name,status='PRELIMINARY_POWER_SYSTEM_DESIGN',load_breakdown=loads,
            energy={'continuous_power_w':input_power,'required_energy_wh':required_wh,'nominal_battery_energy_wh':nominal_wh},
            electrical={'nominal_current_a':current_a,'peak_power_w':peak_power,'peak_current_a':peak_current_a,'nominal_voltage_v':req.nominal_voltage_v},
            battery={'usable_fraction':req.usable_battery_fraction,'estimated_mass_kg':battery_mass},checks=checks,warnings=warnings,
            limitations=['Lumped energy model; excludes cell chemistry, temperature dependence, aging, converter dynamics and manufacturer limits.',
                         'Not a battery-pack construction specification or human-use safety approval.'])
