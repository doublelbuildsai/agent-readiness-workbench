from __future__ import annotations

import json
from pathlib import Path

from backend.config import DATA_DIR


def _load_opportunities() -> list[dict]:
    return json.loads((DATA_DIR / "opportunities.json").read_text(encoding="utf-8"))


def _load_reps() -> list[dict]:
    return json.loads((DATA_DIR / "reps.json").read_text(encoding="utf-8"))


def get_opportunity(opportunity_id: str) -> dict:
    for opp in _load_opportunities():
        if opp["id"] == opportunity_id:
            rep = next((r for r in _load_reps() if r["id"] == opp["rep"]), None)
            return {"opportunity": opp, "rep": rep}
    raise KeyError(f"Opportunity not found: {opportunity_id}")