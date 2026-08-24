# Phase 27 — Complete UI Acceptance

## Blueprint coverage
The Complete UI exposes the required main surfaces: Chat, Projects, Knowledge, Research, Experiments, Simulation, Agents, Memory, Skills, Discoveries, Hypotheses, Evidence, Tasks, System Health, and Settings.

## Tinkle visual behavior
- Holographic cyan 3D Tinkle core rendered with WebGL.
- Core state reactions for listening, speaking, executing, and explaining.
- Tinkle can be moved freely in the stage.
- Explaining state moves/resizes Tinkle to create a dedicated 3D explanation area.
- 3D explanation canvas supports model selection, rotation, zoom, step-by-step explanation, and contextual labels.
- Notification stream, hypothesis stream, and milestone stream are visible.
- Voice identity metadata is preserved as `uju3wxzG5OhpWcoi3SMy`; exact provider voice remains a provider boundary until connected.

## Integration
The UI is served by the same FastAPI application and uses the existing `/api/v1` boundary. It does not replace or rebuild previous phases.
