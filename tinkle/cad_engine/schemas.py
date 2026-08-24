from __future__ import annotations
from typing import Any, Literal
from pydantic import BaseModel, Field
class CADPart(BaseModel):
    primitive: Literal['box','cylinder','sphere']
    parameters: dict[str,float]=Field(default_factory=dict)
    position: list[float]=Field(default_factory=lambda:[0,0,0],min_length=3,max_length=3)
    rotation_deg: list[float]=Field(default_factory=lambda:[0,0,0],min_length=3,max_length=3)
    name: str='part'
class CADAssemblyRequest(BaseModel):
    name: str=Field('assembly',min_length=1,max_length=128)
    parts: list[CADPart]=Field(default_factory=list,max_length=100)
    export: Literal['json','obj','stl']='json'
class CADResult(BaseModel):
    status:str
    assembly:dict[str,Any]
    export_format:str
    export_data:str|None=None
    provenance:dict[str,Any]
    limitations:list[str]=Field(default_factory=list)
