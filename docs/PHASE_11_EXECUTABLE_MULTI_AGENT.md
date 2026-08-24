# Phase 11 — Executable Multi-Agent Runtime

Phase 11 now executes the registered specialist roles through the real Model Runtime.
Each role receives an isolated role-specific prompt and an independently routed `RoutingRequest`.
The runtime records the selected model/provider on successful agent results.

The system then performs a synthesis pass over successful specialist outputs to identify
agreements, contradictions, assumptions, uncertainty, and a recommendation.

Provider failures are explicit: an unavailable provider produces `FAILED` for that agent
and never creates placeholder findings. A run is `COMPLETED` only when all requested agents
and synthesis succeed, `PARTIAL` when some agents succeed, and `FAILED` when none succeed.

This phase does not grant agents arbitrary tool access. Tool execution remains behind the
existing permission and sandbox boundaries.

## Acceptance

- Every requested role is executed through Model Runtime.
- Roles can select different task-routing requirements.
- Provider failures are surfaced without fabricated answers.
- Successful results identify model/provider.
- Successful specialist outputs are synthesized.
- Existing authentication and permission boundaries remain active.
