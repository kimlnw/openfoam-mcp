"""Pure-Python STL geometry analysis for snappyHexMesh preparation.

No OpenFOAM, numpy, or trimesh required. Handles both ASCII and binary STL.
Reports triangle count, bounding box, surface area, a watertight/closed-manifold
check (via edge pairing), signed volume, and a suggested background mesh.
"""

from __future__ import annotations

import math
import os
import struct
from typing import List, Tuple

Vec = Tuple[float, float, float]


def _is_binary_stl(path: str) -> bool:
    size = os.path.getsize(path)
    with open(path, "rb") as fh:
        header = fh.read(80)
        if len(header) < 80:
            return False
        count_bytes = fh.read(4)
        if len(count_bytes) < 4:
            return False
        n = struct.unpack("<I", count_bytes)[0]
    # Binary STL size is exactly 84 + 50*n.
    return size == 84 + 50 * n


def _read_binary(path: str) -> List[Tuple[Vec, Vec, Vec]]:
    tris = []
    with open(path, "rb") as fh:
        fh.read(80)
        n = struct.unpack("<I", fh.read(4))[0]
        for _ in range(n):
            data = fh.read(50)
            if len(data) < 50:
                break
            vals = struct.unpack("<12fH", data)
            v1 = (vals[3], vals[4], vals[5])
            v2 = (vals[6], vals[7], vals[8])
            v3 = (vals[9], vals[10], vals[11])
            tris.append((v1, v2, v3))
    return tris


def _read_ascii(path: str) -> List[Tuple[Vec, Vec, Vec]]:
    tris = []
    verts: List[Vec] = []
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            s = line.strip()
            if s.startswith("vertex"):
                parts = s.split()
                verts.append((float(parts[1]), float(parts[2]), float(parts[3])))
                if len(verts) == 3:
                    tris.append((verts[0], verts[1], verts[2]))
                    verts = []
    return tris


def _cross(a: Vec, b: Vec) -> Vec:
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _sub(a: Vec, b: Vec) -> Vec:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _dot(a: Vec, b: Vec) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def analyze_stl(path: str) -> dict:
    if not os.path.isfile(path):
        raise FileNotFoundError(f"No such STL file: {path}")

    fmt = "binary" if _is_binary_stl(path) else "ascii"
    tris = _read_binary(path) if fmt == "binary" else _read_ascii(path)
    if not tris:
        return {"path": path, "format": fmt, "error": "No triangles parsed."}

    # Bounding box, area, signed volume
    xs = [v[0] for t in tris for v in t]
    ys = [v[1] for t in tris for v in t]
    zs = [v[2] for t in tris for v in t]
    bbox_min = (min(xs), min(ys), min(zs))
    bbox_max = (max(xs), max(ys), max(zs))
    size = tuple(bbox_max[i] - bbox_min[i] for i in range(3))

    area = 0.0
    signed_vol = 0.0
    for v1, v2, v3 in tris:
        n = _cross(_sub(v2, v1), _sub(v3, v1))
        area += 0.5 * math.sqrt(_dot(n, n))
        signed_vol += _dot(v1, _cross(v2, v3)) / 6.0

    # Watertight check: every edge should be shared by exactly two triangles.
    # Quantize vertices to tolerance to fuse near-duplicates.
    scale = max(size) if max(size) > 0 else 1.0
    tol = scale * 1e-6

    def key(v: Vec):
        return (round(v[0] / tol), round(v[1] / tol), round(v[2] / tol))

    edge_count = {}
    for v1, v2, v3 in tris:
        ks = [key(v1), key(v2), key(v3)]
        for i in range(3):
            a, b = ks[i], ks[(i + 1) % 3]
            e = (a, b) if a <= b else (b, a)
            edge_count[e] = edge_count.get(e, 0) + 1
    open_edges = sum(1 for c in edge_count.values() if c != 2)
    watertight = open_edges == 0

    # Suggested background mesh: ~20 cells across the smallest non-zero dim.
    nonzero = [s for s in size if s > 0]
    base_cell = (min(nonzero) / 20.0) if nonzero else 0.0

    return {
        "path": path,
        "format": fmt,
        "triangles": len(tris),
        "bounding_box_min": bbox_min,
        "bounding_box_max": bbox_max,
        "size_m": size,
        "surface_area_m2": area,
        "enclosed_volume_m3": abs(signed_vol),
        "watertight": watertight,
        "open_edges": open_edges,
        "suggested_background_cell_m": base_cell,
        "snappyhexmesh_notes": (
            ("Mesh is watertight — good to use as a snappyHexMesh surface. "
             if watertight else
             f"NOT watertight ({open_edges} unpaired edges) — repair/close the "
             "surface (e.g. surfaceCheck, meshlab) before snappyHexMesh, or it "
             "will leak. ")
            + "Place surfaceFeatureExtract on it, set a background blockMesh a "
            "few body-lengths larger than the bounding box, and add refinement "
            "regions around the body."
        ),
    }
