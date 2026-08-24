# Phase 12 — Guardian Repair Loop

The integrated execution path now treats high-severity Guardian findings as actionable feedback.

Workflow:

Meta-Mind → Planner → Multi-Agent → Guardian → Repair Context → Multi-Agent → Guardian

Rules:
- Only high-severity findings trigger automatic repair.
- The retry budget is bounded to 0–5 attempts.
- Provider failures stop the loop and are never replaced with fabricated output.
- Each attempt records Guardian findings and the resulting status.
- The final result remains reviewable; Guardian does not certify external truth.

Verification:
- pytest: PASS
- compileall: PASS
- scripts/run_checks.py: the configured environment is missing `ruff`, so the static-check portion cannot run until the development dependency is installed.
