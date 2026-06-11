#!/usr/bin/env python3
"""Copy frontend assets into dist/ for static preview hosting."""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "frontend"
DIST = ROOT / "dist"
FILES = ["index.html", "styles.css", "app.js", "static-demo.json"]


def main() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    for name in FILES:
        shutil.copy2(SRC / name, DIST / name)
    (DIST / ".nojekyll").touch()
    print("Built static site → dist/")
    print("Preview: python3 -m http.server 4173 --directory dist")


if __name__ == "__main__":
    main()