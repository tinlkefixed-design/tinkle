# Tinkle Scientific Discovery Roadmap — Stages 1–2 Acceptance

## Stage 1 — Scientific Core

Implemented as a real, callable layer under `tinkle/scientific_core/`:

- `ScientificProblem` schema with objective, domains, variables, parameters, constants, constraints, assumptions, known laws, unknowns, evidence, hypotheses, simulations, experiments, failures and verification state.
- `ProblemFormalizer` converts a natural-language mission into a structured problem and a problem graph.
- `DomainClassifier` supports multidisciplinary classification across physics, chemistry, biology, materials, energy, electronics, mechanical/electrical engineering, computer science, mathematics, control, fluid dynamics, thermodynamics, quantum and astronomy.
- `UnitDimensionEngine` provides deterministic SI conversion and dimensional compatibility checks.
- API endpoint: `POST /api/v1/scientific-core/formalize`.

### Boundary
Natural-language extraction is deliberately conservative. It does not pretend to infer equations, constants, laws, measurements or experimental evidence that were not supplied.

## Stage 2 — Deep Research & Knowledge Discovery

The existing knowledge layer was upgraded rather than duplicated:

- Source quality profile: authority, recency, relevance, reproducibility, independence, evidence quality.
- Evidence objects now preserve source quality and provenance identifiers.
- Scientific claims and unresolved conflicts are explicit objects.
- Search modes: broad, deep, contradiction, failure, prior-art, negative.
- Research engine can consume local indexed evidence first and optionally fetch public search leads for deep/contradiction/failure/prior-art/negative modes.
- External search hits remain leads; fetched text is marked `UNVERIFIED` until appropriate provenance evidence exists.
- Contradictory evidence is preserved instead of being silently collapsed into a single answer.
- Prior-art mode explicitly avoids claiming legal novelty or patentability.

## Verification policy

A calculated result, fetched source, simulation, inference or hypothesis is never silently promoted to experimental or validated status. Provenance remains the authority for verification state.

## Tests

New acceptance tests cover formalization/graph construction, multidisciplinary classification, unit dimensional safety, source-quality propagation, failure search and contradiction preservation.
