from tinkle.reframing.engine import ProblemReframingEngine
from tinkle.reframing.schemas import ReframingRequest, Representation

def test_math_representation():
    r=ProblemReframingEngine().reframe(ReframingRequest(problem="solve the equation for velocity"))
    assert r.selected_representation==Representation.mathematical

def test_engineering_representation():
    r=ProblemReframingEngine().reframe(ReframingRequest(problem="design a sensor system with materials and manufacturing constraints"))
    assert r.selected_representation==Representation.engineering

def test_optimization_representation():
    r=ProblemReframingEngine().reframe(ReframingRequest(problem="optimize the best design under a cost limit"))
    assert r.selected_representation==Representation.optimization

def test_all_representations_are_considered():
    r=ProblemReframingEngine().reframe(ReframingRequest(problem="analyze a system"))
    assert {x.representation for x in r.candidates}==set(Representation)
    assert r.status=="REFRAMED"
