#!/usr/bin/env python3
"""Regenerate frontend/static-demo.json from backend demo logic."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from backend.modes.failed_pilot import run_failed_pilot
from backend.modes.production import run_production

ROOT = Path(__file__).resolve().parents[1]


async def collect(gen):
    return [event async for event in gen]


async def main() -> None:
    failed = await collect(run_failed_pilot("high-northline"))
    production = await collect(run_production("high-northline", approved=False))
    approved = await collect(run_production("high-northline", approved=True))

    tail: list[dict] = []
    for index, event in enumerate(approved):
        if event.get("message", "").startswith("HITL approval"):
            tail = approved[index:]
            break

    scenarios = json.loads((ROOT / "data/scenarios.json").read_text(encoding="utf-8"))
    payload = {
        "scenarios": scenarios,
        "failed": failed,
        "production": production,
        "production_approved_tail": tail,
    }
    out = ROOT / "frontend/static-demo.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    asyncio.run(main())