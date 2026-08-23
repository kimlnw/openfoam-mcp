"""Read and edit OpenFOAM dictionary files.

Editing prefers the ``foamDictionary`` utility (shipped with OpenFOAM) when it
is available on PATH, because it understands the full dictionary grammar and
macro expansion. When OpenFOAM is not installed it falls back to a conservative
text substitution that handles top-level ``keyword   value;`` entries.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from typing import Optional


def _foam_dictionary_available() -> bool:
    return shutil.which("foamDictionary") is not None


def read_dict(path: str, entry: Optional[str] = None) -> dict:
    """Return the contents of an OpenFOAM dictionary file.

    If ``entry`` is given (e.g. ``application`` or ``solvers/p/solver``) and
    foamDictionary is available, only that entry's value is returned.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"No such file: {path}")

    if entry and _foam_dictionary_available():
        result = subprocess.run(
            ["foamDictionary", "-entry", entry, "-value", path],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return {"path": path, "entry": entry, "value": result.stdout.strip()}
        # fall through to raw read on failure

    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        content = fh.read()
    return {"path": path, "entry": entry, "content": content}


def set_entry(path: str, entry: str, value: str) -> dict:
    """Set ``entry`` to ``value`` in the dictionary at ``path``.

    ``entry`` uses foamDictionary path syntax, e.g. ``endTime`` or
    ``solvers/p/tolerance``. Returns which backend performed the edit.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"No such file: {path}")

    if _foam_dictionary_available():
        result = subprocess.run(
            ["foamDictionary", "-entry", entry, "-set", value, path],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return {"path": path, "entry": entry, "value": value, "backend": "foamDictionary"}
        # else fall back to text edit for simple top-level keys

    if "/" in entry:
        raise RuntimeError(
            "Nested entry edits need the foamDictionary utility (OpenFOAM not "
            f"found on PATH). Could not set '{entry}'."
        )

    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        text = fh.read()

    # Replace a top-level 'keyword   ...;' entry (single line).
    pattern = re.compile(rf"^(\s*{re.escape(entry)}\s+)[^;{{}}]*;", re.MULTILINE)
    new_text, n = pattern.subn(rf"\g<1>{value};", text)
    if n == 0:
        raise RuntimeError(
            f"Keyword '{entry}' not found as a top-level single-line entry in {path}. "
            "Install OpenFOAM for full dictionary editing."
        )
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(new_text)
    return {"path": path, "entry": entry, "value": value, "backend": "text-fallback", "replacements": n}


def set_boundary_condition(
    field_file: str,
    patch: str,
    bc_type: str,
    value: Optional[str] = None,
) -> dict:
    """Set the boundaryField entry for ``patch`` in a 0/ field file.

    Rewrites (or inserts) the whole patch block:

        <patch>
        {
            type            <bc_type>;
            value           uniform <value>;   // only if value given
        }
    """
    if not os.path.isfile(field_file):
        raise FileNotFoundError(f"No such file: {field_file}")
    with open(field_file, "r", encoding="utf-8", errors="replace") as fh:
        text = fh.read()

    block_lines = [f"    {patch}", "    {", f"        type            {bc_type};"]
    if value is not None:
        block_lines.append(f"        value           uniform {value};")
    block_lines.append("    }")
    block = "\n".join(block_lines)

    # Try to replace an existing block for this patch.
    patch_pattern = re.compile(
        rf"^[ \t]*{re.escape(patch)}\s*\n[ \t]*\{{.*?^[ \t]*\}}",
        re.MULTILINE | re.DOTALL,
    )
    if patch_pattern.search(text):
        new_text = patch_pattern.sub(block, text, count=1)
        action = "replaced"
    else:
        # Insert just inside boundaryField { ... }
        bf_pattern = re.compile(r"(boundaryField\s*\n\s*\{)", re.MULTILINE)
        if not bf_pattern.search(text):
            raise RuntimeError(f"No boundaryField block found in {field_file}")
        new_text = bf_pattern.sub(r"\1\n" + block + "\n", text, count=1)
        action = "inserted"

    with open(field_file, "w", encoding="utf-8") as fh:
        fh.write(new_text)
    return {"field_file": field_file, "patch": patch, "type": bc_type, "value": value, "action": action}
