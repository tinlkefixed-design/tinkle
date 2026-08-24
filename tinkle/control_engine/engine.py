from __future__ import annotations
from .schemas import ControlRequest, ControlArchitecture

class ControlEngine:
    """Architecture checker for sensing and closed-loop control; no hardware I/O."""
    def analyze(self, req: ControlRequest) -> ControlArchitecture:
        sensor_summary=[]; warnings=[]
        for s in req.sensors:
            if s.noise_std < 0: raise ValueError(f'invalid noise for {s.name}')
            sensor_summary.append({'name':s.name,'kind':s.kind,'sample_hz':s.sample_hz,'max_latency_ms':s.max_latency_ms})
            if s.max_latency_ms > 1000/s.sample_hz*2: warnings.append(f'Latency budget is high for sensor {s.name}')
        loop_summary=[]
        sensor_rates=[s.sample_hz for s in req.sensors]
        max_sensor_rate=max(sensor_rates)
        for l in req.loops:
            if l.rate_hz > max_sensor_rate*2: warnings.append(f'Loop {l.name} requests a rate far above the fastest declared sensor')
            loop_summary.append({'name':l.name,'rate_hz':l.rate_hz,'gains':{'kp':l.kp,'ki':l.ki,'kd':l.kd},'command_limit':l.command_limit})
        return ControlArchitecture(
            status='PRELIMINARY_CONTROL_ARCHITECTURE', sensor_summary=sensor_summary, loop_summary=loop_summary,
            architecture={'topology':'sensor -> state estimation -> controller -> actuator interface','actuator_count':req.actuator_count,'emergency_timeout_ms':req.emergency_timeout_ms,'hardware_io_enabled':False},
            safety_gates=['Independent watchdog','Command saturation and rate limiting','Sensor plausibility checks','Loss-of-sensor safe state','Power-stage emergency isolation','Hardware-in-the-loop validation before physical actuation'],
            warnings=warnings,
            limitations=['No PID stability proof is claimed','No real-time guarantees are claimed','No hardware is controlled by this API','Actual sensor noise, timing jitter and actuator dynamics require measured data']
        )
