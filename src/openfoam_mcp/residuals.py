"""Parse OpenFOAM solver logs and diagnose convergence."""

from __future__ import annotations

import math
import os
import re
from typing import Dict, List, Optional

# smoothSolver:  Solving for Ux, Initial residual = 0.01, Final residual = 1e-6, No Iterations 3
_RESIDUAL_RE = re.compile(
    r"Solving for (\w+),\s*Initial residual = ([0-9eE.+\-nafinNAFIN]+),\s*"
    r"Final residual = ([0-9eE.+\-nafinNAFIN]+),\s*No Iterations (\d+)"
)
_TIME_RE = re.compile(r"^Time = ([0-9eE.+\-]+)", re.MULTILINE)
_COURANT_RE = re.compile(r"Courant Number mean: ([0-9eE.+\-]+) max: ([0-9eE.+\-]+)")
_BOUNDING_RE = re.compile(r"bounding (\w+),")


def _to_float(s: str) -> float:
    try:
        return float(s)
    except ValueError:
        return math.nan


def parse_log(text: str) -> dict:
    """Parse a solver log string into per-field residual histories and a
    convergence diagnosis."""
    history: Dict[str, List[float]] = {}
    iterations: Dict[str, List[int]] = {}
    for m in _RESIDUAL_RE.finditer(text):
        field, init, _final, iters = m.group(1), m.group(2), m.group(3), m.group(4)
        history.setdefault(field, []).append(_to_float(init))
        iterations.setdefault(field, []).append(int(iters))

    times = [_to_float(t) for t in _TIME_RE.findall(text)]
    courant = _COURANT_RE.findall(text)
    max_courant = max((_to_float(c[1]) for c in courant), default=None)
    bounded = sorted(set(_BOUNDING_RE.findall(text)))

    fields_summary = {}
    diverged = False
    has_nan = False
    for field, hist in history.items():
        if not hist:
            continue
        first = next((v for v in hist if not math.isnan(v)), math.nan)
        last = hist[-1]
        if math.isnan(last):
            has_nan = True
        if not math.isnan(first) and not math.isnan(last) and first > 0 and last > 10 * first:
            diverged = True
        fields_summary[field] = {
            "first_initial_residual": first,
            "last_initial_residual": last,
            "orders_of_magnitude_dropped": (
                round(math.log10(first / last), 2)
                if (first > 0 and last > 0 and not math.isnan(first) and not math.isnan(last))
                else None
            ),
            "samples": len(hist),
        }

    # Convergence verdict
    converged = (
        bool(fields_summary)
        and not has_nan
        and not diverged
        and all(
            (s["last_initial_residual"] is not None and s["last_initial_residual"] < 1e-3)
            for s in fields_summary.values()
        )
    )
    if has_nan:
        verdict = "DIVERGED — NaN/inf residuals detected. Reduce time step / relaxation, check mesh quality and BCs."
    elif diverged:
        verdict = "DIVERGING — residuals rising >10x. Lower relaxation factors or Courant number, improve mesh orthogonality."
    elif converged:
        verdict = "CONVERGED — all monitored fields below 1e-3."
    elif fields_summary:
        verdict = "RUNNING / NOT YET CONVERGED — residuals still above 1e-3; continue iterating or tighten schemes."
    else:
        verdict = "No residual lines found — is this an OpenFOAM solver log?"

    return {
        "verdict": verdict,
        "converged": converged,
        "steps_or_timesteps": len(times),
        "last_time": times[-1] if times else None,
        "max_courant_number": max_courant,
        "bounded_fields": bounded,
        "fields": fields_summary,
    }


def parse_log_file(path: str) -> dict:
    if not os.path.isfile(path):
        raise FileNotFoundError(f"No such log file: {path}")
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return parse_log(fh.read())
