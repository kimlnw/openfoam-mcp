"""Parse an OpenFOAM `checkMesh` log into a plain-English quality verdict.

Works on a pasted/collected log, so it needs no OpenFOAM install at analysis
time. Extracts the numbers that actually predict solver stability and maps them
to concrete fvSchemes/fvSolution advice.
"""

from __future__ import annotations

import os
import re


def _search_float(pattern: str, text: str):
    m = re.search(pattern, text)
    return float(m.group(1)) if m else None


def parse_checkmesh(text: str) -> dict:
    cells = _search_float(r"cells:\s+(\d+)", text)
    max_nonortho = _search_float(r"non-orthogonality Max:\s*([0-9.eE+\-]+)", text)
    avg_nonortho = _search_float(r"non-orthogonality Max:.*average:\s*([0-9.eE+\-]+)", text)
    max_skew = _search_float(r"[Mm]ax skewness\s*=\s*([0-9.eE+\-]+)", text)
    max_ar = _search_float(r"[Mm]ax aspect ratio\s*=\s*([0-9.eE+\-]+)", text)

    mesh_ok = "Mesh OK" in text
    failed_m = re.search(r"Failed (\d+) mesh checks", text)
    failed_checks = int(failed_m.group(1)) if failed_m else (0 if mesh_ok else None)

    warnings = []
    advice = []

    if max_nonortho is not None:
        if max_nonortho > 70:
            warnings.append(f"High max non-orthogonality ({max_nonortho:.1f}° > 70°)")
            advice.append(
                "Set nNonOrthogonalCorrectors to 1-2 in fvSolution and use "
                "'Gauss linear corrected' laplacianSchemes; consider improving the mesh."
            )
        elif max_nonortho > 60:
            advice.append("Non-orthogonality 60-70°: use at least 1 nNonOrthogonalCorrector.")

    if max_skew is not None and max_skew > 4:
        warnings.append(f"High max skewness ({max_skew:.2f} > 4)")
        advice.append("Skewness > 4 hurts accuracy/stability — refine or smooth those cells.")

    if max_ar is not None and max_ar > 100:
        warnings.append(f"Very high aspect ratio ({max_ar:.0f})")
        advice.append(
            "Extreme aspect ratios slow convergence; expected in boundary layers "
            "but keep bulk cells reasonable."
        )

    if failed_checks:
        verdict = f"FAILED {failed_checks} mesh check(s) — fix before solving."
    elif mesh_ok and not warnings:
        verdict = "Mesh OK — good quality, safe to solve."
    elif mesh_ok and warnings:
        verdict = "Mesh OK but with quality flags — solvable with the scheme tweaks below."
    else:
        verdict = "Could not find a clear verdict — is this a checkMesh log?"

    return {
        "verdict": verdict,
        "cells": int(cells) if cells else None,
        "max_non_orthogonality_deg": max_nonortho,
        "avg_non_orthogonality_deg": avg_nonortho,
        "max_skewness": max_skew,
        "max_aspect_ratio": max_ar,
        "failed_checks": failed_checks,
        "warnings": warnings,
        "advice": advice,
    }


def parse_checkmesh_file(path: str) -> dict:
    if not os.path.isfile(path):
        raise FileNotFoundError(f"No such file: {path}")
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return parse_checkmesh(fh.read())
