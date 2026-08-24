# Phase 25 — Security Hardening Acceptance

## Source-backed requirements

The Blueprint requires dangerous tools to be isolated, permissions to be defined for every Tool and Agent, important operations to be recorded in an Audit Log, and self-improvement to pass through Sandbox + Tests + Benchmarks + Security Review.

## Implemented

- Constant-time API-key comparison.
- Explicit API-key → permission mapping.
- Explicit API-key → principal mapping.
- Authentication and permission denials are emitted as auditable security events.
- Production-only API rate limiting with a configurable per-minute limit.
- Tool input size enforcement.
- Sensitive tools remain blocked until the Sandbox boundary is available.
- Tool execution/denial events are audited without storing tool input or output in the security event payload.
- Authenticated security status endpoint: `/api/v1/security/status`.
- Health and application version advanced to Phase 25 / v2.1.0.

## Explicit boundary

The Blueprint specifies Sandbox controls such as CPU, RAM, time, file, network, process, permission, and audit restrictions. The current Phase 25 implementation does not claim to provide OS-level process isolation or hard CPU/RAM enforcement; sensitive execution remains blocked until the dedicated Sandbox capability exists.
