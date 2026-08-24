from __future__ import annotations
import hashlib, json, math, random, platform, sys
from dataclasses import dataclass
from typing import Any, Callable

@dataclass(frozen=True)
class Provenance:
    engine: str
    version: str
    random_seed: int
    input_hash: str
    environment: dict[str, str]


def _hash(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()


def euler_ode(initial: float, derivative: Callable[[float, float], float], dt: float, steps: int):
    if steps < 1 or dt <= 0 or not math.isfinite(dt): raise ValueError('invalid integration settings')
    t, x = 0.0, float(initial)
    out=[]
    for i in range(steps+1):
        if not math.isfinite(x): raise ValueError('simulation diverged to non-finite state')
        out.append({'step': i, 'time': t, 'state': x})
        x += dt * float(derivative(t, x)); t += dt
    return out


def monte_carlo_normal(mean: float, std: float, samples: int, seed: int):
    if samples < 1 or samples > 2_000_000: raise ValueError('samples out of bounds')
    if std < 0 or not all(math.isfinite(v) for v in (mean,std)): raise ValueError('invalid distribution')
    rng=random.Random(seed)
    values=[rng.gauss(mean,std) for _ in range(samples)]
    avg=sum(values)/samples
    var=sum((v-avg)**2 for v in values)/max(1,samples-1)
    return {'samples': samples, 'mean': avg, 'std': math.sqrt(var), 'min': min(values), 'max': max(values)}


def parameter_sweep(values: dict[str, list[float]], evaluator: Callable[[dict[str,float]], float]):
    names=list(values)
    if not names or any(not v for v in values.values()): raise ValueError('sweep requires non-empty parameter ranges')
    total=1
    for v in values.values(): total*=len(v)
    if total>100_000: raise ValueError('parameter sweep exceeds safety limit')
    rows=[]
    def rec(i, current):
        if i==len(names):
            score=float(evaluator(dict(current)))
            if not math.isfinite(score): raise ValueError('non-finite evaluator result')
            rows.append({'parameters':dict(current),'score':score}); return
        for x in values[names[i]]:
            if not math.isfinite(float(x)): raise ValueError('non-finite sweep value')
            current[names[i]]=float(x); rec(i+1,current)
    rec(0,{})
    return rows


def provenance(input_payload: Any, seed: int) -> dict[str, Any]:
    return {'engine':'Tinkle Scientific Simulation Engine','version':'7.0','random_seed':seed,
            'input_hash':_hash(input_payload),'environment':{'python':sys.version.split()[0],'platform':platform.platform()}}
