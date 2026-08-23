"""Tests for openfoam-mcp core logic (no OpenFOAM install required)."""

import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from openfoam_mcp import (  # noqa: E402
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


# --------------------------- calculators --------------------------- #
def test_first_cell_height_roundtrip():
    r = calc.first_cell_height(y_plus=1.0, velocity=10.0, length=1.0)
    y = r["first_cell_centroid_distance_m"]
    assert y > 0
    back = calc.y_plus_from_height(y, velocity=10.0, length=1.0)
    assert math.isclose(back["predicted_y_plus"], 1.0, rel_tol=1e-6)


def test_flow_regime_internal_laminar():
    r = calc.flow_regime(velocity=0.01, length=0.01, kinematic_viscosity=1e-6, geometry="internal")
    assert r["regime"] == "laminar"
    assert "laminar" in r["recommended_turbulence_model"]


def test_flow_regime_external_turbulent():
    r = calc.flow_regime(velocity=50.0, length=2.0, geometry="external")
    assert r["regime"] == "turbulent"
    assert r["reynolds_number"] > 1e6


def test_inlet_turbulence_positive():
    r = calc.inlet_turbulence(velocity=10.0, turbulence_intensity=0.05, length_scale=0.014)
    assert r["k_m2_s2"] > 0 and r["omega_1_s"] > 0 and r["epsilon_m2_s3"] > 0


def test_time_step_cfl():
    r = calc.time_step_from_cfl(velocity=10.0, cell_size=0.01, target_courant=1.0)
    assert math.isclose(r["time_step_s"], 0.001, rel_tol=1e-9)


# --------------------------- scaffolding --------------------------- #
def test_scaffold_simplefoam(tmp_path):
    files = scaffold.build_case(solver="simpleFoam", velocity=5.0)
    written = scaffold.write_case(str(tmp_path), files)
    for req in ["system/controlDict", "system/fvSchemes", "0/U", "0/p", "0/k", "0/omega", "0/nut"]:
        assert req in written
        assert os.path.isfile(os.path.join(tmp_path, req))


def test_scaffold_icofoam_is_laminar(tmp_path):
    files = scaffold.build_case(solver="icoFoam")
    scaffold.write_case(str(tmp_path), files)
    assert "0/k" not in files  # laminar has no turbulence fields
    assert "laminar" in files["constant/momentumTransport"]


# --------------------------- dictionary editing --------------------------- #
def test_set_entry_text_fallback(tmp_path):
    p = tmp_path / "controlDict"
    p.write_text("application     simpleFoam;\nendTime         1000;\n")
    dicts.set_entry(str(p), "endTime", "2000")
    assert "endTime         2000;" in p.read_text()


def test_set_boundary_condition_replace(tmp_path):
    p = tmp_path / "U"
    p.write_text(
        "boundaryField\n{\n    inlet\n    {\n        type zeroGradient;\n    }\n}\n"
    )
    r = dicts.set_boundary_condition(str(p), "inlet", "fixedValue", "(10 0 0)")
    assert r["action"] == "replaced"
    txt = p.read_text()
    assert "fixedValue" in txt and "uniform (10 0 0)" in txt


def test_set_boundary_condition_insert(tmp_path):
    p = tmp_path / "U"
    p.write_text("boundaryField\n{\n}\n")
    r = dicts.set_boundary_condition(str(p), "outlet", "zeroGradient")
    assert r["action"] == "inserted"
    assert "outlet" in p.read_text()


# --------------------------- residual parsing --------------------------- #
SAMPLE_LOG = """
Time = 1
smoothSolver:  Solving for Ux, Initial residual = 0.5, Final residual = 1e-3, No Iterations 2
smoothSolver:  Solving for Uy, Initial residual = 0.4, Final residual = 1e-3, No Iterations 2
GAMG:  Solving for p, Initial residual = 0.9, Final residual = 1e-4, No Iterations 10
Courant Number mean: 0.2 max: 0.8
Time = 200
smoothSolver:  Solving for Ux, Initial residual = 1e-5, Final residual = 1e-7, No Iterations 1
smoothSolver:  Solving for Uy, Initial residual = 1e-5, Final residual = 1e-7, No Iterations 1
GAMG:  Solving for p, Initial residual = 5e-5, Final residual = 1e-7, No Iterations 3
"""


def test_parse_log_converged():
    r = residuals.parse_log(SAMPLE_LOG)
    assert r["converged"] is True
    assert "CONVERGED" in r["verdict"]
    assert r["fields"]["Ux"]["orders_of_magnitude_dropped"] > 3


def test_parse_log_diverged_nan():
    log = "Time = 1\nsmoothSolver:  Solving for Ux, Initial residual = nan, Final residual = nan, No Iterations 1\n"
    r = residuals.parse_log(log)
    assert r["converged"] is False
    assert "DIVERGED" in r["verdict"]


def test_parse_log_empty():
    r = residuals.parse_log("hello world")
    assert r["converged"] is False
    assert "No residual lines" in r["verdict"]


# --------------------------- case checking --------------------------- #
def test_check_case_good(tmp_path):
    files = scaffold.build_case(solver="simpleFoam")
    scaffold.write_case(str(tmp_path), files)
    r = checks.check_case(str(tmp_path))
    assert r["passed"] is True, r["errors"]
    assert set(["inlet", "outlet", "walls"]).issubset(set(r["mesh_patches"]))


def test_check_case_missing_turbulence_field(tmp_path):
    files = scaffold.build_case(solver="simpleFoam")
    scaffold.write_case(str(tmp_path), files)
    os.remove(os.path.join(tmp_path, "0", "omega"))
    r = checks.check_case(str(tmp_path))
    assert r["passed"] is False
    assert any("omega" in e for e in r["errors"])


def test_run_command_rejects_unlisted(tmp_path):
    try:
        checks.run_command(str(tmp_path), "rm -rf /")
    except ValueError as e:
        assert "not allowed" in str(e)
    else:
        assert False, "should have rejected"


# --------------------------- new: friction & heat --------------------------- #
def test_pipe_pressure_drop_laminar():
    r = calc.pipe_pressure_drop(velocity=0.1, diameter=0.01, length=1.0)
    assert "laminar" in r["flow_regime"]
    assert math.isclose(r["darcy_friction_factor"], 64.0 / r["reynolds_number"], rel_tol=1e-9)


def test_pipe_pressure_drop_turbulent_colebrook():
    r = calc.pipe_pressure_drop(velocity=3.0, diameter=0.05, length=10.0, roughness=4.5e-5)
    assert "turbulent" in r["flow_regime"]
    # Darcy f for water at Re~1.5e5, mild roughness is ~0.02-0.03
    assert 0.015 < r["darcy_friction_factor"] < 0.035
    assert r["pressure_drop_Pa"] > 0


def test_heat_transfer_dittus_boelter():
    r = calc.heat_transfer_pipe(velocity=2.0, diameter=0.02)
    assert r["reynolds_number"] > 4000
    assert r["convective_heat_transfer_coefficient_W_m2K"] > 0


# --------------------------- new: blockmesh grading --------------------------- #
def test_grading_solver_matches_first_cell():
    info = blockmesh.grading_from_first_cell(length=0.1, n_cells=40, first_cell=1e-4)
    assert info["grading"] > 1.0
    # reconstruct: first cell size should match target within tolerance
    r = info["expansion_ratio"]
    total = 1e-4 * (r**40 - 1) / (r - 1)
    assert math.isclose(total, 0.1, rel_tol=1e-3)


def test_generate_blockmesh_presets():
    for preset in ["channel", "flatplate", "step", "box"]:
        out = blockmesh.generate(preset=preset, first_cell_height=1e-4)
        assert "vertices" in out["blockMeshDict"]
        assert "blocks" in out["blockMeshDict"]
        assert out["meta"]["preset"] == preset


# --------------------------- new: STL geometry --------------------------- #
TETRA_ASCII = """solid tetra
facet normal 0 0 0
 outer loop
  vertex 0 0 0
  vertex 1 0 0
  vertex 0 1 0
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0 0 0
  vertex 0 1 0
  vertex 0 0 1
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 0 0 0
  vertex 0 0 1
  vertex 1 0 0
 endloop
endfacet
facet normal 0 0 0
 outer loop
  vertex 1 0 0
  vertex 0 0 1
  vertex 0 1 0
 endloop
endfacet
endsolid tetra
"""


def test_analyze_stl_watertight(tmp_path):
    p = tmp_path / "tetra.stl"
    p.write_text(TETRA_ASCII)
    r = geometry.analyze_stl(str(p))
    assert r["format"] == "ascii"
    assert r["triangles"] == 4
    assert r["watertight"] is True
    assert r["open_edges"] == 0
    assert r["enclosed_volume_m3"] > 0


def test_analyze_stl_open_surface(tmp_path):
    # Drop the last facet -> open surface
    partial = "\n".join(TETRA_ASCII.splitlines()[:-8]) + "\nendsolid tetra\n"
    p = tmp_path / "open.stl"
    p.write_text(partial)
    r = geometry.analyze_stl(str(p))
    assert r["triangles"] == 3
    assert r["watertight"] is False
    assert r["open_edges"] > 0


# --------------------------- new: checkMesh parsing --------------------------- #
CHECKMESH_OK = """
Mesh stats
    points:           12345
    cells:            10000
Checking geometry...
    Mesh non-orthogonality Max: 42.5 average: 8.1
    Max skewness = 1.8 OK.
    Max aspect ratio = 12.4 OK.
Mesh OK.
"""

CHECKMESH_BAD = """
    Mesh non-orthogonality Max: 78.9 average: 22.1
    Max skewness = 6.1  ***High skewness
Failed 2 mesh checks.
"""


def test_mesh_quality_ok():
    r = meshquality.parse_checkmesh(CHECKMESH_OK)
    assert r["cells"] == 10000
    assert r["max_non_orthogonality_deg"] == 42.5
    assert "OK" in r["verdict"]


def test_mesh_quality_bad():
    r = meshquality.parse_checkmesh(CHECKMESH_BAD)
    assert r["failed_checks"] == 2
    assert r["max_non_orthogonality_deg"] > 70
    assert any("non-orthogonality" in w.lower() for w in r["warnings"])
    assert "FAILED" in r["verdict"]


# --------------------------- new: wizard --------------------------- #
def test_recommend_setup_full():
    r = wizard.recommend_setup("flow through a pipe", velocity=2.0, length=0.05, fluid="water")
    assert r["scenario"] == "internal"
    assert r["recommendation"]["mesh_preset"] == "channel"
    assert r["recommendation"]["recommended_first_cell_height_m"] > 0
    assert r["reynolds_number"] > 0


def test_recommend_setup_missing_inputs_asks():
    r = wizard.recommend_setup("drag on a car")
    assert "velocity" in r["missing_inputs"]
    assert len(r["questions_to_ask_user"]) >= 1
    assert r["scenario"] == "external"


# --------------------------- new: foamRun / v12 flavor --------------------------- #
def test_flavor_classic_default(tmp_path):
    files = scaffold.build_case(solver="simpleFoam", flavor="classic")
    assert "constant/transportProperties" in files
    assert "constant/physicalProperties" not in files
    assert "application     simpleFoam;" in files["system/controlDict"]


def test_flavor_foundation_v12(tmp_path):
    files = scaffold.build_case(solver="simpleFoam", flavor="foundation-v12")
    cd = files["system/controlDict"]
    assert "application     foamRun;" in cd
    assert "solver          incompressibleFluid;" in cd
    assert "constant/physicalProperties" in files
    assert "constant/transportProperties" not in files
    assert "viscosityModel  constant;" in files["constant/physicalProperties"]


def test_flavor_v12_icofoam_uses_pimple_not_piso():
    files = scaffold.build_case(solver="icoFoam", flavor="v12")
    # incompressibleFluid uses PIMPLE even for laminar transient
    assert "PIMPLE" in files["system/fvSolution"]
    assert "PISO" not in files["system/fvSolution"]


def test_flavor_unknown_rejected():
    try:
        scaffold.build_case(solver="simpleFoam", flavor="nope")
    except ValueError as e:
        assert "flavor" in str(e).lower()
    else:
        assert False, "should reject unknown flavor"
