"""OpenFOAM / CFD co-pilot — MCP server entry point.

Exposes CFD setup and diagnosis tools over the Model Context Protocol so any
MCP client (Claude Desktop, etc.) can scaffold OpenFOAM cases, edit
dictionaries, size boundary-layer meshes, and interpret solver residuals.

Run with:  ``openfoam-mcp``  (stdio transport)
"""

from __future__ import annotations

import os
from typing import Optional

from mcp.server.fastmcp import FastMCP

from . import (
    __version__,
    blockmesh,
    calc,
    checks,
    dicts,
    geometry,
    meshquality,
    residuals,
    scaffold,
    wizard,
)

mcp = FastMCP("openfoam-mcp")


# --------------------------------------------------------------------------- #
# Reference
# --------------------------------------------------------------------------- #
@mcp.tool()
def list_solvers() -> dict:
    """List the OpenFOAM solver templates this server can scaffold, with a
    one-line description of each and when to use it."""
    return {"version": __version__, "solvers": scaffold.SUPPORTED}


# --------------------------------------------------------------------------- #
# CFD calculators (no OpenFOAM install required)
# --------------------------------------------------------------------------- #
@mcp.tool()
def first_cell_height(
    y_plus: float,
    velocity: float,
    length: float,
    density: float = 1.225,
    kinematic_viscosity: float = 1.5e-5,
) -> dict:
    """Estimate the wall-normal first-cell height needed to hit a target y+ on a
    turbulent boundary layer (flat-plate correlation). Use before meshing to set
    the near-wall cell size. Defaults are for air at sea level."""
    return calc.first_cell_height(y_plus, velocity, length, density, kinematic_viscosity)


@mcp.tool()
def y_plus_from_height(
    first_cell_height_m: float,
    velocity: float,
    length: float,
    density: float = 1.225,
    kinematic_viscosity: float = 1.5e-5,
) -> dict:
    """Predict the y+ that a given first-cell height will produce, and whether it
    lands in the viscous sublayer, buffer layer (avoid), or log-law region."""
    return calc.y_plus_from_height(first_cell_height_m, velocity, length, density, kinematic_viscosity)


@mcp.tool()
def flow_regime(
    velocity: float,
    length: float,
    kinematic_viscosity: float = 1.5e-5,
    geometry: str = "external",
) -> dict:
    """Reynolds number, laminar/transitional/turbulent classification, and a
    turbulence-model recommendation. `geometry` = 'internal' (pipe/duct) or
    'external' (plate/bluff body/airfoil)."""
    return calc.flow_regime(velocity, length, kinematic_viscosity, geometry)


@mcp.tool()
def inlet_turbulence(
    velocity: float,
    turbulence_intensity: float,
    length_scale: float,
    kinematic_viscosity: float = 1.5e-5,
) -> dict:
    """Compute inlet k, epsilon, omega and nut from turbulence intensity
    (fraction, e.g. 0.05) and turbulent length scale (m). Use to fill the 0/
    directory inlet/internalField values for a RANS case."""
    return calc.inlet_turbulence(velocity, turbulence_intensity, length_scale, kinematic_viscosity)


@mcp.tool()
def time_step_from_cfl(velocity: float, cell_size: float, target_courant: float = 1.0) -> dict:
    """Maximum/target transient time step from a target Courant number
    (dt = Co * dx / U)."""
    return calc.time_step_from_cfl(velocity, cell_size, target_courant)


