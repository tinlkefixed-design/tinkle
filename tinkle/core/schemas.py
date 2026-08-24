from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

def utc_now() -> datetime: return datetime.now(timezone.utc)
class TaskStatus(str, Enum): pending='pending'; running='running'; completed='completed'; failed='failed'
class Permission(str, Enum): read='read'; write='write'; execute='execute'; admin='admin'
class TaskCreate(BaseModel): prompt:str=Field(min_length=1,max_length=10000); project_id:UUID|None=None
class Task(BaseModel):
 id:UUID=Field(default_factory=uuid4); owner:str='default'; prompt:str; status:TaskStatus=TaskStatus.pending; result:str|None=None; error:str|None=None; project_id:UUID|None=None; created_at:datetime=Field(default_factory=utc_now); updated_at:datetime=Field(default_factory=utc_now)
class TaskResponse(BaseModel): task:Task; message:str
class ProjectCreate(BaseModel): name:str=Field(min_length=1,max_length=200)
class Project(BaseModel): id:UUID=Field(default_factory=uuid4); owner:str='default'; name:str; created_at:datetime=Field(default_factory=utc_now)
class Event(BaseModel): id:UUID=Field(default_factory=uuid4); type:str; actor:str='system'; payload:dict[str,Any]=Field(default_factory=dict); created_at:datetime=Field(default_factory=utc_now)
class Job(BaseModel): id:UUID=Field(default_factory=uuid4); type:str; status:str='queued'; created_at:datetime=Field(default_factory=utc_now)
class StructuredResponse(BaseModel): ok:bool; data:Any=None; error:str|None=None; request_id:UUID=Field(default_factory=uuid4)
class ExportResponse(BaseModel): owner:str; projects:list[Project]; tasks:list[Task]; audit_log:list[Event]
class TaskType(str,Enum): simple='simple'; reasoning='reasoning'; research='research'; math='math'; coding='coding'; vision='vision'; general='general'
class Privacy(str,Enum): public='public'; private='private'
class ModelCapabilities(BaseModel): reasoning:float=Field(ge=0,le=1); coding:float=Field(ge=0,le=1); vision:float=Field(ge=0,le=1); tool_use:float=Field(ge=0,le=1); context_size:int=Field(gt=0)
class ModelProfile(BaseModel): id:str; provider:str; capabilities:ModelCapabilities; cost_per_1k_tokens:float=Field(ge=0); latency_ms:int=Field(gt=0); local:bool
class RoutingRequest(BaseModel):
 prompt:str=Field(min_length=1,max_length=10000); task_type:TaskType=TaskType.general; difficulty:float=Field(default=.5,ge=0,le=1); privacy:Privacy=Privacy.public; context_tokens:int=Field(default=1000,gt=0); require_reasoning:bool=False; require_coding:bool=False; require_vision:bool=False; require_tool_use:bool=False; max_cost_per_1k_tokens:float|None=Field(default=None,ge=0); max_latency_ms:int|None=Field(default=None,gt=0)
class RoutingDecision(BaseModel): request_id:UUID=Field(default_factory=uuid4); selected_model:str; provider:str; score:float; reasons:list[str]; fallback_models:list[str]; policy:str
class ProviderRequest(BaseModel): model_id:str; prompt:str
class ProviderResponse(BaseModel): model_id:str; text:str; provider:str; usage:dict[str,Any]={}
class ToolSpec(BaseModel):
 name:str; description:str; input_schema:dict[str,Any]; output_schema:dict[str,Any]; permissions:set[Permission]; timeout_ms:int=Field(gt=0); cpu_limit_ms:int=Field(gt=0); memory_limit_mb:int=Field(gt=0); audit_log:bool=True; requires_sandbox:bool=False
class ToolRequest(BaseModel): tool:str=Field(min_length=1); input:dict[str,Any]=Field(default_factory=dict)
class ToolResult(BaseModel): request_id:UUID=Field(default_factory=uuid4); tool:str; ok:bool; output:Any=None; error:str|None=None; duration_ms:float

class MemoryType(str, Enum):
    working="working"
    episodic="episodic"
    semantic="semantic"
    project="project"
    failure="failure"
    reasoning="reasoning"
    skill="skill"
    decision="decision"

class MemoryWrite(BaseModel):
    type: MemoryType
    content: str = Field(min_length=1, max_length=50000)
    project_id: UUID | None = None
    task_id: UUID | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

class MemorySearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1000)
    type: MemoryType | None = None
    project_id: UUID | None = None
