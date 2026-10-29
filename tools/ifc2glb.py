"""Convert an IFC BIM model to GLB using ifcopenshell + trimesh.

    python ifc2glb.py <in.ifc> <out.glb>

Why this exists: `.rfa` (Revit family) has no free conversion path — every RFA
converter needs Revit installed or is a paid product. IFC is the open BIM
format, so the working route for BIM content is: find the IFC version of the
object, then run it through here.

Geometry comes from ifcopenshell's triangulation in world coordinates.
Materials are reduced to flat colours, because BIM models carry material names
rather than textures.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import trimesh


def colour_for(name: str) -> np.ndarray:
    n = (name or "").lower()
    if "concrete" in n:
        return np.array([176, 176, 172, 255], dtype=np.uint8)
    if "steel" in n or "metal" in n:
        return np.array([132, 140, 148, 255], dtype=np.uint8)
    if "wood" in n or "timber" in n:
        return np.array([176, 137, 84, 255], dtype=np.uint8)
    if "glass" in n:
        return np.array([150, 190, 210, 255], dtype=np.uint8)
    if "brick" in n or "masonry" in n:
        return np.array([160, 96, 78, 255], dtype=np.uint8)
    return np.array([168, 172, 178, 255], dtype=np.uint8)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    a = ap.parse_args()

    import ifcopenshell
    import ifcopenshell.geom

    src, dst = Path(a.src), Path(a.dst)
    if not src.exists():
        print(f"missing {src}")
        return 2

    model = ifcopenshell.open(str(src))
    print(f"schema {model.schema}  by_type IfcBuildingElement: "
          f"{len(model.by_type('IfcBuildingElement'))}")

    settings = ifcopenshell.geom.settings()
    settings.set(settings.USE_WORLD_COORDS, True)

    meshes = []
    total_tris = 0
    elements = 0

    it = ifcopenshell.geom.iterator(settings, model)
    if it.initialize():
        while True:
            shape = it.get()
            g = getattr(shape, "geometry", None)
            if g is not None and g.verts:
                verts = np.array(g.verts, dtype=np.float64).reshape(-1, 3)
                faces = np.array(g.faces, dtype=np.int64).reshape(-1, 3)
                if len(faces):
                    m = trimesh.Trimesh(vertices=verts, faces=faces, process=False)
                    name = ""
                    try:
                        ids = list(g.material_ids)
                        mats = list(g.materials)
                        if ids and mats:
                            name = mats[ids[0]].name or ""
                    except Exception:
                        pass
                    m.visual = trimesh.visual.ColorVisuals(m, face_colors=colour_for(name))
                    meshes.append(m)
                    total_tris += len(faces)
                    elements += 1
            if not it.next():
                break

    if not meshes:
        print("no geometry extracted")
        return 3

    scene = trimesh.Scene(meshes)
    dst.parent.mkdir(parents=True, exist_ok=True)
    scene.export(str(dst), file_type="glb")
    size = dst.stat().st_size / 1e6
    ext = scene.bounds[1] - scene.bounds[0]
    print("=== RESULT ===")
    print(f"elements  {elements}")
    print(f"triangles {total_tris:,}")
    print(f"bounds    {np.round(ext, 2)}")
    print(f"glb       {dst}  ({size:.2f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