# --------------------------------------------------------------------------- #
# Case scaffolding
# --------------------------------------------------------------------------- #
@mcp.tool()
def scaffold_case(
    case_dir: str,
    solver: str = "simpleFoam",
    velocity: float = 10.0,
    kinematic_viscosity: float = 1.5e-5,
    domain_x: float = 1.0,
    domain_y: float = 0.2,
    domain_z: float = 0.1,
    cells_x: int = 40,
    cells_y: int = 20,
    cells_z: int = 1,
    end_time: float = 1000.0,
    openfoam_flavor: str = "classic",
) -> dict:
    """Create a runnable OpenFOAM case skeleton at ``case_dir`` for the chosen
    solver (simpleFoam / pimpleFoam / icoFoam). Writes system/, constant/ and 0/
    with a single-block box mesh (patches: inlet, outlet, walls, frontAndBack)
    and consistent turbulence fields.

    openfoam_flavor selects the case style:
      - 'classic' (default): application <solver>; + transportProperties.
        Validated on ESI v1912; works on ESI v2006+ and Foundation v8-v10.
      - 'foundation-v12': application foamRun; solver incompressibleFluid; +
        physicalProperties. Targets OpenFOAM Foundation v11/v12.
    Run blockMesh, then `<solver>` (classic) or `foamRun` (foundation-v12)."""
    files = scaffold.build_case(
        solver=solver,
        velocity=velocity,
        nu=kinematic_viscosity,
        domain=(domain_x, domain_y, domain_z),
        cells=(cells_x, cells_y, cells_z),
        end_time=end_time,
        flavor=openfoam_flavor,
    )
    written = scaffold.write_case(case_dir, files)
    is_v12 = openfoam_flavor.lower() in ("v12", "foundation", "foamrun", "foundation-v11", "foundation-v12")
    run_cmd = "foamRun" if is_v12 else solver
    return {
        "case_dir": os.path.abspath(case_dir),
        "solver": solver,
        "openfoam_flavor": "foundation-v12" if is_v12 else "classic",
        "files_written": written,
        "next_steps": ["cd " + case_dir, "blockMesh", run_cmd + " | tee log." + run_cmd],
    }


# --------------------------------------------------------------------------- #
# Dictionary editing
# --------------------------------------------------------------------------- #
@mcp.tool()
def read_dict(path: str, entry: Optional[str] = None) -> dict:
    """Read an OpenFOAM dictionary file. If `entry` is given (foamDictionary
    path syntax, e.g. 'endTime' or 'solvers/p/solver') and OpenFOAM is
    installed, return just that entry's value; otherwise return full contents."""
    return dicts.read_dict(path, entry)


@mcp.tool()
def set_dict_entry(path: str, entry: str, value: str) -> dict:
    """Set a keyword in a dictionary file. Uses foamDictionary when available
    (supports nested entries like 'solvers/p/tolerance'); otherwise falls back
    to editing a top-level single-line entry as text."""
    return dicts.set_entry(path, entry, value)


@mcp.tool()
def set_boundary_condition(field_file: str, patch: str, bc_type: str, value: Optional[str] = None) -> dict:
    """Set (or insert) the boundaryField entry for a patch in a 0/ field file,
    e.g. field_file='0/U', patch='inlet', bc_type='fixedValue', value='(10 0 0)'."""
    return dicts.set_boundary_condition(field_file, patch, bc_type, value)


# --------------------------------------------------------------------------- #
# Validation and diagnosis
# --------------------------------------------------------------------------- #
@mcp.tool()
def check_case(case_dir: str) -> dict:
    """Logically validate a case directory: required system files present,
    solver read, turbulence fields consistent with the model, and 0/ boundary
    patches matching the mesh. Returns errors, warnings and a pass flag. Does
    not require OpenFOAM to be installed."""
    return checks.check_case(case_dir)


@mcp.tool()
def analyze_residuals(log_path: str) -> dict:
    """Parse an OpenFOAM solver log file and report per-field residual drop,
    Courant number, bounded fields, and a convergence verdict (converged /
    diverging / NaN / still running)."""
    return residuals.parse_log_file(log_path)


@mcp.tool()
def run_openfoam_command(case_dir: str, command: str, timeout: int = 120) -> dict:
    """Run a whitelisted OpenFOAM utility (blockMesh, checkMesh, foamDictionary,
    renumberMesh, decomposePar, foamListTimes, surfaceCheck, transformPoints)
    inside a case directory. Requires OpenFOAM installed and its environment
    sourced. Returns return code and the tail of stdout/stderr."""
    return checks.run_command(case_dir, command, timeout)


# --------------------------------------------------------------------------- #
# Guided planner — "what do you want OpenFOAM to do?"
# --------------------------------------------------------------------------- #
@mcp.tool()
def recommend_setup(
    goal: str,
    velocity: Optional[float] = None,
    length: Optional[float] = None,
    fluid: str = "air",
    transient: Optional[bool] = None,
    heat_transfer: bool = False,
) -> dict:
    """Turn a plain-language goal (e.g. 'flow through a pipe', 'drag on a car')
    into a complete setup plan: recommended solver, turbulence model, target y+,
    which blockMesh preset to auto-generate, the 0/ fields needed, per-patch
    boundary conditions, and a numbered step list. If velocity/length are
    missing it returns targeted questions to ask the user first. Start here."""
    return wizard.recommend_setup(goal, velocity, length, fluid, transient, heat_transfer)


