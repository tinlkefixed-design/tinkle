# Phase 11: Experiment Results Analysis and Evidence Update

## Architecture

Phase 11 adds `tinkle.experiment_results.ExperimentResultsEngine`, a thin orchestration layer over externally supplied results. It consumes existing Phase 10 plans and prediction references, while preserving Phase 8 decisions and Phase 9 validation as authoritative systems. It does not execute experiments, mutate decisions, pass validation, or create a second simulation, uncertainty, planner, graph, provenance, or authentication system.

## Inputs and Lifecycle

`ExperimentResult` requires an existing Phase 10 plan and explicit source reference, observations or measurements, conditions, evidence state, quality, assumptions, limitations, and provenance. `Observation` keeps value, units, uncertainty, condition, timestamp, source, and epistemic state explicit. The engine does not assume instruments are calibrated or sources are trustworthy.

The lifecycle is submitted -> quality/completeness check -> observation extraction -> prediction comparison -> hypothesis impact -> evidence-update proposal -> decision impact. Invalidation marks an analysis result invalidated and appends history; it never deletes prior records.

## Prediction Comparison

Predictions remain predictions. Numeric values are compared only when units are compatible. Missing values or nonnumeric values produce `INSUFFICIENT_DATA`; different declared units produce `INCOMPARABLE`. Difference and relative difference are deterministic. When both prediction and observation provide uncertainty, overlap availability is reported. A match is numerical evidence impact, not proof.

## Uncertainty and Quality

Phase 5 structures are reused indirectly through Phase 10 prediction/simulation references. Missing uncertainty is not invented and weakens interpretation. Quality (`UNKNOWN`, `INCOMPLETE`, `SUSPECT`, `ACCEPTABLE`, `HIGH_QUALITY`, `REJECTED`) is separate from truth or validation.

## Hypothesis and Decision Impact

Hypothesis impacts are `SUPPORTS`, `WEAKLY_SUPPORTS`, `NEUTRAL`, `WEAKLY_CONTRADICTS`, `CONTRADICTS`, `INSUFFICIENT_DATA`, or `INCOMPARABLE`. These describe evidence impact only and never mean proven or scientifically true. Decision impacts report whether an existing recommendation is supported, weakened, contradicted, unchanged, or requires reevaluation. The Phase 8 decision is never automatically mutated.

## Evidence Updates and Validation

Evidence updates are proposals. They retain previous state, proposed state, supporting and conflicting evidence IDs, assumptions, limitations, and provenance. An external measured result may support a Phase 9 validation requirement, but submitting a result does not pass validation. Simulated input remains `SIMULATED`; explicit measurement evidence may be `MEASURED`.

## Conflicts and Reproducibility

The model preserves result and observation references, source, conditions, units, uncertainty, provenance, and deterministic canonical hashes. Result analysis includes a serializable manifest with method and input hash. Multiple result conflict handling is represented through explicit comparison/analysis data; the system does not arbitrarily select one observation.

## Research Graph and API

The existing Research Graph is extended only with `PRODUCES_RESULT`, `OBSERVES`, `COMPARES_WITH`, `SUPPORTS_HYPOTHESIS`, `CONTRADICTS_HYPOTHESIS`, `UPDATES_EVIDENCE`, `IMPACTS_DECISION`, `SATISFIES_VALIDATION`, `CONFLICTS_WITH`, and `REPEATS`. Graph writes are intended to remain idempotent. API routes are authenticated under `/api/v1/experiment-results` for submission, analysis, comparisons, hypothesis/decision impact, evidence update, history, manifest, and invalidation.

## Security and Limitations

Result fields are untrusted data. The engine validates IDs and values and never executes uploaded content or treats references as paths or code. Phase 11 does not claim scientific truth, physical or experimental validation without explicit evidence, laboratory execution, hardware control, procurement, safety certification, manufacturing readiness, regulatory approval, statistical significance, commercial viability, autonomous experimentation, autonomous invention, or guaranteed reproducibility.
