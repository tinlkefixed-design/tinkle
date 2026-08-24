from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field
from tinkle.exoskeleton_engine.schemas import ExoskeletonRequest
from tinkle.design_optimization.schemas import OptimizationVariable

class InnovationCampaignRequest(BaseModel):
    mission: str = Field(min_length=1, max_length=10000)
    design: ExoskeletonRequest
    variables: list[OptimizationVariable] = Field(min_length=1, max_length=8)
    objectives: list[str] = Field(min_length=1, max_length=8)
    max_peak_power_w: float | None = Field(default=None, gt=0)
    max_battery_energy_wh: float | None = Field(default=None, gt=0)
    min_efficiency: float | None = Field(default=None, gt=0, le=1)
    experiment_risk: str = 'LOW'
    prototype_risk: str = 'LOW'
    evaluations: int = Field(default=120, ge=8, le=5000)
    seed: int = 0

class InnovationCampaignResult(BaseModel):
    status: str
    mission: str
    optimization: dict[str, Any]
    recommended_experiment: dict[str, Any]
    prototype_plan: dict[str, Any]
    decision_gates: list[str]
    next_actions: list[str]
    limitations: list[str]
