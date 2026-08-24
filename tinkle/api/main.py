from uuid import UUID
from pathlib import Path
from tinkle.api.knowledge import router as knowledge_router
from tinkle.api.provenance import router as provenance_router
from tinkle.api.metamind import router as metamind_router
from tinkle.api.reframing import router as reframing_router
from tinkle.api.compiler import router as compiler_router
from tinkle.api.planner import router as planner_router
from tinkle.api.multi_agent import router as multi_agent_router
from tinkle.api.guardian import router as guardian_router
from tinkle.api.math_engine import router as math_router
from tinkle.api.math_discovery import router as math_discovery_router
from tinkle.api.constraints import router as constraints_router
from tinkle.api.science_engine import router as science_router
from tinkle.api.engineering_engine import router as engineering_router
from tinkle.api.simulation_engine import router as simulation_router
from tinkle.api.advanced_simulation import router as advanced_simulation_router
from tinkle.api.evolution import router as evolution_router
from tinkle.api.adversarial_science import router as adversarial_science_router
from tinkle.api.autonomous_discovery import router as autonomous_discovery_router
from tinkle.api.hypothesis_universe import router as hypothesis_universe_router
from tinkle.api.research_engine import router as research_router
from tinkle.api.research_lab import router as research_lab_router
from tinkle.api.reality_engine import router as reality_router
from tinkle.api.research_graph import router as research_graph_router
from tinkle.api.discovery_engine import router as discovery_router
from tinkle.api.invention_engine import router as invention_router
from tinkle.api.cross_domain import router as cross_domain_router
from tinkle.api.failure_atlas import router as failure_atlas_router
from tinkle.api.skill_evolution import router as skill_evolution_router
from tinkle.api.self_evaluation import router as self_evaluation_router
from tinkle.api.observer import router as observer_router
from tinkle.api.self_improvement import router as self_improvement_router
from tinkle.api.security import router as security_router
from tinkle.api.privacy import router as privacy_router
from tinkle.api.integration import router as integration_router
from tinkle.api.benchmark_arena import router as benchmark_arena_router
from tinkle.api.experiment_engine import router as experiment_router
from tinkle.api.prototype_engine import router as prototype_router
from tinkle.api.innovation_platform import router as innovation_platform_router
from tinkle.api.visual3d import router as visual3d_router
from tinkle.api.engineering_brain import router as engineering_brain_router
from tinkle.api.exoskeleton import router as exoskeleton_router
from tinkle.api.cae import router as cae_router
from tinkle.api.cad import router as cad_router
from tinkle.api.digital_twin import router as digital_twin_router
from tinkle.api.manufacturing import router as manufacturing_router
from tinkle.api.design_optimization import router as design_optimization_router
from tinkle.api.innovation_campaign import router as innovation_campaign_router
from tinkle.api.invention_design import router as invention_design_router
from tinkle.api.engineering_decision import router as engineering_decision_router
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from tinkle.core.config import settings
from tinkle.core.errors import AuthenticationError, InvalidStateTransitionError, ProjectNotFoundError, TaskNotFoundError, PermissionDeniedError, NoCompatibleModelError
from tinkle.core.logging import configure_logging
from tinkle.core.schemas import ExportResponse, Job, Permission, Project, ProjectCreate, StructuredResponse, Task, TaskCreate, TaskResponse, RoutingRequest, RoutingDecision, ToolRequest, ToolResult, MemoryType, MemoryWrite, MemorySearchRequest, Privacy
from tinkle.core.container import data, jobs, projects, tasks, memory
from tinkle.api.deps import principal_from_key, require
from tinkle.core.auth import Principal
from tinkle.router.catalog import default_catalog
from tinkle.router.router import ModelRouter
from tinkle.tools.registry import ToolRegistry
from tinkle.tools.builtins import register_builtin_tools
from tinkle.tools.executor import ToolExecutor
from tinkle.hardware import build_hardware_sizing

