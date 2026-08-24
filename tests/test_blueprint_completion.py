from tinkle.advanced.engines import *
from tinkle.persistence import PostgreSQLAdapter, RedisAdapter, QdrantAdapter
from tinkle.memory.service import MemoryService
from tinkle.core.schemas import MemoryType

def test_information_gain():
    out=InformationGainEngine().rank_actions([], [{"name":"a","coverage":.9,"cost":1},{"name":"b","coverage":.5,"cost":2}]); assert out[0]["name"]=="a"

def test_causal_and_twin():
    c=CausalWorldModel(); c.add_edge("cause","effect"); assert "effect" in c.descendants("cause")
    t=DigitalTwin({"x":1}); assert t.what_if({"x":2})["x"]==3

def test_research_radar_and_dream():
    assert ResearchRadar().scan(["physics"])[0]["kind"]=="watch_item"
    assert DreamMode().generate(["idea"],[],["question"])[0]["status"]=="HYPOTHESIS"

def test_memory_evolution_attention_design():
    assert MemoryEvolution().consolidate([{"type":"x","content":"a"},{"type":"x","content":"a"}])["count"]==1
    assert AttentionAllocator().allocate({"cpu":10},[{"priority":1}])[0]["allocation"]["cpu"]==10
    assert "worlds" in ParallelDesignWorlds().generate([{"score":1}])

def test_adversarial_observer_security():
    assert AdversarialReality().stress({"x":1},[{"x":2}])[0]["robust"]
    assert ObserverHealth().evaluate({"latency":1})["healthy"]
    assert SecurityCapabilityMatrix().verify({k:True for k in SecurityCapabilityMatrix.CAPABILITIES})["complete"]

def test_persistence_adapters():
    p=PostgreSQLAdapter("sqlite://./data/test_provider.db"); assert p.connect(); assert p.status().available
    r=RedisAdapter("redis://local"); r.set("x",1); assert r.get("x")==1
    q=QdrantAdapter("qdrant://local"); q.upsert([1,0],{"id":1}); assert q.search([1,0])[0]["id"]==1

def test_durable_memory():
    path="./data/test_memory_completion.db"; m=MemoryService(path); item=m.write(owner="u",memory_type=MemoryType.semantic,content="Tinkle knowledge")
    assert m.search("u","knowledge")[0].id==item.id
