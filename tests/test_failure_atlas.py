from tinkle.failure_atlas import FailureAtlas, FailureAtlasRequest


def test_failure_becomes_structured_knowledge():
    result = FailureAtlas().record(FailureAtlasRequest(
        failure="simulation timeout",
        cause="resource budget exceeded",
        conditions=["large model"],
        symptoms=["timeout"],
        detection=["timeout monitor"],
        prevention=["bounded resource budget"],
        lesson="enforce a resource budget before execution",
    ))
    assert result.status == "FAILURE_KNOWLEDGE_RECORDED"
    assert result.knowledge["failure"] == "simulation timeout"
    assert result.knowledge["cause"] == "resource budget exceeded"
    assert result.record.lesson.startswith("enforce")
