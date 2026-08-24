import pytest

from tinkle.math_engine import MathematicsEngine, MathMode, MathRequest


def test_exact_calculation_and_verification():
    result = MathematicsEngine().calculate(
        MathRequest(question="two plus two", expression="2 + 2", mode=MathMode.exact)
    )
    assert result.result == "4"
    assert result.exact_result == "4"
    assert result.verification.verified is True


def test_numerical_calculation_uses_substitution():
    result = MathematicsEngine().calculate(
        MathRequest(
            question="square root of x",
            expression="sqrt(x)",
            mode=MathMode.numerical,
            variables={"x": 9},
        )
    )
    assert result.numerical_result == pytest.approx(3.0)
    assert result.verification.verified is True


def test_invalid_expression_is_rejected():
    with pytest.raises(ValueError):
        MathematicsEngine().calculate(MathRequest(question="bad", expression="__import__('os')"))

@pytest.mark.parametrize("expression", ["1/0", "2**1001", "float('nan')", "__import__('os')"])
def test_unsafe_or_invalid_math_is_rejected(expression):
    with pytest.raises(ValueError):
        MathematicsEngine().calculate(MathRequest(question="invalid", expression=expression))


def test_non_finite_variable_is_rejected():
    with pytest.raises(ValueError):
        MathematicsEngine().calculate(
            MathRequest(question="bad variable", expression="x + 1", variables={"x": float("nan")})
        )


def test_single_argument_functions_are_supported():
    result = MathematicsEngine().calculate(
        MathRequest(question="sine", expression="sin(pi / 2)", mode=MathMode.exact)
    )
    assert result.result == "1"
    assert result.verification.verified is True
