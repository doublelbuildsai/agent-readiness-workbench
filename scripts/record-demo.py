#!/usr/bin/env python3
"""Record the autoplay demo to a video file (no manual screen capture)."""

from __future__ import annotations

import argparse
import shutil
import socket
import subprocess
import sys
import threading
import time
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
OUTPUT_DIR = ROOT / "recordings"
VIEWPORT = {"width": 1440, "height": 900}


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def build_static() -> None:
    subprocess.run([sys.executable, str(ROOT / "scripts" / "build-static.py")], check=True, cwd=ROOT)


def start_server(port: int) -> tuple[ThreadingHTTPServer, threading.Thread]:
    dist_dir = str(DIST)

    class DistHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=dist_dir, **kwargs)

        def log_message(self, format: str, *args) -> None:
            return

    server = ThreadingHTTPServer(("127.0.0.1", port), DistHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def ensure_playwright() -> None:
    try:
        import playwright  # noqa: F401
    except ImportError:
        print("Installing recording dependencies…")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(ROOT / "requirements-record.txt")],
            check=True,
        )
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)


def convert_to_mp4(source: Path, target: Path) -> Path:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        return source
    subprocess.run(
        [ffmpeg, "-y", "-i", str(source), "-c:v", "libx264", "-pix_fmt", "yuv420p", str(target)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    source.unlink(missing_ok=True)
    return target


def record_demo(pace: int, hold_seconds: float) -> Path:
    from playwright.sync_api import sync_playwright

    build_static()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    port = find_free_port()
    server, _thread = start_server(port)

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    staging_dir = OUTPUT_DIR / f".capture-{stamp}"
    staging_dir.mkdir(parents=True, exist_ok=True)

    url = f"http://127.0.0.1:{port}/?record=1&pace={pace}"
    timeout_ms = int((90 + hold_seconds) * 1000 * max(1, pace / 3))

    print(f"Recording {url}")
    print(f"Viewport: {VIEWPORT['width']}×{VIEWPORT['height']} (≈{pace}x pacing)")

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(
                viewport=VIEWPORT,
                record_video_dir=str(staging_dir),
                record_video_size=VIEWPORT,
                device_scale_factor=1,
            )
            page = context.new_page()
            page.goto(url, wait_until="networkidle")
            page.wait_for_function(
                '() => document.body.dataset.recordComplete === "true"',
                timeout=timeout_ms,
            )
            page.wait_for_timeout(int(hold_seconds * 1000))
            page.close()
            context.close()
            browser.close()

        captures = sorted(staging_dir.glob("*.webm"), key=lambda path: path.stat().st_mtime)
        if not captures:
            raise RuntimeError("Playwright did not produce a video file.")

        webm_path = OUTPUT_DIR / f"agent-readiness-demo-{stamp}.webm"
        shutil.move(str(captures[-1]), webm_path)
        shutil.rmtree(staging_dir, ignore_errors=True)

        mp4_path = OUTPUT_DIR / f"agent-readiness-demo-{stamp}.mp4"
        final_path = convert_to_mp4(webm_path, mp4_path)
        return final_path
    finally:
        server.shutdown()


def main() -> None:
    parser = argparse.ArgumentParser(description="Record the agent readiness workbench demo.")
    parser.add_argument("--pace", type=float, default=3.5, help="Agent-step pacing multiplier (default: 3.5 ≈ 70s)")
    parser.add_argument("--hold", type=float, default=4.0, help="Seconds to hold on the results screen")
    args = parser.parse_args()

    ensure_playwright()
    output = record_demo(pace=args.pace, hold_seconds=args.hold)
    print(f"\nSaved demo video → {output}")
    print("Upload this file to LinkedIn as a native video.")


if __name__ == "__main__":
    main()