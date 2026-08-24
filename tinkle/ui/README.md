# Tinkle Open UI

This is the live interface layer for the current Tinkle system (through Phase 27).

Design target: a cyan holographic Tinkle core inspired by the supplied reference image, with:
- a central animated 3D/WebGL-style core;
- state reactions for listening, speaking, executing, and explaining;
- a notification stream for Tinkle activity;
- hypothesis and achievement panels;
- a dedicated interactive WebGL 3D explanation workspace with scene labels and step controls;
- movement/resizing of the core when explanation mode opens;
- draggable-ready actor surface and responsive layout;
- configured voice identity: `uju3wxzG5OhpWcoi3SMy`.

Voice ID is configuration metadata only until a real TTS provider/API is connected. Browser speech synthesis is used as the current local fallback.
