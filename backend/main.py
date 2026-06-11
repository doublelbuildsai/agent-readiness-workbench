from __future__ import annotations

import json
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.config import DATA_DIR, ROOT_DIR, settings
from backend.llm import llm_available
from backend.modes.failed_pilot import run_failed_pilot
from backend.modes.production import run_production

app = FastAPI(title="Agent Readiness Workbench", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = ROOT_DIR / "frontend"


class RunRequest(BaseModel):
    scenario_id: str
    mode: str  # "failed" | "production"
    approved: bool = False


@app.get("/api/health")
async def health() -> dict:
    return {
        "status": "ok",
        "llm_configured": llm_available(),
        "model": settings.llm_model if llm_available() else None,
    }


@app.get("/api/scenarios")
async def list_scenarios() -> list[dict]:
    return json.loads((DATA_DIR / "scenarios.json").read_text(encoding="utf-8"))


async def _stream_events(generator: AsyncIterator[dict]) -> AsyncIterator[str]:
    async for event in generator:
        yield f"data: {json.dumps(event)}\n\n"


@app.post("/api/run")
async def run_scenario(request: RunRequest) -> StreamingResponse:
    if request.mode not in {"failed", "production"}:
        raise HTTPException(status_code=400, detail="mode must be 'failed' or 'production'")

    if request.mode == "failed":
        generator = run_failed_pilot(request.scenario_id)
    else:
        generator = run_production(request.scenario_id, approved=request.approved)

    return StreamingResponse(_stream_events(generator), media_type="text/event-stream")


if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")