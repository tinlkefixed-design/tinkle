# Phase 9: Validation, Traceability, and Reproducibility

## Purpose and Architecture

Phase 9 adds `tinkle.validation.ValidationEngine`, a small orchestration layer over the existing Phase 8 engineering decision engine. It records what must be validated, what evidence was supplied, how evidence connects to a decision, whether a gate is currently satisfied, and whether the decision has enough recorded inputs to be reproduced.

Phase 9 reuses Phase 8 decisions and criteria, Phase 7 candidates/evaluations, Phase 4 simulation identifiers, Phase 5 uncertainty/sensitivity identifiers, Phase 6 research references, the existing Research Graph, `ClaimStatus`, provenance bundle, persistence injection points, and authenticated API dependency. It does not replace or duplicate any of those systems.

## Validation Lifecycle

`ValidationRequirement` is distinct from an engineering requirement. An engineering requirement says what a design should satisfy; a validation requirement says what evidence must demonstrate before a decision is sufficiently validated for its declared purpose.

`ValidationRecord` supports `NOT_STARTED`, `REQUIRED`, `IN_PROGRESS`, `PASSED`, `FAILED`, `INCONCLUSIVE`, `BLOCKED`, and `NOT_APPLICABLE`. A `PASSED` record requires explicit evidence with `MEASURED` epistemic state. Simulation, prediction, source-backed material, and assumptions cannot satisfy that rule by themselves.

The gate reports `VALIDATION_NOT_REQUIRED`, `VALIDATION_REQUIRED`, `VALIDATION_READY`, `VALIDATED`, `VALIDATION_FAILED`, `VALIDATION_INCONCLUSIVE`, `INVALIDATED`, or `DATA_INSUFFICIENT`. A Phase 8 recommendation can coexist with `VALIDATION_REQUIRED`; recommendation and validation are separate states.

## Evidence Chains and Traceability

Evidence kinds are explicit: `DIRECT`, `DERIVED`, `SIMULATED`, `MEASURED`, `SOURCE_BACKED`, `ASSUMED`, and `UNKNOWN`. An `EvidenceChain` preserves direction from decision through candidate/evaluation and simulation or analysis references to evidence and provenance. Missing evidence and conflicts remain explicit.

`DecisionTrace` is machine-readable and contains requirements, candidates, evaluations, criteria, evidence IDs, validation IDs, graph relationships, assumptions, limitations, provenance, a canonical input hash, and method version. Timestamps are excluded from canonical trace content so identical immutable inputs produce the same trace hash.

## Reproducibility

`ReproducibilityManifest` records decision and evaluation IDs, criteria and weights, evidence and validation IDs, simulation model IDs, uncertainty references, assumptions, method versions, package metadata, random seed, deterministic mode, missing inputs, and canonical hashes. It reports `REPRODUCIBLE`, `PARTIALLY_REPRODUCIBLE`, `NON_REPRODUCIBLE`, or `UNKNOWN`. A decision with missing evaluation or criterion weights is not called reproducible.

## Contradictions and Invalidation

Numeric validation records under the same requirement, method, and units are checked for conflicting observed values. Conflicting evidence IDs are returned and the gate remains data-insufficient; the engine never chooses a value arbitrarily.

`InvalidationCondition` declares a possible trigger, such as a model change, changed geometry, contradicted assumption, failed validation, or an out-of-range parameter. Declaring a condition does not invalidate a decision. Explicitly triggering it records the evidence and causes the gate to report `INVALIDATED` without deleting prior history.

## Epistemic Guarantees

`UNKNOWN` remains unknown. `SIMULATED` remains simulated. `MEASURED` is preserved as measured and is required for a passed validation record. `SOURCE_BACKED` is not silently converted to experimental confirmation. No validation is marked passed without valid measured evidence, and no result claims scientific truth, physical safety, manufacturing readiness, certification, statistical significance, or real-world deployment.

## Graph and Provenance

The existing Research Graph is used with the minimal Phase 9 relationships `REQUIRES_VALIDATION`, `SUPPORTED_BY`, `TRACEABLE_TO`, `REPRODUCED_BY`, and `INVALIDATED_BY`. Edges are idempotent at the orchestration layer. Validation, trace, and requirement nodes retain epistemic state and provenance metadata.

Artifacts preserve source and model references, assumptions, limitations, method identifiers, timestamps, and canonical input/result hashes where relevant. History events preserve lifecycle changes and provenance rather than overwriting prior records.

## API

All mutation and read routes use the existing API-key authentication and permission model:

- `POST /api/v1/validation/requirements`
- `GET /api/v1/validation/requirements/{id}`
- `POST /api/v1/validation/records`
- `GET /api/v1/validation/records/{id}`
- `POST /api/v1/validation/decisions/{id}/gate`
- `GET /api/v1/validation/decisions/{id}/trace`
- `GET /api/v1/validation/decisions/{id}/evidence-chain`
- `GET /api/v1/validation/decisions/{id}/reproducibility`
- `POST /api/v1/validation/decisions/{id}/invalidation-conditions`
- `GET /api/v1/validation/decisions/{id}/history`

## Limitations and Non-goals

Phase 9 is an evidence, validation, traceability, and reproducibility layer. It does not execute laboratory work, control hardware, manufacture objects, certify safety, approve regulation, establish statistical significance, prove scientific truth, guarantee correctness, establish commercial viability, claim deployment readiness, perform global optimization, autonomously invent, replace humans, or claim physical validation without physical measurement.
