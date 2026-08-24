# Tinkle Phase 50.3–50.4 Acceptance

## 50.3 Sandbox
- Sensitive execution has a real disposable subprocess boundary.
- POSIX CPU, address-space, file-size, file-descriptor and process-count limits are applied.
- Timeout and output caps are enforced.
- Credentials and proxy environment variables are not inherited.
- Temporary working directory is destroyed after execution.
- The local backend does **not** claim kernel-level network isolation; production network isolation must use a container/unshare backend before release.

## 50.4 Persistence Foundation
- Durable local memory survives process restart.
- Memory ownership and deletion remain enforced.
- SQLite WAL is used for the local durable mode.
- Production deployment contracts reserve PostgreSQL, Redis and Qdrant endpoints without pretending those services are running locally.

## Verification
- Phase-specific tests cover execution, timeout, environment isolation and persistence.
- A phase is not considered a final production database stack until PostgreSQL/Redis/Qdrant integration tests run against real services.
