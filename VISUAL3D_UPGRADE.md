# Tinkle v2.44.0 — Scientific 3D / CAD / Simulation Upgrade

This upgrade adds a real, self-contained procedural 3D layer to the existing Stages 11–12 system.

## Added

- Scientific 3D model catalog: atom, molecule, DNA, cell, heart, solar system, planet, turbine, gearbox, bridge, circuit, robot arm.
- Parametric CAD primitives: box, cylinder, sphere, gear, shaft, beam, bracket fallback, pipe.
- Text-directed 3D scene generation with automatic domain classification.
- Bounded numerical 3D simulations: gravity, projectile motion, spring-mass, orbital motion, heat diffusion field, and flow-field visualization.
- WebGL renderer capable of triangles, lines, and point clouds.
- Interactive rotation and zoom retained in the explanation workspace.
- UI controls for Library / CAD / Physics / Generate.
- API endpoints under `/api/v1/visual3d`.
- Regression tests for catalog, CAD, generator, and all simulation modes.

## Scientific boundary

The models are computational/procedural representations. The system explicitly labels limitations and does not claim experimental evidence, validated CFD/FEA, certified CAD, or measurement-grade anatomical/atomic reconstruction.

## Validation

The complete repository test suite passes after the upgrade.
