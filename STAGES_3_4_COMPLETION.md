# Tinkle v2.48.0 — Stages 3 + 4

## Stage 3 — Actuator & Mechanism Engine
- Direct-drive and transmission-aware conceptual sizing
- Output torque/speed to input torque/speed conversion
- Efficiency, service factor, and safety factor
- Motor speed/torque constraint checks
- Explicit limitations and warnings
- API: `/api/v1/mechanism/design`

## Stage 4 — Power & Energy System
- Load aggregation
- Continuous and peak power estimates
- Runtime energy calculation
- Usable battery fraction
- Nominal/peak current estimation
- Optional battery mass estimate from supplied specific energy
- Explicit limitations and warnings
- API: `/api/v1/power-system/design`

## Validation
- Existing regression suite preserved.
- New Stage 3/4 tests added.
- Full pytest suite: PASS.
- Python compilation: PASS.

These are deterministic conceptual engineering models, not certification, fabrication instructions, or proof of human-use safety.
