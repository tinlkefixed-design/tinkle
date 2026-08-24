# Phase 26 — Privacy System

## Blueprint-derived scope
The user must have clear control over what is stored, what is sent to Cloud Models, what remains local, what is deleted, and what is exported. Local Mode must be available when needed.

## Implemented
- Per-owner privacy settings.
- Storage gate for projects, tasks, and memory writes.
- Cloud-model gate; Local Mode forces local routing.
- Export permission gate.
- Deletion permission gate.
- Authenticated privacy API.
- Explicit privacy settings returned by the API.

## API
- `GET /api/v1/privacy`
- `PUT /api/v1/privacy`
- `POST /api/v1/privacy/local-mode`

## Boundaries
This phase does not claim OS-level data erasure, legal compliance certification, or encryption-at-rest because those details are not specified by the Blueprint.
