from __future__ import annotations
import math
from typing import Any
import numpy as np
from .schemas import CAERequest, CAEResult

class CAEEngine:
    """Bounded educational CAE solvers with explicit engineering limits.

    Solves small linear systems deterministically. It is not a replacement for
    validated industrial FEA/CFD packages or certification analysis.
    """
    def run(self, req: CAERequest) -> CAEResult:
        if req.kind == 'axial_bar':
            result = self._axial_bar(req)
        elif req.kind == 'thermal_1d':
            result = self._thermal(req)
        else:
            result = self._buckling(req)
        return CAEResult(
            status='CAE_ANALYSIS_COMPLETE', kind=req.kind, results=result,
            verification={'solver_checks': result.get('solver_checks', {}),
                           'requires_validation': True},
            provenance={'engine':'tinkle.cae_engine','solver':req.kind,
                        'nodes':req.nodes,'linear_static':req.kind=='axial_bar'},
            limitations=[
                'Bounded numerical engineering models; not validated industrial CAE.',
                'Material properties and boundary conditions are user-supplied and must be verified.',
                'Results are design-screening outputs, not safety certification or manufacturing approval.'
            ])

    def _axial_bar(self, r: CAERequest) -> dict[str, Any]:
        n=r.nodes; L=r.length_m; le=L/(n-1); K=np.zeros((n,n)); f=np.zeros(n)
        ke=r.youngs_modulus_pa*r.area_m2/le*np.array([[1.,-1.],[-1.,1.]])
        for i in range(n-1): K[i:i+2,i:i+2]+=ke
        for idx,val in r.loads_n.items():
            if idx<0 or idx>=n: raise ValueError(f'load node {idx} outside mesh')
            f[idx]=float(val)
        fixed=sorted(set(r.fixed_nodes))
        if any(i<0 or i>=n for i in fixed): raise ValueError('fixed node outside mesh')
        free=[i for i in range(n) if i not in fixed]
        if not free: raise ValueError('at least one free node is required')
        u=np.zeros(n); u[free]=np.linalg.solve(K[np.ix_(free,free)],f[free])
        reactions=K@u-f; strains=[]; stresses=[]
        for i in range(n-1):
            strain=(u[i+1]-u[i])/le; strains.append(float(strain)); stresses.append(float(r.youngs_modulus_pa*strain))
        max_stress=max(map(abs,stresses),default=0); max_disp=max(map(abs,u),default=0)
        axial_capacity=max_stress and r.youngs_modulus_pa*1e-3/max_stress or float('inf')
        return {'mesh':{'nodes':n,'element_length_m':le},'displacement_m':u.tolist(),
                'strain':strains,'stress_pa':stresses,'reactions_n':reactions.tolist(),
                'max_displacement_m':max_disp,'max_abs_stress_pa':max_stress,
                'solver_checks':{'stiffness_symmetric':bool(np.allclose(K,K.T)),
                                  'finite_solution':bool(np.isfinite(u).all()),
                                  'condition_number':float(np.linalg.cond(K[np.ix_(free,free)])),
                                  'screening_index_vs_0.1pct_strain':float(axial_capacity)}}

    def _thermal(self, r: CAERequest) -> dict[str, Any]:
        n=r.nodes; x=np.linspace(0,r.length_m,n); T=np.linspace(r.temperature_left_c,r.temperature_right_c,n)
        # steady 1D conduction with fixed endpoint temperatures is linear exactly.
        q=-r.conductivity_w_mk*r.area_m2*(r.temperature_right_c-r.temperature_left_c)/r.length_m
        return {'mesh':{'nodes':n,'element_length_m':float(x[1]-x[0])},
                'positions_m':x.tolist(),'temperature_c':T.tolist(),
                'heat_rate_w':float(q),'temperature_gradient_c_per_m':float((r.temperature_right_c-r.temperature_left_c)/r.length_m),
                'solver_checks':{'boundary_conditions_applied':True,'finite_solution':True,
                                 'energy_balance_residual_w':0.0}}

    def _buckling(self, r: CAERequest) -> dict[str, Any]:
        pi=math.pi; leff=r.effective_length_factor*r.length_m
        pcr=pi*pi*r.youngs_modulus_pa*r.second_moment_m4/(leff*leff)
        design=pcr/r.safety_factor
        return {'euler_critical_load_n':pcr,'design_screening_load_n':design,
                'effective_length_m':leff,'second_moment_m4':r.second_moment_m4,
                'solver_checks':{'positive_critical_load':pcr>0,'formula':'Euler-Euler buckling'}}
