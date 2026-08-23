"""Pure-Python CFD engineering calculators.

None of these require an OpenFOAM installation. They implement standard,
citable correlations used when setting up a CFD case: boundary-layer meshing
(y+ / first-cell height), flow regime, inlet turbulence quantities, and a
CFL-based time-step estimate.
"""

from __future__ import annotations

import math
from typing import Optional

C_MU = 0.09  # standard k-epsilon / k-omega model constant


# --------------------------------------------------------------------------- #
# Boundary-layer meshing: first-cell height from a target y+
# --------------------------------------------------------------------------- #
def first_cell_height(
    y_plus: float,
    velocity: float,
    length: float,
    density: float = 1.225,
    kinematic_viscosity: float = 1.5e-5,
) -> dict:
    """Estimate the wall-normal distance of the first cell centroid for a
    target y+ on a turbulent flat-plate boundary layer.

    Uses the standard flat-plate skin-friction correlation
        Cf = 0.026 / Re_x**(1/7)
    then tau_w = 0.5 * Cf * rho * U**2, u_tau = sqrt(tau_w / rho),
    and y = y_plus * nu / u_tau.

    Returns wall distance to the first cell *centroid* and the recommended
    first-cell *height* (~2x the centroid distance for a wall-adjacent cell).
    """
    if velocity <= 0 or length <= 0:
        raise ValueError("velocity and length must be positive")
    nu = kinematic_viscosity
    re_x = velocity * length / nu
    cf = 0.026 / re_x ** (1.0 / 7.0)
    tau_w = 0.5 * cf * density * velocity**2
    u_tau = math.sqrt(tau_w / density)
    y_centroid = y_plus * nu / u_tau
    return {
        "reynolds_number": re_x,
        "skin_friction_coefficient_Cf": cf,
        "wall_shear_stress_Pa": tau_w,
        "friction_velocity_m_s": u_tau,
        "first_cell_centroid_distance_m": y_centroid,
        "recommended_first_cell_height_m": 2.0 * y_centroid,
        "target_y_plus": y_plus,
        "notes": (
            "Flat-plate correlation Cf = 0.026/Re^(1/7). For wall-resolved "
            "(low-Re) modelling aim y+ ~ 1; for wall functions aim y+ 30-300. "
            "First-cell height is ~2x the centroid distance in a cell-centred "
            "FV code such as OpenFOAM."
        ),
    }


def y_plus_from_height(
    first_cell_height_m: float,
    velocity: float,
    length: float,
    density: float = 1.225,
    kinematic_viscosity: float = 1.5e-5,
) -> dict:
    """Inverse of :func:`first_cell_height`: predict the y+ that results from a
    given first-cell centroid distance."""
    if velocity <= 0 or length <= 0 or first_cell_height_m <= 0:
        raise ValueError("inputs must be positive")
    nu = kinematic_viscosity
    re_x = velocity * length / nu
    cf = 0.026 / re_x ** (1.0 / 7.0)
    tau_w = 0.5 * cf * density * velocity**2
    u_tau = math.sqrt(tau_w / density)
    y_plus = first_cell_height_m * u_tau / nu
    if y_plus < 5:
        regime = "viscous sublayer (wall-resolved; y+ ~ 1 ideal)"
    elif y_plus < 30:
        regime = "buffer layer — AVOID: neither wall-resolved nor wall-function valid"
    elif y_plus <= 300:
        regime = "log-law region (wall-function valid)"
    else:
        regime = "y+ too high — first cell outside the log-law region"
    return {
        "reynolds_number": re_x,
        "friction_velocity_m_s": u_tau,
        "predicted_y_plus": y_plus,
        "regime": regime,
    }


# --------------------------------------------------------------------------- #
# Flow regime and turbulence-model recommendation
# --------------------------------------------------------------------------- #
def flow_regime(
    velocity: float,
    length: float,
    kinematic_viscosity: float = 1.5e-5,
    geometry: str = "external",
) -> dict:
    """Reynolds number, laminar/turbulent classification, and a turbulence
    model recommendation. `geometry` is 'internal' (pipe/duct) or 'external'
    (flat plate / bluff body / airfoil)."""
    if velocity <= 0 or length <= 0:
        raise ValueError("velocity and length must be positive")
    re = velocity * length / kinematic_viscosity
    geometry = geometry.lower()
    if geometry.startswith("int"):
        if re < 2300:
            regime = "laminar"
        elif re < 4000:
            regime = "transitional"
        else:
            regime = "turbulent"
        crit = "internal (pipe): laminar < 2300, transitional 2300-4000, turbulent > 4000"
    else:
        if re < 5e5:
            regime = "laminar"
        elif re < 1e6:
            regime = "transitional"
        else:
            regime = "turbulent"
        crit = "external (flat plate): transition near Re_x ~ 5e5"

    if regime == "laminar":
        model = "laminar (no turbulence model needed)"
    elif geometry.startswith("int"):
        model = "k-omega SST (general) or realizable k-epsilon for fully-developed internal flow"
    else:
        model = "k-omega SST (general external) or Spalart-Allmaras for attached aerodynamic flows"

    return {
        "reynolds_number": re,
        "regime": regime,
        "criterion": crit,
        "recommended_turbulence_model": model,
    }


