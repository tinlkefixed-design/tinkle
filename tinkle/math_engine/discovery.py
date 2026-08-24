from __future__ import annotations

import math
from dataclasses import dataclass
from itertools import product
from typing import Any

import numpy as np
import sympy as sp

from tinkle.scientific_core.units import UnitDimensionEngine


@dataclass(frozen=True)
class CandidateModel:
    equation: str
    target: str
    features: tuple[str, ...]
    powers: tuple[tuple[int, ...], ...]
    coefficients: tuple[float, ...]
    complexity: int
    train_error: float
    test_error: float
    dimensional_consistent: bool
    robust: bool
    predictive_power: float
    status: str = "CANDIDATE"


class EquationDiscoveryEngine:
    """Deterministic, interpretable equation discovery.

    It deliberately produces *candidate* laws only. No result from this engine is
    experimental evidence or a scientific law. The search is bounded so it can be
    used safely inside long-running discovery jobs.
    """

    def __init__(self, max_terms: int = 8, max_exponent: int = 2) -> None:
        self.max_terms = max_terms
        self.max_exponent = max_exponent
        self.units = UnitDimensionEngine()

    def symbolic_regression(
        self, rows: list[dict[str, float]], target: str, variables: list[str] | None = None,
        units: dict[str, str] | None = None, top_k: int = 10, seed: int = 0,
    ) -> list[CandidateModel]:
        if len(rows) < 6:
            raise ValueError("At least 6 observations are required")
        variables = variables or [k for k in rows[0] if k != target]
        if not variables or target not in rows[0]:
            raise ValueError("Target and at least one variable are required")
        data = np.asarray([[float(r[v]) for v in variables] for r in rows], dtype=float)
        y = np.asarray([float(r[target]) for r in rows], dtype=float)
        if not np.isfinite(data).all() or not np.isfinite(y).all():
            raise ValueError("Dataset contains non-finite values")
        rng = np.random.default_rng(seed)
        order = rng.permutation(len(rows)); cut = max(3, int(len(rows) * 0.8))
        train, test = order[:cut], order[cut:]
        exps = self._monomials(len(variables))
        X = self._design(data, exps)
        candidates=[]
        for keep in range(1, min(self.max_terms, len(exps)) + 1):
            subset=exps[:keep]
            Xi=X[:, :keep]
            coef, *_=np.linalg.lstsq(Xi[train], y[train], rcond=None)
            pred_train=Xi[train]@coef; pred_test=Xi[test]@coef
            scale=max(1e-12,float(np.var(y[train])))
            train_error=float(np.mean((pred_train-y[train])**2)/scale)
            test_error=float(np.mean((pred_test-y[test])**2)/scale)
            features=tuple(self._feature_name(variables,e) for e in subset)
            consistent=self._dimensional_consistency(target, subset, variables, units or {})
            robust=self._noise_robust(Xi,y,train,coef,rng)
            candidates.append(CandidateModel(self._equation(target,features,coef),target,features,tuple(e for e in subset),tuple(float(c) for c in coef),keep+sum(sum(abs(x) for x in e) for e in subset),train_error,test_error,consistent,robust,max(0.0,1.0-test_error)))
        candidates.sort(key=lambda c:(not c.dimensional_consistent,c.test_error,c.complexity,-int(c.robust)))
        return candidates[:top_k]

    def differential_equation_discovery(
        self, times: list[float], series: list[float], *, max_degree: int = 3
    ) -> list[dict[str, Any]]:
        if len(times) != len(series) or len(times) < 8:
            raise ValueError("At least 8 aligned time-series observations are required")
        t = np.asarray(times, dtype=float); y = np.asarray(series, dtype=float)
        if not np.isfinite(t).all() or not np.isfinite(y).all() or np.any(np.diff(t) <= 0):
            raise ValueError("Times must be finite and strictly increasing")
        dy = np.gradient(y, t)
        terms = [np.ones_like(y)] + [y ** i for i in range(1, max_degree + 1)]
        X = np.column_stack(terms)
        coef, *_ = np.linalg.lstsq(X, dy, rcond=None)
        pred = X @ coef
        mse = float(np.mean((pred - dy) ** 2))
        equation = "dy/dt = " + " + ".join(f"{c:.8g}*y^{i}" if i else f"{c:.8g}" for i, c in enumerate(coef) if abs(c) > 1e-10)
        return [{"equation": equation, "mse": mse, "complexity": int(np.count_nonzero(abs(coef) > 1e-10)), "status": "CANDIDATE"}]

    @staticmethod
    def compare(candidates: list[CandidateModel]) -> list[dict[str, Any]]:
        if not candidates:
            return []
        return [
            {
                "equation": c.equation,
                "accuracy_score": max(0.0, 1.0 - c.test_error),
                "complexity": c.complexity,
                "generalization_score": max(0.0, 1.0 - c.test_error),
                "physical_consistency": c.dimensional_consistent,
                "robustness": c.robust,
                "predictive_power": c.predictive_power,
                "status": c.status,
            }
            for c in candidates
        ]

    def falsify(self, candidate: CandidateModel, rows: list[dict[str, float]], *, tolerance: float = 0.25) -> dict[str, Any]:
        failures = []
        for i, row in enumerate(rows):
            actual = float(row[candidate.target])
            values = []
            for powers in candidate.powers:
                term = 1.0
                for name, power in zip([v for v in row if v != candidate.target], powers):
                    term *= float(row[name]) ** power
                values.append(term)
            predicted = float(np.dot(np.asarray(values), np.asarray(candidate.coefficients)))
            rel = abs(predicted - actual) / max(1e-12, abs(actual))
            if rel > tolerance:
                failures.append({"index": i, "relative_error": rel})
        return {"survived": not failures, "failures": failures, "status": "FALSIFIED" if failures else "NOT_FALSIFIED"}

    def _monomials(self, n: int):
        exps = list(product(range(self.max_exponent + 1), repeat=n))
        exps.sort(key=lambda e:(sum(e), e))
        return exps[: min(len(exps), self.max_terms * 3)]

    @staticmethod
    def _design(data: np.ndarray, exps: tuple[tuple[int, ...], ...]) -> np.ndarray:
        return np.column_stack([np.prod(np.power(data, np.asarray(e)), axis=1) for e in exps])

    @staticmethod
    def _feature_name(vars_: list[str], e: tuple[int, ...]) -> str:
        parts = [v if p == 1 else f"{v}^{p}" for v, p in zip(vars_, e) if p]
        return "*".join(parts) or "1"

    @staticmethod
    def _equation(target: str, features: tuple[str, ...], coef: np.ndarray) -> str:
        terms = [f"{c:.8g}*{f}" for c, f in zip(coef, features) if abs(c) > 1e-10]
        return f"{target} = " + (" + ".join(terms) if terms else "0")

    def _dimensional_consistency(self, target: str, exps, variables: list[str], units: dict[str, str]) -> bool:
        if target not in units or any(v not in units for v in variables):
            return False
        # Coefficients are allowed to carry inferred dimensions (e.g. a in y=a*x^2).
        # A candidate becomes inconsistent only when explicit coefficient dimensions
        # are supplied and contradict the dimensions required by the equation.
        return all(all(isinstance(power, int) and power >= 0 for power in e) for e in exps)

    def validate_equation_dimensions(self, target: str, variables: list[str], powers: list[tuple[int, ...]], units: dict[str, str], coefficient_units: list[str] | None = None) -> dict:
        if target not in units or any(v not in units for v in variables):
            return {"consistent": False, "reason": "Missing target or variable units"}
        target_dim=self.units.dimension(units[target]); inferred=[]
        for e in powers:
            feature_dim=tuple(sum(p*d for p,d in zip(e,self.units.dimension(units[v]))) for v in variables)
            coeff_dim=tuple(a-b for a,b in zip(target_dim,feature_dim))
            inferred.append(coeff_dim)
        if coefficient_units is not None:
            if len(coefficient_units)!=len(powers):
                return {"consistent":False,"reason":"Coefficient-unit count mismatch"}
            for required, unit in zip(inferred, coefficient_units):
                if self.units.dimension(unit)!=required:
                    return {"consistent":False,"reason":f"Coefficient unit {unit} is dimensionally inconsistent"}
        return {"consistent":True,"inferred_coefficient_dimensions":inferred}

    @staticmethod
    def _noise_robust(X, y, train, coef, rng) -> bool:
        noise = rng.normal(0, max(1e-12, np.std(y[train]) * 0.01), size=len(train))
        noisy_coef, *_ = np.linalg.lstsq(X[train], y[train] + noise, rcond=None)
        return bool(np.linalg.norm(noisy_coef - coef) <= 0.25 * max(1.0, np.linalg.norm(coef)))
