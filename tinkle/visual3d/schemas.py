from __future__ import annotations
from typing import Any, Literal
from pydantic import BaseModel, Field

class SceneRequest(BaseModel):
    kind: Literal['library','cad','generate'] = 'generate'
    name: str = Field(default='concept', min_length=1, max_length=128)
    prompt: str = Field(default='', max_length=10000)
    parameters: dict[str, float] = Field(default_factory=dict)

class CADRequest(BaseModel):
    primitive: Literal['box','cylinder','sphere','gear','shaft','beam','bracket','pipe']
    parameters: dict[str, float] = Field(default_factory=dict)

class Simulation3DRequest(BaseModel):
    kind: Literal['gravity','projectile','spring','orbit','heat','fluid']
    parameters: dict[str, float] = Field(default_factory=dict)
    steps: int = Field(default=60, ge=1, le=1000)
    dt: float = Field(default=0.02, gt=0, le=1.0)

class SceneResult(BaseModel):
    status: str
    scene: dict[str, Any]
    provenance: dict[str, Any]
    limitations: list[str] = Field(default_factory=list)

class Simulation3DResult(BaseModel):
    status: str
    kind: str
    frames: list[dict[str, Any]]
    visualization: dict[str, Any]
    provenance: dict[str, Any]
    limitations: list[str] = Field(default_factory=list)
