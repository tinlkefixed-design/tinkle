from __future__ import annotations
import math
from time import time
from .schemas import *

class DigitalTwinEngine:
    def run(self, req: DigitalTwinRequest) -> DigitalTwinResult:
        samples = max(1, min(1000, int(round(req.duration_s * req.sample_rate_hz)) + 1))
        dt = req.duration_s / max(1, samples - 1)
        snapshots: list[TwinSnapshot] = []
        comparisons: list[TwinComparison] = []
        for i in range(samples):
            t = i * dt
            state = {k: float(v) for k, v in req.parameters.items()}
            signals=[]
            for s in req.signals:
                # Deterministic virtual telemetry: baseline + bounded dynamic component.
                value = s.value + 0.01 * math.sin(2 * math.pi * t / max(req.duration_s, dt))
                signals.append(s.model_copy(update={'value': value}))
            health=1.0
            for s in signals:
                if s.expected is not None:
                    err=abs(s.value-s.expected); tol=max(s.tolerance, abs(s.expected)*s.tolerance)
                    health=min(health, 1.0 if err<=tol else max(0.0, 1.0-err/max(tol,1e-12)))
            snapshots.append(TwinSnapshot(timestamp=time()+t,state=state,signals=signals,health_score=health))
        # Compare final virtual snapshot to supplied expected values.
        final=snapshots[-1]
        for s in final.signals:
            if s.expected is None: continue
            ae=abs(s.value-s.expected); re=ae/max(abs(s.expected),1e-12); tol=max(s.tolerance,abs(s.expected)*s.tolerance)
            comparisons.append(TwinComparison(signal=s.name,expected=s.expected,observed=s.value,absolute_error=ae,relative_error=re,within_tolerance=ae<=tol))
        score=min((s.health_score for s in snapshots), default=1.0)
        warnings=[f'Signal {c.signal} exceeds tolerance' for c in comparisons if not c.within_tolerance]
        return DigitalTwinResult(name=req.name,model_id=req.model_id,snapshots=snapshots,comparisons=comparisons,health_score=score,warnings=warnings,provenance={'engine':'STAGE_9_DIGITAL_TWIN','mode':'virtual','real_hardware_control':False,'evidence':'computed_from_supplied_parameters'})
