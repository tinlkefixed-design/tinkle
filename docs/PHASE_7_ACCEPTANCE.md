# Phase 7 — Meta-Mind Acceptance

The blueprint describes Meta-Mind as the highest-level coordinator and gives
the lifecycle:
Understand → Classify → Reframe → Plan → Select Model → Select Agents →
Select Tools → Execute → Verify → Synthesize.

This implementation establishes the coordinator, task classifier, planning
schema, model/tool routing hints, and verification strategy, integrated with
the existing API/auth system.

Important boundary: this phase creates orchestration and planning contracts;
it does not fabricate autonomous agents or pretend that every downstream
provider/tool is already connected. Agent System, Advanced Reasoning, and
later components remain separate phases.
