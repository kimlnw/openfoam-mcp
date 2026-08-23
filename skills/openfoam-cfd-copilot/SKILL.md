---
name: openfoam-cfd-copilot
description: >-
  Set up, mesh, run, and debug OpenFOAM CFD simulations. Use whenever the user
  is working with OpenFOAM or CFD — sizing a near-wall mesh (y+, first-cell
  height, wall grading), choosing a solver or turbulence model, writing or
  editing case dictionaries (controlDict, fvSchemes, fvSolution, blockMeshDict,
  0/ fields), setting boundary conditions, checking mesh quality, sizing pipe
  pressure drop or convective heat transfer, or interpreting solver residuals
  and convergence. Works standalone with the reference formulas below, and uses
  the `openfoam-mcp` MCP server's tools when it is connected.
license: MIT
metadata:
  author: iLab (Tanawat Manokieng)
  version: 1.0.0
---

# OpenFOAM CFD Co-Pilot (by iLab)

This skill turns a plain-language CFD goal into a correct OpenFOAM case and helps
diagnose it — doing the tedious, error-prone bookkeeping (y+, patch matching,
turbulence fields, residual reading) so the user focuses on the physics.

If the **`openfoam-mcp`** MCP server is connected, prefer its tools (they read and
write real case files). If it is not, apply the reference formulas and templates
in this document by hand.

## Workflow

Follow these steps in order. Ask the user only for what you still need
(characteristic velocity, characteristic length, fluid, steady vs transient,
heat transfer yes/no, and which OpenFOAM version they run).

1. **Classify the problem and pick the setup.**
   - Internal (pipe/duct/channel), external (plate/airfoil/bluff body),
     backward-facing step, or lid-driven cavity.
   - Compute the Reynolds number and decide laminar vs turbulent.
   - Choose the solver and turbulence model (rules below).
   - *MCP:* `recommend_setup(goal, velocity, length, fluid, transient, heat_transfer)`.

2. **Size the near-wall mesh.**
   - Pick a wall-treatment strategy: wall-resolved (y+ ≈ 1) or wall functions
     (y+ 30–300). Avoid the buffer layer (5 < y+ < 30).
   - Compute the first-cell height for the target y+.
   - *MCP:* `first_cell_height(y_plus, velocity, length)` /
     `y_plus_from_height(...)`.

3. **Generate the mesh.**
   - Build a graded `blockMeshDict` from a geometry preset; grade the wall-normal
     direction to hit the first-cell height from step 2.
   - *MCP:* `generate_blockmesh(output_path, preset, first_cell_height=…)`.
   - For an imported geometry, check the STL is watertight before snappyHexMesh.
     *MCP:* `analyze_stl(path)`.

4. **Scaffold the case and set inlet turbulence.**
   - Write `system/`, `constant/`, `0/`.
   - Compute inlet k, ε, ω, νt from turbulence intensity (~5% internal) and a
     length scale (~0.07 × hydraulic diameter).
   - *MCP:* `scaffold_case(case_dir, solver, velocity, openfoam_flavor)` +
     `inlet_turbulence(velocity, intensity, length_scale)`.

5. **Set boundary conditions per patch** (table below).
   - *MCP:* `set_boundary_condition(field_file, patch, bc_type, value)` and
     `set_dict_entry(path, entry, value)`.

6. **Run and validate.**
   - Order: `blockMesh` → `checkMesh` → solver (tee to a log).
   - Confirm mesh quality, then confirm convergence.
   - *MCP:* `run_openfoam_command(case_dir, "checkMesh")`,
     `mesh_quality_report(log)`, `analyze_residuals(log)`.

## Decision rules

**Laminar vs turbulent** — internal: laminar Re < 2300, turbulent Re > 4000.
External: transition near Re_x ≈ 5×10⁵.

**Solver:**
- Steady incompressible → `simpleFoam`.
- Transient incompressible (vortex shedding, unsteady) → `pimpleFoam`.
- Transient laminar teaching case (cavity, low-Re) → `icoFoam`.
- Conjugate/buoyant heat transfer → `buoyantSimpleFoam` / `buoyantPimpleFoam`
  (scaffold the isothermal momentum case as a starting point).

