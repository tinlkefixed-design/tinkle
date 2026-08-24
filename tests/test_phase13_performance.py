import time

from tinkle.math_engine import MathematicsEngine, MathMode, MathRequest


def test_math_engine_performance_smoke():
    engine = MathematicsEngine()
    request = MathRequest(question="performance", expression="sqrt(144) + 2**3", mode=MathMode.numerical)
    start = time.perf_counter()
    for _ in range(100):
        result = engine.calculate(request)
        assert result.verification.verified is True
    elapsed = time.perf_counter() - start
    assert elapsed < 5.0
