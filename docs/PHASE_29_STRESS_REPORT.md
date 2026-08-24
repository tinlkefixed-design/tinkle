# Phase 29 Stress Report

The automated Phase-29 harness uses bounded concurrency to exercise the existing
integrated paths rather than adding new autonomous functionality.

| Scenario | Requests | Workers | Guard |
|---|---:|---:|---|
| Health | 160 | 8 | all 200; max < 2000 ms/request |
| Full integration smoke | 96 | 8 | all 200; max < 5000 ms/request |
| Integration status | 96 | 8 | all 200 |
| Failure/recovery | 2 | 1 | 401 then 200 |

These thresholds are local stress guards and are not production SLAs.
