"""Download Poly Haven CC0 models as GLB.

    python ph_download.py <asset_id> [asset_id ...] [--res 1k]

Poly Haven serves glTF as a `.gltf` plus a set of `include` files (bin + jpg
textures). This pulls the whole set into one folder, then converts to a single
self-contained .glb with Blender.

Everything is CC0 — no attribution required, commercial use fine.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
OUT = Path(r"C:\Users\ray\assets\free\polyhaven")
GLB = Path(r"C:\Users\ray\assets\web\models\ph")
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"


def get(url: str, timeout: int = 90) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def get_json(url: str) -> dict:
    return json.loads(get(url).decode("utf-8"))


def fetch_asset(asset: str, res: str = "1k") -> Path | None:
    info = get_json(f"https://api.polyhaven.com/files/{asset}")
    gltf = (info.get("gltf") or {}).get(res)
    if not gltf or "gltf" not in gltf:
        print(f"  ! {asset}: no gltf at {res}")
        return None

    folder = OUT / asset
    if folder.exists():
        import shutil

        shutil.rmtree(folder)
    folder.mkdir(parents=True, exist_ok=True)

    main = gltf["gltf"]
    target = folder / Path(main["url"]).name
    target.write_bytes(get(main["url"]))
    got = 1

    for rel, meta in (main.get("include") or {}).items():
        dest = folder / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(get(meta["url"]))
        got += 1
    print(f"  {asset}: {got} files, {sum(f.stat().st_size for f in folder.rglob('*') if f.is_file())/1e6:.1f} MB")
    return target


def to_glb(gltf_path: Path, name: str) -> None:
    GLB.mkdir(parents=True, exist_ok=True)
    out = GLB / f"{name}.glb"
    r = subprocess.run(
        [BLENDER, "--background", "--factory-startup", "--python", r"C:\Users\ray\gltf2glb.py",
         "--", str(gltf_path), str(out)],
        capture_output=True, text=True,
    )
    for line in (r.stdout or "").splitlines():
        if line.startswith(("triangles", "glb ", "images")):
            print("    " + line)


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    res = "1k"
    for a in sys.argv[1:]:
        if a.startswith("--res"):
            res = a.split("=")[-1] if "=" in a else res
    if len(sys.argv) > 2 and sys.argv[-2] == "--res":
        res = sys.argv[-1]
        args = [a for a in args if a != res]

    if not args:
        print(__doc__)
        return 2

    for asset in args:
        t0 = time.time()
        p = fetch_asset(asset, res)
        if p:
            to_glb(p, asset)
        print(f"  {asset} done in {time.time()-t0:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
