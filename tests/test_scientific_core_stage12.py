from tinkle.scientific_core import DomainClassifier, ProblemFormalizer, UnitDimensionEngine

def test_formalizer_builds_problem_and_graph():
    problem, graph = ProblemFormalizer().formalize('Design a battery with voltage=12 V and mass=2 kg')
    assert problem.objective.startswith('Design a battery')
    assert 'Energy' in problem.domains or 'Electrical Engineering' in problem.domains
    assert problem.variables
    assert graph.problem_id == problem.id
    assert any(e['relation']=='depends_on' for e in graph.edges)

def test_multidomain_classifier():
    domains=DomainClassifier().classify('optimize a biological sensor circuit using protein and voltage')
    assert len(domains)>=2

def test_units_conversion_and_dimension_safety():
    u=UnitDimensionEngine()
    assert u.convert(1,'km','m') == 1000
    assert u.compatible('N','Pa') is False
    assert u.check_equation(['N','N']) is True
