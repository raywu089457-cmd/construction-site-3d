"""Download Poly Haven CC0 texture sets for construction materials.

    python ph_textures.py [--res 1k] [--maps Diffuse,nor_gl,Rough] brick_4 ...

Writes `assets/web/textures/<id>/<map>_1k.jpg` and a `materials.json` manifest the
viewer can read to build MeshStandardMaterial (map / normalMap / roughnessMap).
"""

from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
OUT = Path(r"C:\Users\ray\assets\web\textures")

DEFAULT = [
    "brick_4",
    "concrete_block_wall",
    "brushed_concrete",
    "plywood",
    "bicolour_gravel",
    "rusty_metal",
    "rusty_corrugated_iron",
    "asphalt_04",
    "sand_01",
]


def get(url: str, timeout: int = 120) -> bytes:
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        return r.read()


def get_json(url: str) -> dict:
    return json.loads(get(url).decode("utf-8"))


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    res = "1k"
    for i, a in enumerate(sys.argv):
        if a == "--res" and i + 1 < len(sys.argv):
            res = sys.argv[i + 1]
            args = [x for x in args if x != res]
    ids = args or DEFAULT

    OUT.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for tid in ids:
        try:
            info = get_json(f"https://api.polyhaven.com/files/{tid}")
        except Exception as e:
            print(f"  ! {tid}: {e}")
            continue
        folder = OUT / tid
        folder.mkdir(exist_ok=True)
        entry = {}
        for api_name, key in (("Diffuse", "map"), ("nor_gl", "normalMap"), ("Rough", "roughnessMap")):
            node = (info.get(api_name) or {}).get(res)
            if not node:
                continue
            meta = node.get("jpg") or node.get("png") or next(iter(node.values()))
            url = meta["url"]
            dest = folder / f"{key}_{res}.jpg"
            if not dest.exists():
                try:
                    dest.write_bytes(get(url))
                except Exception as e:
                    print(f"  ! {tid}/{key}: {e}")
                    continue
            entry[key] = f"textures/{tid}/{dest.name}"
        manifest[tid] = entry
        size = sum(f.stat().st_size for f in folder.iterdir() if f.is_file()) / 1e6
        print(f"  {tid:26s} {len(entry)} maps  {size:5.1f} MB")

    mf = OUT / "materials.json"
    mf.write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    print(f"\n{len(manifest)} 組 -> {mf}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
