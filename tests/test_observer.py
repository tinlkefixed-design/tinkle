from tinkle.observer import TinkleObserver, ObserverEventRequest

def test_observer_tracks_all_blueprint_metrics():
    obs = TinkleObserver()
    for metric in ['Accuracy','Hallucinations','Retrieval Quality','Memory Quality','Latency','Agent Loops','Failures','Model Drift','Resource Usage','Tool Errors','Security Events']:
        obs.observe(ObserverEventRequest(metric=metric, value=1.0, source='test'))
    snap = obs.snapshot()
    assert snap.phase == 23
    assert snap.total_events == 11
    assert {m.metric for m in snap.metrics} == set(['Accuracy','Hallucinations','Retrieval Quality','Memory Quality','Latency','Agent Loops','Failures','Model Drift','Resource Usage','Tool Errors','Security Events'])
    assert all(m.count == 1 for m in snap.metrics)

def test_observer_does_not_invent_values():
    snap = TinkleObserver().snapshot()
    assert snap.total_events == 0
    assert all(m.latest_value is None for m in snap.metrics)
