"""Guided setup planner — turn 'what do you want OpenFOAM to do?' into a plan.

Given a plain-language goal plus whatever numbers the user has, this returns a
complete, opinionated setup: solver, turbulence model, target y+, which
blockMesh preset to auto-generate, the 0/ fields needed, per-patch boundary
conditions, and a numbered step list. When a critical input is missing it
returns targeted questions so the assistant can ask the user for just that.
"""

from __future__ import annotations

from typing import Optional

from . import calc

FLUIDS = {
    "air": {"nu": 1.5e-5, "rho": 1.225},
    "water": {"nu": 1.0e-6, "rho": 998.0},
}


def _classify(goal: str) -> str:
    g = goal.lower()
    if any(w in g for w in ["pipe", "duct", "channel", "internal", "manifold"]):
        return "internal"
    if any(w in g for w in ["step", "backward", "reattach", "separation"]):
        return "step"
    if any(w in g for w in ["cavity", "lid-driven", "lid driven"]):
        return "cavity"
    if any(w in g for w in ["plate", "airfoil", "aerofoil", "wing", "car", "external", "aero", "bluff", "cylinder", "building"]):
        return "external"
    return "generic"


def recommend_setup(
    goal: str,
    velocity: Optional[float] = None,
    length: Optional[float] = None,
    fluid: str = "air",
    transient: Optional[bool] = None,
    heat_transfer: bool = False,
) -> dict:
    """Recommend a complete OpenFOAM setup for the user's goal."""
    scenario = _classify(goal)
    fluid_key = fluid.lower() if fluid.lower() in FLUIDS else "air"
    props = FLUIDS[fluid_key]

    missing = []
    questions = []
    if velocity is None:
        missing.append("velocity")
        questions.append("What is the characteristic flow velocity (m/s)?")
    if length is None:
        missing.append("length")
        questions.append(
            "What is the characteristic length (m)? "
            "(pipe/duct: hydraulic diameter; plate/airfoil: chord; bluff body: width)"
        )
    if transient is None:
        questions.append(
            "Do you need time-accurate/transient results (e.g. vortex shedding), "
            "or is a steady-state answer enough?"
        )

    # Reynolds / regime (best-effort if we have the numbers)
    regime_info = None
    reynolds = None
    laminar = False
    if velocity and length:
        geom = "internal" if scenario in ("internal", "cavity") else "external"
        regime_info = calc.flow_regime(velocity, length, props["nu"], geom)
        reynolds = regime_info["reynolds_number"]
        laminar = regime_info["regime"] == "laminar"

    # Decide transient default per scenario if user hasn't said
    want_transient = transient
    if want_transient is None:
        want_transient = scenario == "step"  # separation is inherently unsteady

    # Solver
    if scenario == "cavity" or laminar:
        solver = "icoFoam" if want_transient or scenario == "cavity" else "simpleFoam"
    elif want_transient:
        solver = "pimpleFoam"
    else:
        solver = "simpleFoam"
    if heat_transfer:
        solver_note = (
            "For conjugate/buoyant heat transfer use buoyantSimpleFoam (steady) or "
            "buoyantPimpleFoam (transient) instead; this server scaffolds the "
            "isothermal momentum case as a starting point."
        )
    else:
        solver_note = None

    # Turbulence
    if laminar or scenario == "cavity":
        turbulence_model = "laminar"
        fields = ["U", "p"]
    else:
        turbulence_model = "kOmegaSST"
        fields = ["U", "p", "k", "omega", "nut"]

    # y+ strategy
    y_plus_target = 1.0
    y_plus_note = (
        "Default to wall-resolved y+~1 (best accuracy). If cells get too many, "
        "switch to wall functions and aim y+ 30-300."
    )

    # Mesh preset
    preset = {
        "internal": "channel",
        "external": "flatplate",
        "step": "step",
        "cavity": "box",
        "generic": "channel",
    }[scenario]

    # Boundary conditions (per patch, for the chosen preset)
    bc = {
        "inlet": "U fixedValue (uniform velocity); p zeroGradient; k/omega fixedValue (use inlet_turbulence tool)",
        "outlet": "U zeroGradient (or inletOutlet); p fixedValue 0",
        "walls": "U noSlip; p zeroGradient; k/omega/nut wall functions",
    }
    if preset == "flatplate":
        bc = {
            "inlet": "U fixedValue; p zeroGradient; k/omega fixedValue",
            "outlet": "U zeroGradient; p fixedValue 0",
            "plate": "U noSlip; wall functions on k/omega/nut",
            "top": "U slip or freestream; p zeroGradient",
        }

    # First-cell height (if we can)
    first_cell = None
    if velocity and length:
        fc = calc.first_cell_height(y_plus_target, velocity, length,
                                    props["rho"], props["nu"])
        first_cell = fc["recommended_first_cell_height_m"]

    # Step-by-step plan
    plan = [
        f"1. Auto-generate the mesh: generate_blockmesh(preset='{preset}', "
        f"first_cell_height={first_cell:.3g})" if first_cell else
        f"1. Auto-generate the mesh: generate_blockmesh(preset='{preset}') "
        "(provide velocity & length to auto-size the near-wall cell).",
        f"2. Scaffold the case: scaffold_case(solver='{solver}', velocity=<U>, "
        "openfoam_flavor='classic'|'foundation-v12').",
        "3. Compute inlet turbulence with inlet_turbulence(...) and set k/omega inlet values.",
        "4. Set boundary conditions per patch (set_boundary_condition) per the table above.",
        "5. Run blockMesh, then checkMesh (analyze with mesh_quality_report).",
        f"6. Run {solver}, tee to a log, then analyze_residuals(log) to confirm convergence.",
    ]

    result = {
        "goal": goal,
        "scenario": scenario,
        "assumptions": {
            "fluid": fluid_key,
            "kinematic_viscosity_m2_s": props["nu"],
            "density_kg_m3": props["rho"],
            "transient": want_transient,
            "heat_transfer": heat_transfer,
        },
        "reynolds_number": reynolds,
        "regime": regime_info["regime"] if regime_info else "unknown (need velocity & length)",
        "recommendation": {
            "solver": solver,
            "turbulence_model": turbulence_model,
            "y_plus_target": y_plus_target,
            "y_plus_note": y_plus_note,
            "mesh_preset": preset,
            "fields_needed": fields,
            "recommended_first_cell_height_m": first_cell,
            "boundary_conditions": bc,
            "openfoam_flavor_note": (
                "Use openfoam_flavor='classic' for ESI OpenFOAM or Foundation "
                "v10 and earlier; 'foundation-v12' for Foundation v11/v12 "
                "(foamRun modular solvers). Ask the user which OpenFOAM they run."
            ),
        },
        "plan": plan,
        "missing_inputs": missing,
        "questions_to_ask_user": questions,
    }
    if solver_note:
        result["recommendation"]["solver_note"] = solver_note
    return result
