# Phase 8: Engineering Decision and Design Synthesis

## Architecture

Phase 8 adds `tinkle.engineering_decision.EngineeringDecisionEngine`, a deterministic decision ledger over existing Phase 7 candidates and evaluations. It does not generate candidates and does not replace Phase 3 invention intelligence, Phase 4 `PhysicsLabEngine`, Phase 5 `UncertaintyEngine`, Phase 6 research workflows, the Research Graph, provenance, persistence, or authentication.

The engine validates references, captures explicit criteria and evidence, screens hard constraints, preserves trade-offs, calculates an explainable weighted score, and emits an auditable decision plus history. It is process-local like the existing Phase 7 orchestration layer; a caller may inject the existing graph and Phase 7 engine.

## Artifacts and Lifecycle

`DecisionRequest` identifies the objective, Phase 7 requirement/candidate/evaluation references, evidence references, criteria, assumptions, unknowns, and provenance. `DecisionOption` points to the existing `DesignCandidate` and `DesignEvaluation`, including simulation, uncertainty, sensitivity, research, and limitation references. `DecisionEvidence`, `DecisionCriterion`, `Tradeoff`, `EngineeringDecision`, and `DecisionEvent` retain structured decision context.

Decision states are `UNDECIDED`, `DATA_INSUFFICIENT`, `CONSTRAINED`, `TRADEOFF_REQUIRED`, `RECOMMENDED`, `SELECTED`, and `REQUIRES_VALIDATION`. Selection is caller action and is permitted only for the current justified recommendation.

## Method and Trade-offs

Every criterion requires an explicit positive weight and numeric value for every option. Values are min-max normalized, with inversion for `MINIMIZE`; weighted sums are deterministic and tie-broken by candidate UUID. The canonical request/options representation is hashed with sorted JSON keys and excludes generated IDs/timestamps. Missing weights or values prevent recommendation.

Pairwise `Tradeoff` records preserve criterion, options, direction, numeric magnitude when available, evidence references, uncertainty, epistemic state, and limitations. Trade-offs are not hidden behind the aggregate score.

Hard constraint failures exclude an option from recommendation unless the request explicitly permits relaxation. Unknown constraints, evaluations, criteria, and unresolved unknowns remain visible and block recommendation. Soft constraints may be represented as criteria or evidence, but are never promoted to hard facts.

## Reused Evidence and Epistemic Integrity

Phase 4 simulation and Phase 5 uncertainty/sensitivity outputs are consumed through Phase 7 evaluations. Simulation remains `SIMULATED`; measured evidence remains `MEASURED`; source-backed evidence remains `SOURCE_BACKED`; assumptions remain `ASSUMED`. A high score never promotes epistemic state, and recommendation never becomes fact or validation.

Phase 6 question, hypothesis, prediction, experiment, result, comparison, and history artifacts are referenced by provenance/evidence IDs rather than recreated. The decision layer does not execute physical experiments or control hardware.

## Provenance and Research Graph

All artifacts retain source, requirement, candidate, evaluation, simulation, uncertainty, sensitivity, research, assumptions, method, criteria/weights, timestamp, canonical input hash, and limitations where applicable. Decision graph nodes use the existing Research Graph and `INFORMS`, `SUPPORTS_DECISION`, `REJECTS`, `TRADEOFF_WITH`, and `SELECTS` relationships. Graph state retains epistemic state; no parallel graph is created.

## API

Routes use the existing API-key auth and permissions:

- `POST /api/v1/engineering/decisions/evidence`
- `POST /api/v1/engineering/decisions/requests`
- `POST /api/v1/engineering/decisions/{request_id}/evaluate`
- `POST /api/v1/engineering/decisions/{request_id}/tradeoffs`
- `POST /api/v1/engineering/decisions/{request_id}/decide`
- `GET /api/v1/engineering/decisions/{request_id}`
- `GET /api/v1/engineering/decisions/{request_id}/history`

## Limitations

Phase 8 does not provide physical validation, scientific truth, manufacturing feasibility or certification, regulatory approval, statistical significance, commercial viability, safety certification, global optimization, autonomous invention, or autonomous physical experimentation. Its recommendation is an evidence-bound engineering decision under explicitly supplied criteria and limitations, not a validated fact.
