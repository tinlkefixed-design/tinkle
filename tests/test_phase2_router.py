import pytest
from tinkle.core.errors import NoCompatibleModelError
from tinkle.core.schemas import Privacy, RoutingRequest, TaskType
from tinkle.router.catalog import default_catalog
from tinkle.router.router import ModelRouter

def test_simple_prefers_fast_or_local():
    r = ModelRouter(default_catalog()).route(
        RoutingRequest(prompt="hello", task_type=TaskType.simple)
    )
    assert r.selected_model in {"small-local", "fast-cloud"}

def test_complex_reasoning_selects_reasoning_model():
    r = ModelRouter(default_catalog()).route(
        RoutingRequest(prompt="prove this", task_type=TaskType.reasoning, difficulty=.95,
                       require_reasoning=True)
    )
    assert r.selected_model == "reasoning-cloud"

def test_private_selects_local():
    r = ModelRouter(default_catalog()).route(
        RoutingRequest(prompt="private", privacy=Privacy.private)
    )
    assert r.selected_model == "small-local"

def test_coding_selects_coding_model():
    r = ModelRouter(default_catalog()).route(
        RoutingRequest(prompt="write code", task_type=TaskType.coding, require_coding=True)
    )
    assert r.selected_model == "coding-cloud"

def test_context_constraint():
    r = ModelRouter(default_catalog()).route(
        RoutingRequest(prompt="long", context_tokens=100000, require_reasoning=True)
    )
    assert r.selected_model in {"reasoning-cloud", "research-cloud", "coding-cloud"}

def test_no_compatible_model():
    router = ModelRouter(default_catalog())
    with pytest.raises(NoCompatibleModelError):
        router.route(RoutingRequest(prompt="x", context_tokens=999999999))

def test_audit():
    router = ModelRouter(default_catalog())
    decision = router.route(RoutingRequest(prompt="x"))
    assert router.audit.events[-1].request_id == decision.request_id