configure_logging()
app=FastAPI(title=settings.app_name,version='2.56.0',description='Tinkle integrated system through Final Blueprint Compliance')
app.include_router(adversarial_science_router)
app.include_router(autonomous_discovery_router)
app.include_router(design_optimization_router)
app.include_router(innovation_campaign_router)
app.include_router(invention_design_router)
app.include_router(engineering_decision_router)

@app.get('/', include_in_schema=False)
def ui_root():
    return FileResponse(Path(__file__).resolve().parent.parent / 'ui' / 'index.html')

@app.get('/ui/{asset}', include_in_schema=False)
def ui_asset(asset: str):
    if asset not in {'styles.css', 'app.js'}:
        raise HTTPException(404, 'UI asset not found')
    return FileResponse(Path(__file__).resolve().parent.parent / 'ui' / asset)
model_router=ModelRouter(default_catalog()); tool_registry=ToolRegistry(); register_builtin_tools(tool_registry)
from tinkle.core.container import events, security_policy, privacy, observer
from tinkle.integration.engine import IntegrationCoordinator, IntegratedExecutionService, FinalSystemOrchestrator
tool_executor=ToolExecutor(tool_registry, events=events, policy=security_policy)
integration = IntegrationCoordinator(events=events, router=model_router, tools=tool_executor, memory=memory, observer=observer)
integrated_execution = IntegratedExecutionService(events=events, memory=memory, observer=observer)
final_orchestrator = FinalSystemOrchestrator()
@app.get('/health',response_model=StructuredResponse)
def health(): return StructuredResponse(ok=True,data={'status':'ok','system':'tinkle','phase':33,'current_phase':50,'phase_50_subphases':list(range(1,18)),'phases':list(range(1,34))})

from pydantic import BaseModel, Field

class IntegratedExecuteRequest(BaseModel):
 prompt: str = Field(min_length=1, max_length=20000)
 context: dict = {}

@app.post(f'{settings.api_prefix}/execute', response_model=dict)
def execute_integrated(req: IntegratedExecuteRequest, p: Principal = Depends(principal_from_key)):
 require(p, Permission.execute)
 return integrated_execution.execute(p.name, req.prompt, set(p.permissions), context=req.context)

@app.post(f'{settings.api_prefix}/final-orchestrate')
def final_orchestrate(req: IntegratedExecuteRequest, p: Principal = Depends(principal_from_key)):
 require(p, Permission.execute)
 return final_orchestrator.run(req.prompt, resources=req.context.get("resources") if req.context else None)

@app.get(f'{settings.api_prefix}/hardware-sizing')
def hardware_sizing(p:Principal=Depends(principal_from_key)):
 require(p,Permission.read)
 return build_hardware_sizing()
@app.post(f'{settings.api_prefix}/projects',response_model=Project)
def create_project(data_in:ProjectCreate,p:Principal=Depends(principal_from_key)):
 require(p,Permission.write)
 if not privacy.get(p.name).store_data: raise HTTPException(409,'Storage is disabled by privacy settings')
 return projects.create(data_in,p.name)
@app.get(f'{settings.api_prefix}/projects/{{project_id}}',response_model=Project)
def get_project(project_id:UUID,p:Principal=Depends(principal_from_key)):
 require(p,Permission.read)
 try:return projects.get(project_id,p.name)
 except ProjectNotFoundError as exc:raise HTTPException(404,'Project not found') from exc
@app.delete(f'{settings.api_prefix}/projects/{{project_id}}')
def delete_project(project_id:UUID,p:Principal=Depends(principal_from_key)):
 require(p,Permission.write)
 try:projects.delete(project_id,p.name);return {'ok':True}
 except ProjectNotFoundError as exc:raise HTTPException(404,'Project not found') from exc
@app.post(f'{settings.api_prefix}/tasks',response_model=TaskResponse)
def create_task(data_in:TaskCreate,p:Principal=Depends(principal_from_key)):
 require(p,Permission.write)
 if not privacy.get(p.name).store_data: raise HTTPException(409,'Storage is disabled by privacy settings')
 return TaskResponse(task=tasks.create(data_in,p.name),message='Task created')