**Turbulence model:** k-ω SST is the safe general default (internal and external).
Spalart-Allmaras for attached external aerodynamics; realizable k-ε for
fully-developed high-Re internal flow. Laminar → no model.

## Boundary conditions (incompressible, per patch)

| Patch | U | p | k / ω / nut |
|-------|---|---|-------------|
| inlet | fixedValue (uniform velocity) | zeroGradient | fixedValue (from `inlet_turbulence`) |
| outlet | zeroGradient (or inletOutlet) | fixedValue 0 | zeroGradient |
| wall | noSlip | zeroGradient | wall functions (kqRWallFunction / omegaWallFunction / nutkWallFunction) |
| symmetry / empty (2D) | symmetry / empty | symmetry / empty | symmetry / empty |

## Reference formulas (use when the MCP server is not connected)

- **Reynolds:** Re = U·L / ν  (air ν ≈ 1.5×10⁻⁵ m²/s; water ν ≈ 1.0×10⁻⁶ m²/s).
- **First-cell height for target y+** (turbulent flat plate):
  Cf = 0.026 / Re_x^(1/7);  τ_w = ½ Cf ρ U²;  u_τ = √(τ_w/ρ);
  y = y⁺ ν / u_τ.  First-cell height ≈ 2·y (cell-centred FV).
- **Inlet turbulence** from intensity I and length scale l:
  k = 1.5 (U·I)²;  ε = C_μ^0.75 k^1.5 / l;  ω = k^0.5 / (C_μ^0.25 l);
  ν_t = C_μ k² / ε   (C_μ = 0.09).
- **Time step from Courant number:** dt = Co · dx / U  (aim mean Co ≈ 1 for PIMPLE).
- **Pipe pressure drop:** laminar f = 64/Re; turbulent f from Colebrook–White;
  Δp = f (L/D) ½ρU²  (Darcy–Weisbach).
- **Convective heat transfer (turbulent internal):** Nu = 0.023 Re^0.8 Pr^n
  (n = 0.4 heating, 0.3 cooling); h = Nu·k/D  (laminar Nu = 3.66).

## OpenFOAM version notes

- **Classic** (ESI OpenFOAM, or Foundation v10 and earlier): run the solver by
  name (`simpleFoam`), viscosity in `constant/transportProperties`.
  → `scaffold_case(..., openfoam_flavor="classic")`.
- **Foundation v11/v12** (modular solvers): run `foamRun`, with
  `solver incompressibleFluid;` in `controlDict` and viscosity in
  `constant/physicalProperties`.
  → `scaffold_case(..., openfoam_flavor="foundation-v12")`.
- For maximum compatibility a scaffolded case emits **both**
  `constant/turbulenceProperties` (old) and `constant/momentumTransport` (new).

## Common failures and fixes

- **`cannot find file ".../constant/turbulenceProperties"`** — old OpenFOAM wants
  `turbulenceProperties` (`RASModel …`); new wants `momentumTransport` (`model …`).
  Emit both.
- **`Entry 'method' not found in ".../fvSchemes.wallDist"`** — k-ω SST needs
  `wallDist { method meshWave; }` in `system/fvSchemes`.
- **`Entry 'PISO'/'UFinal'/'pFinal' not found in fvSolution`** — transient runs
  need the right algorithm block (`PISO` for icoFoam, `PIMPLE` for pimpleFoam)
  and `*Final` corrector solver entries.
- **Diverging / NaN residuals** — lower relaxation factors or Courant number,
  improve mesh non-orthogonality/skewness, and verify boundary conditions.

## Companion MCP server

The full tool set lives in the **`openfoam-mcp`** server (install:
`uvx openfoam-mcp`). Tools: `recommend_setup`, `generate_blockmesh`,
`list_mesh_presets`, `list_solvers`, `flow_regime`, `first_cell_height`,
`y_plus_from_height`, `inlet_turbulence`, `time_step_from_cfl`,
`pipe_pressure_drop`, `heat_transfer_pipe`, `scaffold_case`, `read_dict`,
`set_dict_entry`, `set_boundary_condition`, `analyze_stl`, `mesh_quality_report`,
`check_case`, `analyze_residuals`, `run_openfoam_command`.
