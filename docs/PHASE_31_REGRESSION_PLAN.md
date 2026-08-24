# Phase 31 — Regression Testing

Phase 31 is the Blueprint-defined full regression gate after Benchmark Arena.

## Scope
- Preserve all Phase 1–30 contracts.
- Re-run the complete automated test suite.
- Verify core task/project behavior.
- Verify Phase 30 Benchmark Arena remains available and versioned.
- Verify authentication boundaries remain enforced.
- Verify `/health` reports Phases 1–31.

## Rule
A regression is not accepted merely because the new Phase 31 code works. The complete suite must pass after integration.

## Execution
Run:

```bash
python scripts/phase31_regression.py
```

This command delegates to the repository's complete pytest suite and returns pytest's exit code.
