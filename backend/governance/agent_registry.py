from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentIdentity:
    agent_id: str
    role: str
    scopes: tuple[str, ...]


PRODUCTION_AGENTS = {
    "orchestrator": AgentIdentity("orch-001", "Orchestrator", ("workflow.plan",)),
    "deal": AgentIdentity("deal-agent-02", "DealAgent", ("salesforce.read",)),
    "policy": AgentIdentity("policy-agent-03", "PolicyAgent", ("knowledge_base.search",)),
    "pricing": AgentIdentity("pricing-agent-04", "PricingAgent", ("cpq.read", "cpq.write")),
    "compliance": AgentIdentity("compliance-agent-05", "ComplianceAgent", ("approval.route", "audit.write")),
}

FAILED_PILOT_AGENT = AgentIdentity(
    "super-agent-00",
    "MonolithicAgent",
    ("salesforce.*", "cpq.*", "approval.*", "audit.*"),
)