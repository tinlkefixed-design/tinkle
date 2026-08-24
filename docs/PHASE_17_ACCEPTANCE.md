# Phase 17 — Research Engine Acceptance

## Blueprint alignment
Phase 17 preserves the exact name **Research Engine** and the required pipeline:

**Question → Search → Sources → Evidence → Knowledge → Hypotheses → Analysis → Simulation → Criticism → Verification → Report**.

The implementation does not silently add capabilities not specified by the Blueprint.

## Implementation
- Structured research request and result models.
- Search stage backed by the existing Knowledge Engine.
- Source and Evidence normalization.
- Explicit Hypotheses collection; hypotheses are never promoted to facts automatically.
- Analysis stage.
- Simulation integration with Phase 16 when a simulation model is explicitly supplied.
- Criticism through the existing Guardian.
- Verification through existing Provenance records.
- Report generation with status, confidence, evidence, simulation state, and limitations.
- Authenticated API: `POST /api/v1/research/run`.

## Integration
Integrated into the full Phase 1→17 API application and health chain.

## Boundaries
The Blueprint does not specify a live web-search provider, search API, ranking model, or external evidence service for Phase 17. Therefore the current Search stage searches the configured Knowledge Engine and explicitly reports when no external provider is configured. It does not claim live internet research.
