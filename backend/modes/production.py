from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any, AsyncIterator

from backend.config import DATA_DIR
from backend.governance.agent_registry import PRODUCTION_AGENTS
from backend.governance.audit_log import AuditLog
from backend.governance.margin_impact import compute_unauthorized_margin_impact
from backend.governance.risk_engine import assess_deal_risk
from backend.tools import build_tool_registry
from backend.tools.knowledge_base import search as kb_search

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


async def run_production(scenario_id: str, approved: bool = False) -> AsyncIterator[TraceEvent]:
    scenario = _load_scenario(scenario_id)
    registry = build_tool_registry()
    audit = AuditLog(enabled=True)
    opportunity_id = scenario["opportunity_id"]

    yield await _emit(
        "trace",
        agent="Orchestrator",
        agent_id=PRODUCTION_AGENTS["orchestrator"].agent_id,
        message="Task decomposed into 4 subtasks: research → policy → pricing → compliance",
        status="complete",
    )

    crm_call = registry.execute("salesforce.get_opportunity", PRODUCTION_AGENTS["deal"].agent_id, opportunity_id=opportunity_id)
    opportunity = crm_call.outputs["opportunity"]
    rep = crm_call.outputs.get("rep")
    audit.log(PRODUCTION_AGENTS["deal"].agent_id, "crm_lookup", {"account": opportunity["account"], "acv": opportunity["acv"]})

    yield await _emit(
        "trace",
        agent="DealAgent",
        agent_id=PRODUCTION_AGENTS["deal"].agent_id,
        message=f"salesforce.get_opportunity → {opportunity['account']}, ${opportunity['acv']:,}, {opportunity['tier']}",
        status="complete",
        tool="salesforce.get_opportunity",
    )

    policy_queries = [
        f"{opportunity['tier']} discount cap",
        "promotional pricing stacking volume rebate",
        f"{opportunity.get('payment_terms', 'net-30')} payment terms approval",
    ]
    citations: list[str] = []
    violations: list[str] = []

    for query in policy_queries:
        result = kb_search(query)
        for hit in result["hits"]:
            citations.append(hit["source"])

    if opportunity["tier"] == "Tier-1 Retail" and opportunity["discount_requested"] > 0.15:
        violations.append("Tier-1 retail cap exceeded: 15% max without VP Sales")
    if opportunity.get("volume_rebate_active") and opportunity["discount_requested"] > 0.10:
        violations.append("Promo + volume rebate stacking prohibited")
    if opportunity.get("payment_terms") == "net-60" and opportunity["acv"] > 250000:
        violations.append("Net-60 on deals >$250K requires Finance approval")
    violations = list(dict.fromkeys(violations))

    audit.log(
        PRODUCTION_AGENTS["policy"].agent_id,
        "policy_search",
        {"citations": list(dict.fromkeys(citations)), "violations": violations},
    )

    yield await _emit(
        "trace",
        agent="PolicyAgent",
        agent_id=PRODUCTION_AGENTS["policy"].agent_id,
        message=f"knowledge_base.search → {len(set(citations))} policy citations, {len(violations)} flags",
        status="complete",
        tool="knowledge_base.search",
        citations=list(dict.fromkeys(citations)),
    )

    for violation in violations:
        yield await _emit(
            "trace",
            agent="PolicyAgent",
            agent_id=PRODUCTION_AGENTS["policy"].agent_id,
            message=f"Policy flag: {violation}",
            status="warning",
        )

    cpq_call = registry.execute(
        "cpq.validate_config",
        PRODUCTION_AGENTS["pricing"].agent_id,
        opportunity=opportunity,
    )
    audit.log(PRODUCTION_AGENTS["pricing"].agent_id, "cpq_validate", cpq_call.outputs)

    yield await _emit(
        "trace",
        agent="PricingAgent",
        agent_id=PRODUCTION_AGENTS["pricing"].agent_id,
        message=f"cpq.validate_config ✓ ({cpq_call.outputs['sku_count']} SKUs, {cpq_call.outputs['bundle_count']} bundles)",
        status="complete",
        tool="cpq.validate_config",
    )

    risk = assess_deal_risk(opportunity, {"violations": violations, "citations": citations})
    audit.log(PRODUCTION_AGENTS["compliance"].agent_id, "risk_assessment", {
        "risk_score": risk.risk_score,
        "approvers": risk.approvers,
        "violations": risk.violations,
    })

    yield await _emit(
        "trace",
        agent="ComplianceAgent",
        agent_id=PRODUCTION_AGENTS["compliance"].agent_id,
        message=f"risk_score: {risk.risk_score} → {'PARALLEL_APPROVAL_REQUIRED' if risk.requires_parallel_approval else 'STANDARD_ROUTING'}",
        status="complete",
    )

    if risk.requires_hitl:
        approval_call = registry.execute(
            "approval.route_parallel",
            PRODUCTION_AGENTS["compliance"].agent_id,
            approvers=risk.approvers,
            deal_context={**opportunity, "violations": violations},
        )
        routing = "parallel" if risk.requires_parallel_approval else "sequential"
        yield await _emit(
            "trace",
            agent="ComplianceAgent",
            agent_id=PRODUCTION_AGENTS["compliance"].agent_id,
            message=f"approval.route_{routing} → {', '.join(risk.approvers)}",
            status="pending",
            tool="approval.route_parallel",
        )

        if not approved:
            yield await _emit(
                "hitl_required",
                approvers=risk.approvers,
                risk_score=risk.risk_score,
                violations=violations,
                message="Awaiting human approval before quote generation",
            )
            return

        audit.log(PRODUCTION_AGENTS["compliance"].agent_id, "hitl_approved", {"approvers": risk.approvers})
        yield await _emit(
            "trace",
            agent="ComplianceAgent",
            agent_id=PRODUCTION_AGENTS["compliance"].agent_id,
            message="HITL approval received — proceeding to quote generation",
            status="complete",
        )

    approved_discount = min(opportunity["discount_requested"], 0.15) if risk.requires_hitl else opportunity["discount_requested"]
    quote_call = registry.execute(
        "cpq.generate_quote",
        PRODUCTION_AGENTS["pricing"].agent_id,
        opportunity=opportunity,
        approved_discount=approved_discount if risk.requires_hitl else None,
    )
    audit.log(PRODUCTION_AGENTS["pricing"].agent_id, "quote_generated", quote_call.outputs)

    yield await _emit(
        "trace",
        agent="PricingAgent",
        agent_id=PRODUCTION_AGENTS["pricing"].agent_id,
        message=f"cpq.generate_quote → {quote_call.outputs['quote_id']} (${quote_call.outputs['net_price']:,} net)",
        status="complete",
        tool="cpq.generate_quote",
    )

    audit.log(PRODUCTION_AGENTS["compliance"].agent_id, "audit_export", {"event_count": len(audit.export())})
    yield await _emit(
        "trace",
        agent="ComplianceAgent",
        agent_id=PRODUCTION_AGENTS["compliance"].agent_id,
        message=f"audit_event logged ({len(audit.export())} events, append-only)",
        status="complete",
    )

    margin_impact = compute_unauthorized_margin_impact(opportunity) if violations else {
        "cap_excess_dollars": 0.0,
        "stacking_dollars": 0.0,
        "total_dollars": 0.0,
    }

    yield await _emit(
        "complete",
        mode="production",
        scenario=scenario,
        outcome=scenario["production_outcome"],
        quote=quote_call.outputs,
        risk_score=risk.risk_score,
        turnaround_hours=scenario["production_turnaround_hours"],
        manual_hours=scenario["manual_turnaround_hours"],
        margin_protected=margin_impact["total_dollars"],
        audit=audit.export(),
        rep=rep,
        governance={
            "agent_identity": True,
            "audit_trail": True,
            "scoped_tools": True,
            "kill_switch": True,
            "policy_grounded": True,
        },
    )