from tinkle.compiler import CognitiveCompiler
from tinkle.compiler_schemas import CognitiveCompileRequest


def test_phase9_compilation_is_bounded():
    problem = "design a system with x = 10, y = 20 under a cost limit" * 20
    result = CognitiveCompiler().compile(CognitiveCompileRequest(problem=problem))
    assert len(result.variables) <= 30
    assert len(result.equations) <= 30
    assert len(result.constraints) <= 30
