# Phase 19 — Discovery Engine Acceptance

## Blueprint basis
The Blueprint preserves **PHASE 19: Discovery Engine** in the 33-phase sequence. Its detailed discovery concept later in the Blueprint is the **Emergent Discovery Engine**: search for shared patterns across different fields; example: Physics Pattern + Biology Pattern + Mathematical Structure → New Hypothesis; the result must not be treated as fact until verified.

## Implemented scope
- Accept explicit pattern observations from multiple domains.
- Detect the same normalized pattern across at least two domains.
- Produce an auditable discovery candidate.
- Carry mathematical structures when supplied.
- Mark candidates `NEEDS_VERIFICATION` by default.
- Accept an explicit verification result without inventing one.
- Expose authenticated API: `POST /api/v1/discovery/discover`.
- Integrate with the Phase 1→18 application and health contract.

## Explicit boundaries
- No autonomous external search provider is claimed.
- No scientific truth oracle is claimed.
- No candidate is promoted to fact without explicit verification.
- Autonomous discovery/model generation beyond supplied observations is not claimed because the Blueprint does not specify its algorithm.