# --------------------------------------------------------------------------- #
# Inlet turbulence quantities from intensity and length scale
# --------------------------------------------------------------------------- #
def inlet_turbulence(
    velocity: float,
    turbulence_intensity: float,
    length_scale: float,
    kinematic_viscosity: float = 1.5e-5,
) -> dict:
    """Compute inlet k, epsilon, omega and nut from turbulence intensity I
    (fraction, e.g. 0.05 for 5%) and turbulent length scale l (m).

        k       = 1.5 * (U*I)^2
        epsilon = C_mu^0.75 * k^1.5 / l
        omega   = k^0.5 / (C_mu^0.25 * l)
        nut     = C_mu * k^2 / epsilon
    """
    if velocity <= 0 or turbulence_intensity <= 0 or length_scale <= 0:
        raise ValueError("inputs must be positive")
    k = 1.5 * (velocity * turbulence_intensity) ** 2
    epsilon = C_MU**0.75 * k**1.5 / length_scale
    omega = k**0.5 / (C_MU**0.25 * length_scale)
    nut = C_MU * k**2 / epsilon
    return {
        "k_m2_s2": k,
        "epsilon_m2_s3": epsilon,
        "omega_1_s": omega,
        "nut_m2_s": nut,
        "turbulent_viscosity_ratio_nut_nu": nut / kinematic_viscosity,
        "notes": (
            "Set these as internalField/inlet values for k, epsilon, omega "
            "and nut in the 0/ directory. A common length scale is 0.07*L "
            "for internal flows (L = hydraulic diameter)."
        ),
    }


# --------------------------------------------------------------------------- #
# CFL-based time step
# --------------------------------------------------------------------------- #
def pipe_pressure_drop(
    velocity: float,
    diameter: float,
    length: float,
    density: float = 998.0,
    kinematic_viscosity: float = 1.0e-6,
    roughness: float = 0.0,
) -> dict:
    """Darcy friction factor and pressure drop for internal pipe flow.

    Laminar (Re<2300): f = 64/Re.
    Turbulent: Colebrook-White solved iteratively for the Darcy friction factor,
    then Darcy-Weisbach dp = f (L/D) (rho U^2 / 2). Defaults are for water.
    """
    if velocity <= 0 or diameter <= 0 or length <= 0:
        raise ValueError("velocity, diameter and length must be positive")
    re = velocity * diameter / kinematic_viscosity
    if re < 2300:
        f = 64.0 / re
        regime = "laminar (f = 64/Re)"
    else:
        # Colebrook-White: 1/sqrt(f) = -2 log10( eps/(3.7 D) + 2.51/(Re sqrt(f)) )
        rel = roughness / diameter
        f = 0.02
        for _ in range(100):
            rhs = -2.0 * math.log10(rel / 3.7 + 2.51 / (re * math.sqrt(f)))
            f_new = 1.0 / rhs**2
            if abs(f_new - f) < 1e-10:
                f = f_new
                break
            f = f_new
        regime = "turbulent (Colebrook-White)"
    dp = f * (length / diameter) * 0.5 * density * velocity**2
    return {
        "reynolds_number": re,
        "flow_regime": regime,
        "darcy_friction_factor": f,
        "pressure_drop_Pa": dp,
        "head_loss_m": dp / (density * 9.81),
        "wall_shear_stress_Pa": f / 8.0 * density * velocity**2,
    }


def heat_transfer_pipe(
    velocity: float,
    diameter: float,
    density: float = 998.0,
    kinematic_viscosity: float = 1.0e-6,
    prandtl: float = 7.0,
    conductivity: float = 0.6,
    heating: bool = True,
) -> dict:
    """Convective heat transfer for fully-developed turbulent internal flow via
    the Dittus-Boelter correlation Nu = 0.023 Re^0.8 Pr^n (n=0.4 heating,
    0.3 cooling). Defaults are for water; conductivity in W/m-K.
    """
    if velocity <= 0 or diameter <= 0:
        raise ValueError("velocity and diameter must be positive")
    re = velocity * diameter / kinematic_viscosity
    n = 0.4 if heating else 0.3
    if re < 4000:
        nu = 3.66  # laminar, constant wall temperature
        method = "laminar, Nu = 3.66 (constant wall temp)"
    else:
        nu = 0.023 * re**0.8 * prandtl**n
        method = f"Dittus-Boelter, Nu = 0.023 Re^0.8 Pr^{n}"
    h = nu * conductivity / diameter
    return {
        "reynolds_number": re,
        "prandtl_number": prandtl,
        "nusselt_number": nu,
        "method": method,
        "convective_heat_transfer_coefficient_W_m2K": h,
    }


def time_step_from_cfl(
    velocity: float,
    cell_size: float,
    target_courant: float = 1.0,
) -> dict:
    """Maximum stable/target time step from the Courant number
        Co = U * dt / dx   ->   dt = Co * dx / U
    """
    if velocity <= 0 or cell_size <= 0 or target_courant <= 0:
        raise ValueError("inputs must be positive")
    dt = target_courant * cell_size / velocity
    return {
        "time_step_s": dt,
        "target_courant_number": target_courant,
        "notes": (
            "For PIMPLE transient runs a mean Courant number ~1 (max <5) is "
            "typical. Explicit solvers (interFoam without adjustable dt) need "
            "Co < 1 everywhere. Enable adjustTimeStep in controlDict to let "
            "OpenFOAM hold maxCo automatically."
        ),
    }
