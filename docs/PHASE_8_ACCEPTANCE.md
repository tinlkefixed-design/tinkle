# Phase 8 — Problem Reframing Acceptance

The blueprint requires the Problem Reframing Engine to represent a problem as:
Mathematical, Physical, Causal, Graph, Information, Engineering, Economic,
Optimization, Constraint, or Algorithmic, then select the best representation.

This implementation:
- evaluates all ten representation candidates
- scores candidates from explicit problem cues
- selects the highest-scoring representation deterministically
- preserves assumptions and constraints
- emits a structured reframed problem
- exposes the capability through the integrated API

This phase does not silently implement the Cognitive Compiler (Phase 9).
