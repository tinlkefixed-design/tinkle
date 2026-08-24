import json
from pathlib import Path
from tinkle.core.blueprint_audit import build_audit
from tinkle.tools.registry import ToolRegistry
from tinkle.tools.builtins import register_builtin_tools
from tinkle.tools.executor import ToolExecutor
from tinkle.core.schemas import Permission, ToolRequest, MemoryType
from tinkle.memory.service import MemoryService
from tinkle.knowledge.engine import KnowledgeEngine
from tinkle.knowledge.schemas import KnowledgeDocument, KnowledgeQuery
from tinkle.advanced.engines import InformationGainEngine, CausalWorldModel, DigitalTwin, KnowledgeGraph, ParallelDesignWorlds, AdversarialReality, DreamMode
from tinkle.persistence import RedisAdapter, QdrantAdapter

def test_76_sections_all_pass():
    a=build_audit(); assert a['counts']=={'PASS':76,'PARTIAL':0,'NOT_VERIFIED':0}; assert a['release_ready']

def test_full_tool_memory_knowledge_chain():
    r=ToolRegistry(); register_builtin_tools(r); e=ToolExecutor(r)
    assert e.execute(ToolRequest(tool='calculator',input={'expression':'6*7'}),set(Permission)).output['value']==42
    py=e.execute(ToolRequest(tool='python',input={'code':'print(20+22)'}),set(Permission)); assert py.ok and py.output['stdout'].strip()=='42'
    mem=MemoryService(); item=mem.write(owner='doctor',memory_type=MemoryType.semantic,content='verified Tinkle fact')
    assert mem.search('doctor','verified')[0].id==item.id
    k=KnowledgeEngine(); k.ingest(KnowledgeDocument(title='t',source='test',content='Tinkle uses evidence and verification.')); ans=k.search(KnowledgeQuery(query='evidence verification',top_k=1)); assert ans.evidence and ans.status=='SUPPORTED'

def test_final_reasoning_support_engines():
    assert InformationGainEngine().rank_actions([], [{'coverage':1,'cost':1}])[0]['information_gain_score']==1
    c=CausalWorldModel(); c.add_edge('a','b'); assert 'b' in c.descendants('a')
    assert DigitalTwin({'x':1}).what_if({'x':2})['x']==3
    g=KnowledgeGraph(); g.link('a','supports','b'); assert g.neighbors('a')[0]['node']=='b'
    assert ParallelDesignWorlds().generate([{'score':1}])['worlds']
    assert AdversarialReality().stress({'x':1},[{'x':0}])[0]['robust']
    assert DreamMode().generate(['idea'],[],['q'])

def test_persistence_compatibility():
    r=RedisAdapter('redis://local'); r.set('k','v'); assert r.get('k')=='v'
    q=QdrantAdapter('qdrant://local'); q.upsert([1.0,0.0],{'id':'x'}); assert q.search([1.0,0.0])[0]['id']=='x'

def test_ui_and_release_artifacts():
    assert Path('ui-react/package.json').is_file(); assert Path('ui-react/src/main.tsx').is_file(); assert Path('tinkle/ui/app.js').is_file()
    audit=json.loads(Path('docs/BLUEPRINT_COMPLIANCE_AUDIT.json').read_text()); assert audit['counts']['PASS']==76

def test_final_api_orchestration():
    from fastapi.testclient import TestClient
    from tinkle.api.main import app
    r=TestClient(app).post('/api/v1/final-orchestrate',headers={'X-API-Key':'dev-key'},json={'prompt':'integrated final workflow'})
    assert r.status_code==200 and r.json()['status']=='ORCHESTRATED'
