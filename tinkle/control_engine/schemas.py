from __future__ import annotations
from pydantic import BaseModel, Field

class SensorSpec(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    kind: str = Field(min_length=1, max_length=50)
    sample_hz: float = Field(gt=0, le=5000)
    noise_std: float = Field(ge=0)
    max_latency_ms: float = Field(ge=0, le=10000)

class ControlLoopSpec(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    rate_hz: float = Field(gt=0, le=5000)
    kp: float = Field(ge=0)
    ki: float = Field(ge=0)
    kd: float = Field(ge=0)
    command_limit: float = Field(gt=0)

class ControlRequest(BaseModel):
    sensors: list[SensorSpec] = Field(min_length=1, max_length=64)
    loops: list[ControlLoopSpec] = Field(min_length=1, max_length=32)
    actuator_count: int = Field(ge=1, le=256)
    emergency_timeout_ms: float = Field(gt=0, le=10000, default=100)

class ControlArchitecture(BaseModel):
    status: str
    sensor_summary: list[dict[str, object]]
    loop_summary: list[dict[str, object]]
    architecture: dict[str, object]
    safety_gates: list[str]
    warnings: list[str]
    limitations: list[str]
