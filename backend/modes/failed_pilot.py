from __future__ import annotations

import asyncio
import json
from typing import Any, AsyncIterator

from backend.config import DATA_DIR
from backend.governance.agent_registry import FAILED_PILOT_AGENT
from backend.governance.margin_impact import compute_unauthorized_margin_impact
from backend.tools import build_tool_registry

TraceEvent = dict[str, Any]


def _load_scenario(scenario_id: str) -> dict[str, Any]:
    scenarios = json.loads((DATA_DIR / "scenarios.json").read_text(encoding="utf-8"))
    for scenario in scenarios:
        if scenario["id"] == scenario_id:
            return scenario
    raise KeyError(f"Scenario not found: {scenario_id}")


async def _emit(event_type: str, **payload: Any) -> TraceEvent:
    await asyncio.sleep(0.5)
    return {"type": event_type, **payload}


async def run_failed_pilot(scenario_id: str) -> AsyncIterator[TraceEvent]:
    scenario = _load_scenario(scenario_id)
    registry = build_tool_registry()
    agent = FAILED_PILOT_AGENT
    opportunity_id = scenario["opportunity_id"]

    yield await _emit(
        "trace",
        agent="MonolithicAgent",
        agent_id=agent.agent_id,
        message="Processing deal with broad CRM + pricing + approval access",
        status="running",
        warning="Unbounded permissions: salesforce.*, cpq.*, approval.*",
    )

    crm_call = registry.execute("salesforce.get_opportunity", agent.agent_id, opportunity_id=opportunity_id)
    opportunity = crm_call.outputs["opportunity"]

    yield await _emit(
        "trace",
        agent="MonolithicAgent",
        agent_id=agent.agent_id,
        message=f"CRM loaded: {opportunity['account']} — skipping policy RAG",
        status="warning",
        warning="No policy grounding — LLM memory only",
    )

    discount = opportunity["discount_requested"]
    effective_discount = discount
    stacking_violation = False

    rebate = 0.0
    if opportunity.get("volume_rebate_active"):
        rebate = opportunity.get("volume_rebate_pct", 0.05)
        effective_discount = discount + rebate
        stacking_violation = True

        yield await _emit(
            "trace",
            agent="MonolithicAgent",
            agent_id=agent.agent_id,
            message=f"Applied {discount:.0%} promo + {rebate:.0%} volume rebate (STACKED)",
            status="error",
            warning="Promo stacking violation — promotional_pricing_policy.md",
        )

    if opportunity["tier"] == "Tier-1 Retail" and discount > 0.15:
        pass
        yield await _emit(
            "trace",
            agent="MonolithicAgent",
            agent_id=agent.agent_id,
            message=f"Auto-approved {discount:.0%} discount — Tier-1 cap (15%) ignored",
            status="error",
            warning="retail_channel_pricing_rules.md — VP approval bypassed",
        )

    yield await _emit(
        "trace",
        agent="MonolithicAgent",
        agent_id=agent.agent_id,
        message="Routing approvals sequentially — estimated 72–96 hours",
        status="warning",
        warning="No parallel routing — sequential delay remains",
    )

    quote_call = registry.execute(
        "cpq.generate_quote",
        agent.agent_id,
        opportunity=opportunity,
        approved_discount=effective_discount if stacking_violation else None,
    )

    yield await _emit(
        "trace",
        agent="MonolithicAgent",
        agent_id=agent.agent_id,
        message=f"Quote auto-generated: {quote_call.outputs['quote_id']} — no audit trail",
        status="error",
        warning="No audit log — Finance cannot reconcile (Deloitte 2026: only 21% mature governance)",
    )

    yield await _emit(
        "complete",
        mode="failed",
        scenario=scenario,
        outcome=scenario["failed_outcome"],
        quote=quote_call.outputs,
        turnaround_hours=scenario["manual_turnaround_hours"],
        manual_hours=scenario["manual_turnaround_hours"],
        margin_at_risk=compute_unauthorized_margin_impact(opportunity)["total_dollars"],
        stacking_violation=stacking_violation,
        violations=[
            "Unauthorized discount authority bypassed",
            "Promo + rebate stacking" if stacking_violation else None,
            "No audit trail for Finance review",
            "Sequential approval delay unchanged",
        ],
        governance={
            "agent_identity": False,
            "audit_trail": False,
            "scoped_tools": False,
            "kill_switch": False,
            "policy_grounded": False,
        },
    )