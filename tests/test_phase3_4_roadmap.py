from tinkle.math_engine.discovery import EquationDiscoveryEngine
from tinkle.constraint_engine import ConstraintAnalysisEngine, ConstraintStatus
from tinkle.scientific_core.schemas import ScientificProblem, Constraint, ConstraintKind


def test_symbolic_regression_recovers_quadratic_candidate_and_keeps_candidate_status():
    rows=[{"x":float(x),"y":2*x*x+3*x+1} for x in range(1,31)]
    e=EquationDiscoveryEngine(max_terms=8,max_exponent=2)
    models=e.symbolic_regression(rows,"y",["x"],units={"x":"m","y":"m"},top_k=10,seed=1)
    assert models
    assert all(m.status=="CANDIDATE" for m in models)
    assert any(m.test_error < 1e-8 for m in models)


def test_dimensional_consistency_rejects_wrong_equation_basis():
    rows=[{"t":float(t),"x":2*t*t} for t in range(1,20)]
    e=EquationDiscoveryEngine()
    models=e.symbolic_regression(rows,"x",["t"],units={"t":"s","x":"m"},top_k=5)
    check=e.validate_equation_dimensions("x", ["t"], [(2,)], {"t":"s","x":"m"}, coefficient_units=["s"])
    assert check["consistent"] is False


def test_falsification_is_explicit():
    rows=[{"x":float(x),"y":x*x} for x in range(1,10)]
    e=EquationDiscoveryEngine()
    c=e.symbolic_regression(rows,"y",["x"],top_k=1)[0]
    attacked=[{"x":1.0,"y":100.0}]
    result=e.falsify(c,attacked,tolerance=0.1)
    assert result["status"]=="FALSIFIED"


def test_constraint_engine_distinguishes_technology_from_fundamental():
    e=ConstraintAnalysisEngine()
    tech=e.classify("current technology cannot manufacture this geometry")
    fundamental=e.classify("speed of light limit")
    assert tech.status==ConstraintStatus.RELAXABLE
    assert fundamental.kind==ConstraintKind.fundamental
    assert "impossibility" in fundamental.reason.lower()


def test_no_constraints_does_not_claim_impossibility():
    p=ScientificProblem(objective="solve a new engineering problem")
    r=ConstraintAnalysisEngine().assess_problem(p)
    assert r.conclusion != "PROVED_IMPOSSIBLE"
    assert r.proof_level=="NONE"


def test_relaxation_candidates_are_generated():
    p=ScientificProblem(objective="x", assumptions=["ideal gas", "constant temperature"], constraints=[Constraint(kind=ConstraintKind.technology,expression="current technology limit")])
    candidates=ConstraintAnalysisEngine().relax_assumptions(p)
    assert len(candidates)>=2
