from tinkle.hypothesis_universe import HypothesisUniverse, HypothesisRequest, HypothesisStatus

def test_hypothesis_lifecycle_generate_test_reject_modify_combine_retest():
    result = HypothesisUniverse().run(HypothesisRequest(
        question='Which design is better?',
        hypotheses=['A is better', 'B is better'],
        tests=[{'hypothesis_id':'H1','outcome':'reject','evidence':['test-1'], 'confidence':0.9}],
        modifications={'H2':'B is better under low power'},
        combinations=[['H1','H2']],
        retest=True,
    ))
    assert [h.id for h in result.hypotheses[:2]] == ['H1','H2']
    assert next(h for h in result.hypotheses if h.id == 'H1').status == HypothesisStatus.REJECTED
    assert 'H2M1' in result.retest_required
    assert any(h.id.startswith('HCOMB') for h in result.hypotheses)
    assert result.lifecycle == ['Generate','Test','Modify','Combine','Retest']

def test_no_hypotheses_is_explicit_empty_universe():
    result = HypothesisUniverse().run(HypothesisRequest(question='unknown'))
    assert result.hypotheses == []
    assert result.lifecycle == ['Generate']
