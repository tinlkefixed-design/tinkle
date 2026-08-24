# Phase 10: Experiment Design and Research Action Planning

## Purpose and Architecture

Phase 10 adds `tinkle.experiment_planning.ExperimentPlanningEngine`, a planning-only orchestration layer. It converts explicit research objectives, hypotheses, candidate/decision references, validation requirements, uncertainty context, variables, measurements, conditions, and predictions into auditable experiment plans.

It reuses Phase 2 Research Graph, Phase 4 simulation references, Phase 5 uncertainty/sensitivity references, Phase 6 research artifacts by ID, Phase 7 candidate/evaluation state, Phase 8 decisions, Phase 9 validation requirements, the existing provenance bundle, `ClaimStatus`, persistence injection, and API authentication. It does not replace or duplicate those systems, and the existing generic `experiment_engine` remains unchanged.

## Domain Models and Lifecycle

`ResearchObjective` describes the research question or action target. `ExperimentObjective` identifies whether the plan discriminates hypotheses, measures a parameter, validates a requirement, reduces uncertainty, tests a relationship, or distinguishes candidates. `ExperimentalVariable`, `MeasurementSpecification`, and `ExperimentalCondition` keep roles, units, bounds, methods, ranges, assumptions, and uncertainty explicit.

`Prediction` is always `PREDICTED` and normally `SIMULATED`; `ExpectedOutcome` describes interpretations without upgrading a prediction. `ExperimentPlan` stores hypotheses, candidates, decisions, validation requirements, controls, conditions, measurements, predictions, outcomes, acceptance criteria, prerequisites, risks, limitations, estimates, manifest, provenance, and deterministic hash.

Plan statuses are `DRAFT`, `READY`, `BLOCKED`, `REQUIRES_DATA`, `REQUIRES_VALIDATION`, `APPROVED_FOR_REVIEW`, `EXECUTED_EXTERNALLY`, `RESULTS_PENDING`, `COMPLETED`, and `INVALIDATED`. Phase 10 creates plans as `READY` or `BLOCKED`; it never executes them or marks them executed. External result references require measured or source-backed state and transition only the plan reference to `EXECUTED_EXTERNALLY`.

## Information-Value Method

The planner reports **estimated information value**, not guaranteed information gain. The bounded score is:

`0.35 * uncertainty_reduction + 0.30 * hypothesis_discrimination + 0.20 * validation_relevance + 0.15 * decision_relevance - 0.10 * prerequisite_burden`

Each factor is bounded to `[0, 1]`, and the final value is clamped and rounded to six decimal places. Uncertainty reduction is based on explicitly supplied variable uncertainty; discrimination is higher when multiple hypotheses are declared; validation and decision relevance require explicit references. Missing data and prerequisites reduce the estimate. The method, inputs, and hash are included in the reproducibility manifest.

## Uncertainty, Decision, and Validation Integration

Phase 5 uncertainty and sensitivity outputs are consumed as references and are not recomputed. A priority based on those references means only “priority derived from current model/sensitivity information”; it is not a claim of scientific importance.

Phase 8 decisions contribute candidate, evaluation, criterion, and decision references. A plan can target a decision with simulation-only evidence, but the decision remains unresolved until the existing Phase 9 validation process receives appropriate external evidence.

Phase 9 validation requirements are references. Creating or completing a plan does not satisfy validation. The intended lifecycle is validation required -> plan -> external execution -> registered evidence -> validation evaluation.

## Safety Boundary and Missing Data

Missing variables, measurements, measurement methods, units, or required validation references produce structured missing data and a `BLOCKED` plan. Risk or condition text indicating hazard, danger, human involvement, high risk, or safety adds `REQUIRES_HUMAN_REVIEW` and blocks the plan until explicitly included as a prerequisite. The engine never controls equipment, procures resources, authorizes dangerous work, or runs physical experiments.

## Provenance and Reproducibility

Every plan records objective, hypothesis, candidate, decision, validation, simulation, evidence, uncertainty, model, assumption, limitation, method, timestamp, and canonical hash references where supplied. The manifest includes planner/method versions, IDs, variable and measurement definitions, uncertainty configuration, simulation/evidence references, assumptions, limitations, and canonical hash. Timestamps and generated UUIDs do not enter the canonical content hash.

## Research Graph

The existing graph is reused with minimal planning relationships: `PLANS_EXPERIMENT`, `TARGETS_HYPOTHESIS`, `DISCRIMINATES`, `REDUCES_UNCERTAINTY`, `ADDRESSES_VALIDATION`, `REQUIRES_MEASUREMENT`, `PREDICTS_OUTCOME`, `REQUIRES_PREREQUISITE`, and `RESULTS_FROM`. Objective and plan artifacts retain provenance and epistemic state. Repeated graph insertion is idempotent.

## API

Authenticated routes are provided under `/api/v1/experiments`:

- `POST /objectives`
- `GET /objectives/{id}`
- `POST /experiment-objectives`
- `POST /plans`
- `GET /plans/{id}`
- `POST /plans/{id}/validate`
- `POST /plans/{id}/compare`
- `GET /plans/{id}/trace`
- `GET /plans/{id}/manifest`
- `GET /plans/{id}/history`
- `POST /plans/{id}/results/references`
- `POST /plans/{id}/invalidate`
- `GET /plans/{id}/missing-data`
- `POST /plans/recommend`

## Limitations and Non-goals

Phase 10 does not claim physical experiment execution, laboratory automation, autonomous experimentation, scientific truth, discovery, hypothesis confirmation, manufacturing readiness, regulatory approval, safety certification, statistical significance, real-world measurement, procurement, hardware control, deployment readiness, global optimality, guaranteed information gain, or autonomous invention. It plans research actions and preserves the distinction between plans, predictions, simulations, measurements, validations, recommendations, and facts.
