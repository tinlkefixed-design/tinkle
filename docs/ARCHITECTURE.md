# Tinkle Architecture

Current integrated phase chain:

Core → Model Router → Tool System → Memory → Knowledge → Provenance → Meta-Mind → Problem Reframing → Cognitive Compiler → Planner → Multi-Agent System → Guardian → Mathematics Engine → Science Engine → Engineering Engine → Simulation Engine → Research Engine → Hypothesis Universe → Discovery Engine → Failure Atlas → Skill Evolution → Self-Evaluation

Phase 9 consumes the structured representation selected by Problem Reframing and materializes the Cognitive Compiler stages:

Natural Language → Structured Problem → Variables → Constraints → Equations → Graph → Simulation → Code

Phase 10 provides deterministic task decomposition with verification and recovery boundaries.

Phase 11 provides ten independent agent role boundaries without fabricating external model/tool execution.

Phase 12 subjects important results to deterministic critical review across the Blueprint categories: Errors, Contradictions, Hidden Assumptions, Missing Data, Edge Cases, Failure Modes, and Model Limitations. Guardian is a review boundary and does not certify correctness or fabricate evidence.


## Phase 13 — Mathematics Engine
The Mathematics Engine sits after upstream reasoning/planning and provides a deterministic calculation boundary. It accepts structured mathematical input, performs exact or numerical calculation, then verifies the result. It does not fabricate an LLM/model-provider integration.


## Phase 14 — Science Engine
The Science Engine registers the six science modules named by the Blueprint: Physics, Chemistry, Biology, Materials Science, Energy, and Astronomy. Because the source does not specify their scientific algorithms or evidence providers, the implementation is an explicit typed integration boundary with authentication and evidence-required/limitation metadata; it does not fabricate scientific claims.


## Phase 16 — Simulation Engine
The Simulation Engine implements the Blueprint pipeline Model → Parameters → Simulation → Results → Visualization → Optimization. It provides a bounded scalar simulation capability and keeps domain-specific solvers and optimization objectives behind explicit boundaries.


Phase 17: Research Engine is integrated after Simulation and connects Knowledge → Evidence → Provenance/Verification → Guardian/Criticism → optional Simulation → Report.

## Phase 20 — Failure Atlas

Failure Atlas sits after Discovery Engine and records explicit failure knowledge in the Blueprint-defined shape. It is an authenticated boundary and does not claim autonomous causal inference.

## Phase 21 — Skill Evolution

Skill Evolution sits after Discovery Engine and Failure Atlas. It stores reusable problem-solving methods as versioned Skills with Name, Procedure, Tools, Prerequisites, Benchmarks, Failure Modes, Confidence, and Version. Failure Atlas observations can be carried into a skill's failure modes. Autonomous learning is an explicit future boundary because the Blueprint does not define its algorithm.


## Phase 22 — Self-Evaluation
Self-Evaluation sits after Skill Evolution. It preserves the seven Blueprint questions as structured observations and stores explicit improvements, failures, and remembered lessons through the existing Memory System. It does not claim autonomous evaluation or fabricate verification.


## Phase 24 — Controlled Self-Improvement

Self-improvement is isolated behind a governed lifecycle. Proposals cannot jump stages, and the final Production stage records human approval/readiness without performing a direct production mutation. This preserves the Blueprint path and the core rule that AI must not modify Production directly.

## Phase 26 — Security Hardening

Security hardening sits across the existing Core, Tool, Audit, and Controlled Self-Improvement boundaries. API keys map explicitly to principals and permissions; production requests are rate-limited; sensitive tools remain sandbox-gated; and security-relevant events are audited without persisting tool payloads in the event record.

## Open UI Layer — Phase 26 integration

The current Tinkle system exposes a live UI at `/` and static UI assets at `/ui/*`.
The UI is intentionally a separate presentation layer over the existing Phase 1–26 APIs.
It includes a cyan holographic 3D core, state-driven reactions (listening/speaking/executing/explaining), notifications, hypotheses, milestones, and a dedicated visual explanation area. The core can be moved freely by pointer/touch and is automatically repositioned/resized when explanation mode is active.

Voice identity is configured as `uju3wxzG5OhpWcoi3SMy`. The current environment uses browser speech synthesis as a local fallback; the configured ID is not claimed as an active provider voice until a compatible TTS provider credential is supplied.
