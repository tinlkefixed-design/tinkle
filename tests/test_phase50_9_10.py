from pathlib import Path
from tinkle.core.jobs import JobQueue
from tinkle.benchmark_arena import BenchmarkArena


def test_durable_job_restart_recovery(tmp_path):
    db=tmp_path/'jobs.db'
    q=JobQueue(str(db)); j=q.enqueue('research'); assert q.next().id==j.id
    q2=JobQueue(str(db)); recovered=q2.get(j.id)
    assert recovered is not None and recovered.status=='queued'
    assert q2.size()==1


def test_job_lifecycle(tmp_path):
    q=JobQueue(str(tmp_path/'jobs.db')); j=q.enqueue('task')
    running=q.next(); assert running and running.status=='running'
    done=q.update(j.id,'completed'); assert done.status=='completed'
    assert q.size()==0


def test_benchmark_executes_real_checks():
    run=BenchmarkArena('2.35.0').run(version='v2.35.0')
    assert run['total']==13
    assert run['score']>=90
    assert all('latency_ms' in r for r in run['results'])
