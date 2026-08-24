from tinkle.compiler import CognitiveCompiler
from tinkle.compiler_schemas import CognitiveCompileRequest
from tinkle.reframing.schemas import Representation


def test_cognitive_compiler_materializes_blueprint_flow():
    result = CognitiveCompiler().compile(
        CognitiveCompileRequest(
            problem="optimize x = 10 under a cost limit and produce the best result",
            context={"assumptions": ["x is continuous"], "constraints": ["cost <= 100"]},
        )
    )
    assert result.status == "COMPILED"
    assert result.selected_representation == Representation.optimization
    assert result.structured_problem.representation == Representation.optimization
    assert result.variables
    assert result.constraints
    assert isinstance(result.equations, list)
    assert result.graph.nodes is not None
    assert result.simulation.status == "SPECIFICATION_ONLY"
    assert "RESULT = SOLVE()" in result.code


def test_compiler_preserves_context_boundaries():
    result = CognitiveCompiler().compile(
        CognitiveCompileRequest(problem="design a sensor system", context={"variables": ["sensor_count"]})
    )
    assert any(v.name == "sensor_count" for v in result.variables)
    assert result.structured_problem.assumptions == []


def test_compiler_handles_plain_natural_language():
    result = CognitiveCompiler().compile(CognitiveCompileRequest(problem="analyze this system"))
    assert result.status == "COMPILED"
    assert result.structured_problem.elements
    assert result.graph.nodes == []