@app.get(f'{settings.api_prefix}/tasks/{{task_id}}',response_model=Task)
def get_task(task_id:UUID,p:Principal=Depends(principal_from_key)):
 require(p,Permission.read)
 try:return tasks.get(task_id,p.name)
 except TaskNotFoundError as exc:raise HTTPException(404,'Task not found') from exc
@app.post(f'{settings.api_prefix}/tasks/{{task_id}}/run',response_model=Task)
def run_task(task_id:UUID,p:Principal=Depends(principal_from_key)):
 require(p,Permission.execute)
 try:return tasks.run(task_id,p.name)
 except TaskNotFoundError as exc:raise HTTPException(404,'Task not found') from exc
 except InvalidStateTransitionError as exc:raise HTTPException(409,str(exc)) from exc
@app.post(f'{settings.api_prefix}/jobs',response_model=Job)
def enqueue_job(job_type:str,p:Principal=Depends(principal_from_key)): require(p,Permission.execute); return jobs.enqueue(job_type)
@app.get(f'{settings.api_prefix}/jobs/{{job_id}}', response_model=Job)
def get_job(job_id: UUID, p: Principal=Depends(principal_from_key)):
 require(p,Permission.read)
 job=jobs.get(job_id)
 if job is None: raise HTTPException(404,'Job not found')
 return job

@app.post(f'{settings.api_prefix}/jobs/{{job_id}}/complete', response_model=Job)
def complete_job(job_id: UUID, p: Principal=Depends(principal_from_key)):
 require(p,Permission.execute)
 try: return jobs.update(job_id,'completed')
 except KeyError as exc: raise HTTPException(404,'Job not found') from exc

@app.post(f'{settings.api_prefix}/jobs/{{job_id}}/fail', response_model=Job)
def fail_job(job_id: UUID, p: Principal=Depends(principal_from_key)):
 require(p,Permission.execute)
 try: return jobs.update(job_id,'failed')
 except KeyError as exc: raise HTTPException(404,'Job not found') from exc

@app.post(f'{settings.api_prefix}/jobs/recover')
def recover_jobs(p: Principal=Depends(principal_from_key)):
 require(p,Permission.admin)
 return {'recovered':jobs.recover()}

@app.get(f'{settings.api_prefix}/jobs/size')
def job_queue_size(p:Principal=Depends(principal_from_key)): require(p,Permission.read); return {'size':jobs.size()}
@app.get(f'{settings.api_prefix}/data/export')
def export_data(p:Principal=Depends(principal_from_key)):
 require(p,Permission.read)
 if not privacy.get(p.name).allow_export: raise HTTPException(403,'Data export is disabled by privacy settings')
 return data.export_owner(p.name)
@app.delete(f'{settings.api_prefix}/data')
def delete_data(p:Principal=Depends(principal_from_key)):
 require(p,Permission.admin)
 if not privacy.get(p.name).allow_delete: raise HTTPException(403,'Data deletion is disabled by privacy settings')
 data.delete_owner(p.name)
 return {'ok':True,'message':'Owner data deleted'}
@app.get(f'{settings.api_prefix}/models')
def models(p:Principal=Depends(principal_from_key)): require(p,Permission.read); return {'models':model_router.catalog}
@app.post(f'{settings.api_prefix}/route',response_model=RoutingDecision)
def route(req:RoutingRequest,p:Principal=Depends(principal_from_key)):
 require(p,Permission.execute)
 settings_privacy = privacy.get(p.name)
 if settings_privacy.local_only or not settings_privacy.allow_cloud_models:
  req = req.model_copy(update={'privacy': Privacy.private})
 try:return model_router.route(req)
 except NoCompatibleModelError as exc:raise HTTPException(422,str(exc)) from exc
@app.get(f'{settings.api_prefix}/tools')
def tools(p:Principal=Depends(principal_from_key)): require(p,Permission.read); return {'tools':tool_registry.list()}
@app.post(f'{settings.api_prefix}/tools/execute',response_model=ToolResult)
def execute_tool(req:ToolRequest,p:Principal=Depends(principal_from_key)):
 require(p,Permission.execute); result=tool_executor.execute(req,p.permissions)
 if not result.ok and 'Sandbox' in (result.error or ''): raise HTTPException(409,result.error)
 return result

