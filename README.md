# Agent Readiness Workbench

A side-by-side demo of **the same wholesale deal, two agent architectures** — a failed agentic pilot vs. a production-grade revenue agent stack.

Built for **Summit Gear Co.** (fictional outdoor products wholesaler) selling to retail chains like **Northline Retail Group**.

## Why this demo exists

Enterprise teams are hitting a consistent gap:

- Most agentic workflows stall before production
- Pilots often fail to prove ROI — not because models are weak, but because **governance, integration, and bounded scope** are underbuilt
- Revenue teams invest in agents, but deals still stall in approval chains

This workbench makes that gap visible in about two minutes.

## What it demonstrates

| Pattern | Failed pilot | Production lane |
|---------|--------------|-----------------|
| Agent identity | Monolithic super-agent | Scoped subagents with IDs |
| Policy grounding | LLM memory only | RAG over channel + promo policies |
| Approvals | Auto-approve / sequential | Risk-tiered + parallel routing |
| Audit trail | None | Append-only export for Finance |
| HITL | Bypassed | Required for high-risk deals |

## Quick start (local with API)

```bash
cd agent-readiness-workbench
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # optional: add LLM_API_KEY for live model calls
./run.sh
```

Open http://localhost:8080

## Static preview (no API)

Build a self-contained copy that runs from pre-recorded events in `static-demo.json`:

```bash
python3 scripts/build-static.py
python3 -m http.server 4173 --directory dist
```

Open http://localhost:4173

Regenerate `static-demo.json` after backend changes:

```bash
PYTHONPATH="$(pwd)" python3 scripts/export-static-demo.py
```

## Walkthrough

1. Start the guided story and review the **Northline Retail** deal
2. Play the **Typical pilot** path — auto-approval, promo stacking, no audit
3. Play the **Production approach** — policy checks, risk score, parallel routing
4. Approve the HITL gate — quote generates with audit export
5. Review results and optionally download the approval record

## API

- `GET /api/health` — check LLM configuration
- `GET /api/scenarios` — list demo deals
- `POST /api/run` — SSE stream (`scenario_id`, `mode`: `failed`|`production`, `approved`: bool)

## Architecture

```
Rep request → Orchestrator
  → DealAgent (CRM)
  → PolicyAgent (RAG)
  → PricingAgent (CPQ)
  → ComplianceAgent (risk + HITL + audit)
```

Failed lane: single MonolithicAgent with unbounded permissions.

## Themes

- Agentic workflows need scoped agents, not monolithic super-agents
- Production adoption depends on governance, auditability, and human sign-off — not model quality alone
- Revenue and front-office automation fails when RevOps and Finance cannot trust the approval path

## License

MIT — demo data is fictional.