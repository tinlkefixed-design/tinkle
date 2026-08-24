from tinkle.skill_evolution import SkillEvolution, SkillEvolutionRequest


def test_skill_contains_blueprint_fields():
    e = SkillEvolution()
    r = e.evolve(SkillEvolutionRequest(name='solve', procedure=['parse','verify'], tools=['math'], prerequisites=['input'], benchmarks=['exact'], failure_modes=['bad input'], confidence=0.8))
    s = r.skill
    assert s.name == 'solve'
    assert s.procedure == ['parse','verify']
    assert s.tools == ['math']
    assert s.prerequisites == ['input']
    assert s.benchmarks == ['exact']
    assert s.failure_modes == ['bad input']
    assert s.confidence == 0.8
    assert s.version == 1


def test_skill_evolution_versions_and_records_failure():
    e = SkillEvolution()
    first = e.evolve(SkillEvolutionRequest(name='solve', procedure=['a'], confidence=0.8)).skill
    second = e.evolve(SkillEvolutionRequest(name='solve', procedure=['a','b'], confidence=0.6, previous_skill_id=first.id, benchmark_passed=False, observed_failure='edge case')).skill
    assert second.version == 2
    assert 'edge case' in second.failure_modes
    assert second.confidence <= 0.49
