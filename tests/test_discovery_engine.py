from tinkle.discovery_engine import DiscoveryEngine, DiscoveryRequest, PatternObservation, DiscoveryStatus

def test_cross_domain_pattern_creates_unverified_candidate():
    result = DiscoveryEngine().discover(DiscoveryRequest(
        question='Find a shared principle',
        observations=[
            PatternObservation(domain='Physics', pattern='feedback loop', evidence=['p1'], confidence=0.8),
            PatternObservation(domain='Biology', pattern='feedback loop', evidence=['b1'], confidence=0.7),
        ],
        mathematical_structures=['differential equation'],
    ))
    assert result.status == 'DISCOVERY_CANDIDATES_FOUND'
    assert len(result.candidates) == 1
    assert result.candidates[0].source_domains == ['Physics', 'Biology']
    assert result.candidates[0].status == DiscoveryStatus.NEEDS_VERIFICATION

def test_single_domain_does_not_become_cross_domain_discovery():
    result = DiscoveryEngine().discover(DiscoveryRequest(
        question='Find shared principle',
        observations=[PatternObservation(domain='Physics', pattern='feedback loop')],
    ))
    assert result.candidates == []
    assert result.cross_domain is False

def test_explicit_verification_is_respected_not_invented():
    result = DiscoveryEngine().discover(DiscoveryRequest(
        question='verify candidate',
        observations=[
            PatternObservation(domain='Physics', pattern='symmetry', confidence=1),
            PatternObservation(domain='Biology', pattern='symmetry', confidence=1),
        ],
        verify=True,
        verification_result='verified',
    ))
    assert result.candidates[0].status == DiscoveryStatus.VERIFIED
