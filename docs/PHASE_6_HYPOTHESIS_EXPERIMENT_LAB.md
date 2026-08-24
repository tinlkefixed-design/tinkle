# Phase 6 - Hypothesis and Experiment Lab

## Workflow

The lab records an auditable workflow:

`Question -> Hypothesis -> Prediction -> Experiment -> Result -> Comparison -> Hypothesis update`

The existing Phase 4 `PhysicsLabEngine` performs simulation experiments. The existing planning-only experiment boundary remains available for physical work; this phase does not control hardware or execute physical experiments.

## Epistemic boundaries

- Hypotheses begin `NEW` and remain hypotheses until explicit recorded evidence supports or contradicts them.
- Simulation results remain `SIMULATED` and are never treated as measurements.
- Human-recorded observations retain their supplied epistemic state and require explicit source and method provenance when labeled `MEASURED`.
- Missing predictions or results produce `REQUIRES_DATA` rather than a forced conclusion.
- Comparison uses deterministic range membership and does not claim statistical significance.

## Safety

Experiments are limited to `PLANNED`, `SIMULATION`, and `HUMAN_RECORDED` records. Physical execution, autonomous experimentation, and hardware control are outside this phase.
