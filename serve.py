"""Static file server + frame collector for the construction-progress export.

    python serve.py [--port 4211] [--root C:/Users/ray/assets/web]

Serves the demo pages and adds a tiny export API so the browser can hand over
one rendered frame at a time; ffmpeg then turns the frames into an MP4.

    POST /_export/start                       reset the frame folder
    POST /_export/frame?i=<n>   (image/jpeg)  store frame n
    POST /_export/finish?fps=30               encode -> /_export/out.mp4
    GET  /_export/out.mp4                     the encoded video
    GET  /_export/status                      progress

Why a server instead of MediaRecorder: canvas.captureStream records in real
time, so any dropped frame makes the video stutter and the clip is not
reproducible. Rendering every frame off a deterministic timeline and encoding
afterwards gives a stable 30 fps file that matches the layout exactly.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import threading
import time
import urllib.parse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

FRAMES = Path(r"C:\Users\ray\assets\web\_frames")
OUT = Path(r"C:\Users\ray\assets\web\_export")
LOCK = threading.Lock()
STATE = {"collecting": False, "frames": 0, "encoding": False, "last": None}

FFMPEG_CANDIDATES = [
    r"C:\Users\ray\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin\ffmpeg.exe",
    r"C:\Program Files\kdenlive\bin\ffmpeg.exe",
]


def ffmpeg_path() -> str | None:
    found = shutil.which("ffmpeg")
    if found:
        return found
    for c in FFMPEG_CANDIDATES:
        if Path(c).exists():
            return c
    return None


class Handler(SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(ROOT), **kw)

    def log_message(self, fmt, *args):
        if "/_export/" not in self.path:
            super().log_message(fmt, *args)

    # -- helpers ------------------------------------------------------------
    def _json(self, code: int, obj: dict) -> None:
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("content-type", "application/json; charset=utf-8")
        self.send_header("content-length", str(len(body)))
        self.send_header("cache-control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _query(self) -> dict:
        q = urllib.parse.urlparse(self.path).query
        return {k: v[0] for k, v in urllib.parse.parse_qs(q).items()}

    def _body(self) -> bytes:
        n = int(self.headers.get("content-length") or 0)
        return self.rfile.read(n) if n else b""

    # -- routes -------------------------------------------------------------
    def do_POST(self):  # noqa: N802
        path = urllib.parse.urlparse(self.path).path
        q = self._query()

        if path == "/_export/start":
            self._body()
            with LOCK:
                if FRAMES.exists():
                    shutil.rmtree(FRAMES, ignore_errors=True)
                FRAMES.mkdir(parents=True, exist_ok=True)
                OUT.mkdir(parents=True, exist_ok=True)
                STATE.update(collecting=True, frames=0, encoding=False, last=None)
            self._json(200, {"ok": True})
            return

        if path == "/_export/frame":
            data = self._body()
            i = int(q.get("i", "0"))
            with LOCK:
                if not STATE["collecting"]:
                    self._json(409, {"ok": False, "error": "not collecting"})
                    return
                (FRAMES / f"f{i:05d}.jpg").write_bytes(data)
                STATE["frames"] = max(STATE["frames"], i + 1)
            self._json(200, {"ok": True, "i": i, "bytes": len(data)})
            return

        if path == "/_export/finish":
            self._body()
            fps = int(q.get("fps", "30"))
            with LOCK:
                STATE["collecting"] = False
                STATE["encoding"] = True
                n = STATE["frames"]
            ff = ffmpeg_path()
            if not ff:
                with LOCK:
                    STATE["encoding"] = False
                self._json(500, {"ok": False, "error": "ffmpeg not found"})
                return
            out = OUT / "construction-progress.mp4"
            cmd = [
                ff, "-y", "-hide_banner", "-loglevel", "error",
                "-framerate", str(fps),
                "-i", str(FRAMES / "f%05d.jpg"),
                "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                str(out),
            ]
            t0 = time.time()
            proc = subprocess.run(cmd, capture_output=True)
            with LOCK:
                STATE["encoding"] = False
                STATE["last"] = {
                    "ok": proc.returncode == 0,
                    "frames": n,
                    "seconds": round(time.time() - t0, 1),
                    "bytes": out.stat().st_size if out.exists() else 0,
                    "stderr": proc.stderr.decode("utf-8", "replace")[-400:],
                }
            if proc.returncode != 0:
                self._json(500, {"ok": False, **STATE["last"]})
                return
            self._json(200, {"ok": True, "url": "/_export/out.mp4", **_STATE_SAFE()})
            return

        self._json(404, {"ok": False, "error": "not found"})

    def do_GET(self):  # noqa: N802
        path = urllib.parse.urlparse(self.path).path
        if path == "/_export/status":
            self._json(200, dict(ok=True, **_STATE_SAFE()))
            return
        if path == "/_export/out.mp4":
            f = OUT / "construction-progress.mp4"
            if not f.exists():
                self._json(404, {"ok": False, "error": "no export yet"})
                return
            data = f.read_bytes()
            self.send_response(200)
            self.send_header("content-type", "video/mp4")
            self.send_header("content-length", str(len(data)))
            self.send_header("accept-ranges", "none")
            self.end_headers()
            self.wfile.write(data)
            return
        super().do_GET()


def _STATE_SAFE() -> dict:
    d = {"frames": STATE["frames"], "encoding": STATE["encoding"]}
    if STATE["last"]:
        d["last"] = {k: v for k, v in STATE["last"].items() if k != "stderr"}
    return d


ROOT = Path(r"C:\Users\ray\assets\web")


def main() -> int:
    global ROOT
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=4211)
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--root", default=str(ROOT))
    a = p.parse_args()

    ROOT = Path(a.root)
    os.chdir(ROOT)
    print(f"[serve] {ROOT} on http://{a.host}:{a.port}  ffmpeg={ffmpeg_path()}", flush=True)
    ThreadingHTTPServer((a.host, a.port), Handler).serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
