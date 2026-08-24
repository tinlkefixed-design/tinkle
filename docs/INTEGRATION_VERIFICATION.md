# Tinkle Integrated System — Phase 1 + 2 + 3

The three completed phases are merged into one Tinkle codebase.

## Integration surface
- Phase 1 Core: tasks, projects, jobs, state, audit/export, auth/API.
- Phase 2 Model Router: model catalog, constraints, scoring, fallback, routing audit.
- Phase 3 Tool System: registry, permissions, execution boundary, tool audit.
- Unified API exposes all three areas.

## Verification
`pytest -q` => **41 passed**.

The suite includes the original Phase 1 tests plus Phase 2, Phase 3, and new cross-component integration tests.

Sensitive Python/code/scientific execution remains blocked behind the Sandbox boundary, rather than pretending in-process execution is isolated.