@app.post(f'{settings.api_prefix}/memory', response_model=object)
def write_memory(req:MemoryWrite,p:Principal=Depends(principal_from_key)):
 require(p,Permission.write)
 if not privacy.get(p.name).store_data: raise HTTPException(409,'Storage is disabled by privacy settings')
 return memory.write(owner=p.name,memory_type=req.type,content=req.content,project_id=req.project_id,task_id=req.task_id,metadata=req.metadata)

@app.post(f'{settings.api_prefix}/memory/search')
def search_memory(req:MemorySearchRequest,p:Principal=Depends(principal_from_key)):
 require(p,Permission.read)
 return {'items':memory.search(p.name,req.query,req.type)}

@app.get(f'{settings.api_prefix}/memory')
def list_memory(memory_type:MemoryType|None=None,project_id:UUID|None=None,p:Principal=Depends(principal_from_key)):
 require(p,Permission.read)
 return {'items':memory.list(p.name,memory_type,project_id)}

@app.delete(f'{settings.api_prefix}/memory/{'{'}memory_id{'}'}')
def delete_memory(memory_id:UUID,p:Principal=Depends(principal_from_key)):
 require(p,Permission.write)
 if not memory.delete(p.name,memory_id): raise HTTPException(404,'Memory not found')
 return {'ok':True}

app.include_router(knowledge_router)

app.include_router(provenance_router)

app.include_router(metamind_router)

app.include_router(reframing_router)
app.include_router(compiler_router)

app.include_router(planner_router)
app.include_router(multi_agent_router)
app.include_router(guardian_router)
app.include_router(math_router)
app.include_router(math_discovery_router)
app.include_router(constraints_router)
app.include_router(science_router)
app.include_router(engineering_router)
app.include_router(simulation_router)
app.include_router(visual3d_router)
app.include_router(advanced_simulation_router)
app.include_router(evolution_router)
app.include_router(hypothesis_universe_router)
app.include_router(research_router)
app.include_router(research_lab_router)
app.include_router(reality_router)
app.include_router(research_graph_router)
app.include_router(discovery_router)
app.include_router(invention_router)
app.include_router(cross_domain_router)
app.include_router(failure_atlas_router)
app.include_router(skill_evolution_router)
app.include_router(self_evaluation_router)
app.include_router(observer_router)
app.include_router(self_improvement_router)
app.include_router(security_router)
app.include_router(privacy_router)
app.include_router(integration_router)
app.include_router(benchmark_arena_router)
app.include_router(experiment_router)
app.include_router(prototype_router)
app.include_router(innovation_platform_router)
app.include_router(engineering_brain_router)
from tinkle.api.mechanism import router as mechanism_router
from tinkle.api.power_system import router as power_system_router
app.include_router(exoskeleton_router)
app.include_router(mechanism_router)
app.include_router(power_system_router)
app.include_router(cae_router)
app.include_router(cad_router)
app.include_router(digital_twin_router)
app.include_router(manufacturing_router)

# Executable model endpoint. Provider credentials are optional at startup;
# calls fail explicitly when no provider is configured instead of returning a fake answer.
from tinkle.router.runtime import ModelRuntime
from tinkle.router.providers import ProviderUnavailableError
from tinkle.core.schemas import ProviderResponse
runtime = ModelRuntime(model_router)

@app.post(f'{settings.api_prefix}/generate', response_model=ProviderResponse)
def generate(req: RoutingRequest, p: Principal = Depends(principal_from_key)):
    require(p, Permission.execute)
    privacy_settings = privacy.get(p.name)
    if privacy_settings.local_only or not privacy_settings.allow_cloud_models:
        req = req.model_copy(update={'privacy': Privacy.private})
    try:
        return runtime.generate(req)
    except ProviderUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except NoCompatibleModelError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

# Stage 7-8 engineering extensions: ergonomics and control architecture.
from tinkle.api.ergonomics import router as ergonomics_router
from tinkle.api.control import router as control_router
app.include_router(ergonomics_router)
app.include_router(control_router)
