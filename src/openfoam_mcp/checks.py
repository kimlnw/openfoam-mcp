"""Logical case-setup validation and optional OpenFOAM CLI wrappers."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from typing import List, Optional

# Utilities we are willing to shell out to (read/setup only, no long solves by default).
ALLOWED_COMMANDS = {
    "blockMesh",
    "checkMesh",
    "foamDictionary",
    "surfaceCheck",
    "transformPoints",
    "renumberMesh",
    "decomposePar",
    "foamListTimes",
}


def _read(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def _application(case_dir: str) -> Optional[str]:
    cd = os.path.join(case_dir, "system", "controlDict")
    if not os.path.isfile(cd):
        return None
    m = re.search(r"^\s*application\s+(\w+)\s*;", _read(cd), re.MULTILINE)
    return m.group(1) if m else None


def _extract_block(text: str, keyword: str) -> Optional[str]:
    """Return the brace-balanced body of ``keyword { ... }`` (inner content)."""
    m = re.search(rf"\b{re.escape(keyword)}\b", text)
    if not m:
        return None
    i = text.find("{", m.end())
    if i == -1:
        return None
    depth = 0
    for j in range(i, len(text)):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                return text[i + 1 : j]
    return None


_MESH_TYPES = r"(?:patch|wall|empty|symmetry\w*|cyclic\w*|wedge|processor|mappedWall)"


def _patches_from_field(field_path: str) -> List[str]:
    body = _extract_block(_read(field_path), "boundaryField")
    if body is None:
        return []
    # Each top-level 'name { ... }' inside boundaryField is a patch entry,
    # whether written inline or multi-line.
    return re.findall(r"([A-Za-z0-9_.\-]+)\s*\{", body)


def _mesh_patches(case_dir: str) -> List[str]:
    # Prefer constant/polyMesh/boundary if meshed, else blockMeshDict boundary.
    boundary = os.path.join(case_dir, "constant", "polyMesh", "boundary")
    if os.path.isfile(boundary):
        text = _read(boundary)
    else:
        bmd = os.path.join(case_dir, "system", "blockMeshDict")
        if not os.path.isfile(bmd):
            return []
        text = _read(bmd)
    # A patch definition is 'name { ... type <boundaryType> ... }' (inline or not).
    return re.findall(rf"([A-Za-z0-9_.\-]+)\s*\{{[^{{}}]*type\s+{_MESH_TYPES}\b", text)


def check_case(case_dir: str) -> dict:
    """Validate an OpenFOAM case directory. Returns errors, warnings and a pass flag."""
    errors: List[str] = []
    warnings: List[str] = []
    info: List[str] = []

    if not os.path.isdir(case_dir):
        return {"passed": False, "errors": [f"Directory not found: {case_dir}"], "warnings": [], "info": []}

    for rel in ("system/controlDict", "system/fvSchemes", "system/fvSolution"):
        if not os.path.isfile(os.path.join(case_dir, rel)):
            errors.append(f"Missing required file: {rel}")

    app = _application(case_dir)
    if app:
        info.append(f"application = {app}")
    else:
        warnings.append("Could not read 'application' from system/controlDict")

    zero = os.path.join(case_dir, "0")
    if not os.path.isdir(zero):
        errors.append("Missing 0/ initial-conditions directory")
        return {"passed": False, "errors": errors, "warnings": warnings, "info": info}

    field_files = {f: os.path.join(zero, f) for f in os.listdir(zero) if os.path.isfile(os.path.join(zero, f))}
    for req in ("U", "p"):
        if req not in field_files:
            errors.append(f"Missing 0/{req} field")

    # Turbulence consistency
    mt = os.path.join(case_dir, "constant", "momentumTransport")
    tt = os.path.join(case_dir, "constant", "turbulenceProperties")
    turb_file = mt if os.path.isfile(mt) else (tt if os.path.isfile(tt) else None)
    if turb_file:
        ttext = _read(turb_file)
        if "RAS" in ttext or "LES" in ttext:
            model_m = re.search(r"model\s+(\w+)", ttext) or re.search(r"RASModel\s+(\w+)", ttext)
            model = model_m.group(1) if model_m else "?"
            info.append(f"turbulence model = {model}")
            needed = []
            if model.lower().startswith("komega") or "SST" in model:
                needed = ["k", "omega", "nut"]
            elif "epsilon" in model.lower() or model.lower().startswith("kepsilon") or "realizable" in model.lower():
                needed = ["k", "epsilon", "nut"]
            elif "spalart" in model.lower():
                needed = ["nut", "nuTilda"]
            for f in needed:
                if f not in field_files:
                    errors.append(f"Turbulence model {model} needs 0/{f} but it is missing")
        else:
            info.append("simulationType = laminar (no turbulence fields required)")
    else:
        warnings.append("No constant/momentumTransport or turbulenceProperties found")

    # Patch consistency between mesh and U field
    mesh_patches = set(_mesh_patches(case_dir))
    if "U" in field_files and mesh_patches:
        u_patches = set(_patches_from_field(field_files["U"]))
        # allow regex/group patches like ".*" to satisfy anything
        wildcard = any(p in (".*", '"(.*)"') or ".*" in p for p in u_patches)
        if not wildcard:
            missing = mesh_patches - u_patches
            extra = u_patches - mesh_patches
            if missing:
                errors.append(f"0/U has no boundaryField entry for mesh patch(es): {', '.join(sorted(missing))}")
            if extra:
                warnings.append(f"0/U defines patch(es) not in the mesh: {', '.join(sorted(extra))}")

    passed = len(errors) == 0
    return {
        "passed": passed,
        "case_dir": case_dir,
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "fields_present": sorted(field_files.keys()),
        "mesh_patches": sorted(mesh_patches),
    }


def openfoam_available() -> bool:
    return shutil.which("blockMesh") is not None or shutil.which("checkMesh") is not None


def run_command(case_dir: str, command: str, timeout: int = 120) -> dict:
    """Run a whitelisted OpenFOAM utility inside ``case_dir``.

    ``command`` is a single utility name optionally followed by flags, e.g.
    "checkMesh -allGeometry". The base utility must be in ALLOWED_COMMANDS.
    """
    if not os.path.isdir(case_dir):
        raise FileNotFoundError(f"Case directory not found: {case_dir}")
    parts = command.split()
    if not parts:
        raise ValueError("Empty command")
    base = parts[0]
    if base not in ALLOWED_COMMANDS:
        raise ValueError(
            f"Command '{base}' is not allowed. Permitted: {', '.join(sorted(ALLOWED_COMMANDS))}"
        )
    if shutil.which(base) is None:
        raise RuntimeError(
            f"'{base}' not found on PATH. OpenFOAM must be installed and its environment "
            "sourced (e.g. `source /opt/openfoam*/etc/bashrc`) for this tool."
        )
    try:
        result = subprocess.run(
            parts, cwd=case_dir, capture_output=True, text=True, timeout=timeout
        )
    except subprocess.TimeoutExpired:
        return {"command": command, "timed_out": True, "timeout_s": timeout}
    tail = "\n".join(result.stdout.strip().splitlines()[-40:])
    return {
        "command": command,
        "return_code": result.returncode,
        "stdout_tail": tail,
        "stderr_tail": "\n".join(result.stderr.strip().splitlines()[-20:]),
    }