# --------------------------------------------------------------------------- #
# Auto blockMesh — no hand-writing vertices/blocks
# --------------------------------------------------------------------------- #
@mcp.tool()
def list_mesh_presets() -> dict:
    """List the auto-blockMesh geometry presets (channel, flatplate, step, box)."""
    return {"presets": blockmesh.PRESETS}


@mcp.tool()
def generate_blockmesh(
    output_path: str,
    preset: str = "channel",
    length: float = 1.0,
    height: float = 0.2,
    depth: float = 0.05,
    cells_x: int = 60,
    cells_y: int = 40,
    cells_z: int = 1,
    first_cell_height: float = 0.0,
) -> dict:
    """Auto-generate a valid, boundary-layer-graded blockMeshDict and write it to
    output_path (typically '<case>/system/blockMeshDict'). Pick a preset
    (channel, flatplate, step, box). If first_cell_height > 0, wall-normal
    grading is computed automatically so the near-wall cell matches that height
    (feed it the value from the first_cell_height tool to hit a target y+). This
    removes the hardest, most error-prone part of setting up a case."""
    out = blockmesh.generate(
        preset=preset,
        length=length,
        height=height,
        depth=depth,
        cells_x=cells_x,
        cells_y=cells_y,
        cells_z=cells_z,
        first_cell_height=first_cell_height,
    )
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write(out["blockMeshDict"])
    return {"written": os.path.abspath(output_path), "meta": out["meta"],
            "next_step": "Run blockMesh in the case directory, then checkMesh."}


# --------------------------------------------------------------------------- #
# Geometry & mesh quality
# --------------------------------------------------------------------------- #
@mcp.tool()
def analyze_stl(path: str) -> dict:
    """Analyze an STL surface (ASCII or binary): triangle count, bounding box,
    surface area, enclosed volume, and a watertight/closed-manifold check with
    the count of unpaired edges — plus a suggested background cell size and
    snappyHexMesh advice. No OpenFOAM needed. Use before snappyHexMesh."""
    return geometry.analyze_stl(path)


@mcp.tool()
def mesh_quality_report(log_path: str) -> dict:
    """Parse a checkMesh log file into a quality verdict: max/avg
    non-orthogonality, skewness, aspect ratio, pass/fail, and concrete
    fvSchemes/fvSolution advice (e.g. nNonOrthogonalCorrectors). Works from a
    saved log without OpenFOAM installed."""
    return meshquality.parse_checkmesh_file(log_path)


# --------------------------------------------------------------------------- #
# Internal-flow engineering calculators
# --------------------------------------------------------------------------- #
@mcp.tool()
def pipe_pressure_drop(
    velocity: float,
    diameter: float,
    length: float,
    density: float = 998.0,
    kinematic_viscosity: float = 1.0e-6,
    roughness: float = 0.0,
) -> dict:
    """Darcy friction factor (Colebrook-White for turbulent, 64/Re laminar) and
    Darcy-Weisbach pressure drop / head loss for pipe flow. Defaults are for
    water; set roughness (m) for rough pipes. Handy sanity check against CFD."""
    return calc.pipe_pressure_drop(velocity, diameter, length, density, kinematic_viscosity, roughness)


@mcp.tool()
def heat_transfer_pipe(
    velocity: float,
    diameter: float,
    density: float = 998.0,
    kinematic_viscosity: float = 1.0e-6,
    prandtl: float = 7.0,
    conductivity: float = 0.6,
    heating: bool = True,
) -> dict:
    """Convective heat-transfer coefficient for internal flow (Dittus-Boelter
    Nu = 0.023 Re^0.8 Pr^n; laminar Nu = 3.66). Defaults are for water.
    Returns Nusselt number and h (W/m^2K)."""
    return calc.heat_transfer_pipe(velocity, diameter, density, kinematic_viscosity, prandtl, conductivity, heating)


def main() -> None:
    """Console-script entry point (stdio transport)."""
    mcp.run()


if __name__ == "__main__":
    main()
