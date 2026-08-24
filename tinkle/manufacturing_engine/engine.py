from __future__ import annotations
from .schemas import *

class ManufacturingEngine:
    def plan(self, req: ManufacturingRequest) -> ManufacturingPlan:
        method=(req.preferred_method or 'CNC/ADD/ASSEMBLY').strip()
        ops=[ManufacturingOperation(sequence=1,operation='Incoming material inspection',method='INSPECTION',inspection='Verify material identity and quantity'),
             ManufacturingOperation(sequence=2,operation='Primary fabrication',method=method,setup_min=30,cycle_min=10,inspection='Dimensional inspection'),
             ManufacturingOperation(sequence=3,operation='Assembly and interface verification',method='ASSEMBLY',cycle_min=15,inspection='Fit/function check'),
             ManufacturingOperation(sequence=4,operation='Final inspection',method='INSPECTION',cycle_min=5,inspection='Acceptance criteria review')]
        setup=sum(o.setup_min for o in ops); cycle=sum(o.cycle_min for o in ops)*req.target_quantity
        total=setup+cycle
        machine_cost=(total/60.0)*req.machine_rate_per_hour
        cost=machine_cost + req.material_cost*req.target_quantity
        warnings=[]
        if not req.material: warnings.append('Material is unspecified; manufacturing compatibility cannot be fully verified.')
        if not req.bom: warnings.append('BOM is empty; plan is a generic process skeleton.')
        return ManufacturingPlan(product=req.product,quantity=req.target_quantity,operations=ops,required_material=req.material,estimated_setup_min=setup,estimated_cycle_min=cycle,estimated_total_min=total,estimated_cost=cost,inspection_gates=[o.inspection for o in ops if o.inspection],warnings=warnings,provenance={'engine':'STAGE_10_MANUFACTURING','cost_model':'user_supplied_rates_only','real_world_execution':False})
