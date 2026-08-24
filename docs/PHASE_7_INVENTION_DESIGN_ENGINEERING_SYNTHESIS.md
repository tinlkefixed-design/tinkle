# Phase 7: Invention Design and Engineering Synthesis

## Architecture

Phase 7 adds `tinkle.invention_design.InventionDesignEngine`, an orchestration layer. It does not replace Phase 3 invention generation, Phase 4 `PhysicsLabEngine`, Phase 5 `UncertaintyEngine`, Phase 6 `ResearchLab`, the existing Research Graph, provenance models, persistence, or authentication.

The flow is: requirements -> candidate -> deterministic evaluation -> comparison. A candidate may reference an existing mechanics simulation. When explicit, known parameter intervals are supplied, the existing uncertainty engine provides interval propagation and local sensitivity results.

## Data Models and Lifecycle

`EngineeringRequirement` keeps target, bounds, units, source artifact, provenance, epistemic state, priority, hard/soft classification, assumptions, and limitations. `DesignParameter` permits an unknown value; no default is inferred. `DesignCandidate` contains components, parameters, model/geometry references, requirement IDs, provenance, and lifecycle state.

Candidate lifecycle values are `PROPOSED`, `EVALUATED`, `SUPPORTED`, `REJECTED`, and `REQUIRES_DATA`. Evaluation can set `EVALUATED`, `REJECTED`, or `REQUIRES_DATA`; it never silently sets `SUPPORTED` or calls a candidate a validated invention.

## Constraint Analysis and Metrics

For each requirement, the evaluator emits `PASS`, `FAIL`, or `UNKNOWN`, the required condition, actual value, margin when numeric, provenance, and epistemic state. Missing values and unknown requirements are `UNKNOWN`. A complete evaluation score defaults to the fraction of passed constraints; callers may supply an objective score.

Comparison returns `REQUIRES_DATA` when any candidate lacks an evaluation, has unknown constraints, or lacks a score. Otherwise it sorts descending by score and breaks ties by candidate UUID, making ranking repeatable. This is bounded ordering, not global optimization.

## Provenance and Epistemic Rules

Design artifacts carry originating research, hypothesis, prediction, experiment, simulation, analysis, model, assumptions, limitations, creation time, method, and a deterministic input hash where applicable. Graph nodes retain the artifact provenance in metadata and their epistemic state.

No transition from `UNKNOWN` to `ASSUMED`, `ASSUMED` to `SOURCE_BACKED`, `SIMULATED` to `MEASURED`, hypothesis to fact, or candidate to validated invention occurs implicitly. Simulation and uncertainty outputs remain `SIMULATED`; computational pass/fail is not experimental evidence.

## Research Graph

Existing graph storage is reused. Phase 7 adds only `SATISFIES`, `CONSTRAINED_BY`, `EVALUATED_BY`, `OUTPERFORMS`, `VIOLATES`, and `REQUIRES_DATA` relationship vocabulary. Candidate and requirement nodes retain their epistemic state and provenance metadata. The current implementation uses `CONSTRAINED_BY`; evaluation relationships can be added when a persisted evaluation node is introduced.

## API

All routes use the existing API-key authentication and permission dependencies:

- `POST /api/v1/invention/requirements`
- `POST /api/v1/invention/candidates`
- `GET /api/v1/invention/candidates/{id}`
- `POST /api/v1/invention/candidates/{id}/evaluate`
- `POST /api/v1/invention/candidates/compare`
- `GET /api/v1/invention/candidates/{id}/history`

## Determinism and Limitations

Physics and Phase 5 analyses are reused as supplied. Input hashes use canonical JSON with sorted keys. Candidate comparison uses a stable UUID tie-break. The system does not claim real-world validation, experimental success without measurements, physical-world safety, manufacturability, commercial viability, global optimization, statistical significance, engineering certification, autonomous invention, or autonomous physical experimentation.

Phase 7 is an auditable engineering synthesis and design-evaluation foundation. It does not create a second knowledge, graph, simulation, uncertainty, provenance, hypothesis, persistence, or authentication system.
