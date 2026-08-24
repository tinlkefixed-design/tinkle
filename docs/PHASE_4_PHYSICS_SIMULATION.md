# Phase 4 - Physics and Simulation Lab

## Supported

- Typed scientific models and input quantities.
- One-dimensional Newtonian motion with `F = m a`.
- Explicit Euler integration with deterministic constant-force motion.
- Kinetic energy, gravitational potential energy, momentum, and Hooke's law spring force.
- Research Graph links for model, simulation, parameters, and simulated result.
- Explicit Reality Engine states and input provenance.

## Not supported

This phase does not provide validated CFD, FEA/FEM, rigid-body dynamics, turbulence, advanced thermodynamics, electromagnetics, collision dynamics, real-world measurement acquisition, or experimental validation.

Explicit Euler is timestep-dependent and may be numerically unstable in unsuitable regimes. Simulation output is computational evidence only and remains `SIMULATED`; it is never promoted to `MEASURED` automatically. Required unknown inputs are rejected rather than replaced with defaults.
