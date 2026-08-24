# Phase 21 — Skill Evolution Acceptance

Blueprint-backed requirements:
- A Skill stores Name, Procedure, Tools, Prerequisites, Benchmarks, Failure Modes, Confidence, and Version.
- The phase represents learning methods for solving problems, not merely storing information.

Implementation boundary:
- Skills are versioned and benchmark/failure observations are recorded.
- The Blueprint does not define an autonomous learning algorithm, so no fabricated autonomous learning capability is claimed.
- Confidence is evidence supplied by the caller; the engine does not manufacture evidence of success.

Integration:
- Phase 20 Failure Atlas output can be carried into Phase 21 failure modes.
- Phase 21 is exposed through authenticated API endpoints.
