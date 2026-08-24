# Phase 32 — Release Candidate

## Scope

Phase 32 is the Blueprint-defined **Release Candidate** phase. The Blueprint names the phase but does not prescribe a separate release algorithm, artifact format, or deployment target. Therefore this phase freezes the integrated system at a candidate version, verifies the existing acceptance gates, records the candidate metadata, and does not introduce new product capabilities.

## Candidate

- Candidate version: **v2.8.0**
- Base version: **v2.7.0 / Phase 31**
- Phase: **32 — Release Candidate**
- Phase sequence preserved: **1–32**

## Release-candidate gates

- Full automated regression suite executed.
- Compile check executed.
- Live HTTP smoke checks executed.
- Health reports Phase 32 and phases 1–32.
- UI root and OpenAPI endpoints remain reachable.
- Authentication boundaries remain covered by the regression suite.
- Benchmark Arena contract remains covered by the regression suite.
- No new autonomous capability, external provider, solver, or hardware claim is introduced by this phase.
- Artifact integrity and SHA-256 recorded.
- Documentation and verification record included in the candidate.

## Known toolchain limitations

Ruff and mypy are not counted as passing unless their executables are installed in the execution environment. They remain **DEFERRED** for this candidate.

## Status

**RELEASE CANDIDATE READY FOR PHASE 33 REVIEW**
