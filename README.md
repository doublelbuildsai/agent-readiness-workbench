# Agent Readiness Workbench

A hybrid demo for personal brand and executive storytelling: **same wholesale deal, two architectures** — a failed agentic pilot vs. a production-grade revenue agent stack.

Built for **Summit Gear Co.** (fictional outdoor products wholesaler) selling to retail chains like **Northline Retail Group**.

## Why this demo exists

Enterprise teams are hitting a consistent gap:

- Most agentic workflows stall before production
- Pilots often fail to prove ROI — not because models are weak, but because **governance, integration, and bounded scope** are underbuilt
- Revenue teams invest in agents, but deals still stall in approval chains

This workbench makes that gap visible in 90 seconds.

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

## Static demo (GitHub Pages — for LinkedIn)

No server needed. The demo auto-plays from `static-demo.json` on GitHub Pages.

```bash
python3 scripts/build-static.py
# or: bash scripts/build-static.sh
python3 -m http.server 4173 --directory dist
```

Open http://localhost:4173

**Autoplay for screen recording:** http://localhost:4173/?record=1

**Automated video capture (no manual recording):**

```bash
bash scripts/record-demo.sh
```

**Deploy:** see [docs/LINKEDIN.md](docs/LINKEDIN.md) and [docs/RECORDING.md](docs/RECORDING.md)

## 90-second demo script

1. Select **Tier-1 Renewal** (Northline Retail, $480K, 22% promo)
2. Click **Run failed pilot** — watch auto-approval, promo stacking, no audit
3. Click **Run production lane** — watch policy RAG, risk score, parallel routing
4. Click **Approve HITL gate** — quote generates with audit export
5. Export audit JSON — show Finance-ready trail

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

## LinkedIn hook

> A retail buyer asks for 22% off a $480K wholesale renewal. Your agentic pilot auto-approves it. Your RevOps team kills the deal. I built a side-by-side demo of what failed vs. what production-grade revenue agents actually need — channel policy grounding, parallel approvals, and an audit trail Finance can use.

## Themes this demo reflects

- Agentic workflows need scoped agents, not monolithic super-agents
- Production adoption depends on governance, auditability, and human sign-off — not model quality alone
- Revenue and front-office automation fails when RevOps and Finance cannot trust the approval path

## License

MIT — demo data is fictional.