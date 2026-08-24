# Phase 12 — Guardian Acceptance

Status: implemented and integrated.

The Guardian follows the Blueprint requirement that every important result is subjected to criticism. It checks for:
- Errors
- Contradictions
- Hidden Assumptions
- Missing Data
- Edge Cases
- Failure Modes
- Model Limitations

The implementation is a deterministic review boundary over supplied content. It does not fabricate external evidence and does not certify correctness.

API: `POST /api/v1/guardian/review`
