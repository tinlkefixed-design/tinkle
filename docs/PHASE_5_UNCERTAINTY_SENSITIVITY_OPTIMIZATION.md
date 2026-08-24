# Phase 5 - Uncertainty, Sensitivity, and Optimization

## Supported methods

- Explicit caller-supplied parameter intervals.
- Deterministic three-point interval grid: lower, nominal, upper.
- One-at-a-time normalized local finite difference sensitivity:

`S = (delta Y / Y) / (delta X / X)`

- Interval propagation through the existing Phase 4 mechanics simulator.
- Robustness variation: `maximum output - minimum output`, with optional normalized variation relative to the nominal output.
- Transparent bounded grid search with three points per supplied parameter.

## Scientific state

Parameter ranges retain their caller-supplied epistemic state. Derived sweep, sensitivity, uncertainty, robustness, and optimization results are `SIMULATED`. No result is presented as measured, experimentally validated, or statistically confident.

Unknown ranges are rejected. The engine never invents bounds or silently fills missing values. Provenance records the method, ranges, model/simulation relationship, assumptions, and evaluation count.

## Optimization guarantee and limitations

Optimization reports the best configuration found within the explicitly evaluated grid. It does not claim a global optimum, real-world optimality, or experimental validation.

This phase does not provide experimental uncertainty estimation, statistical confidence intervals, stochastic measurement models, adaptive/global optimization, or uncertainty distributions unless a future phase explicitly supplies and validates those methods.
