from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class RiskAssessment:
    risk_score: float
    requires_hitl: bool
    requires_parallel_approval: bool
    approvers: list[str]
    violations: list[str]
    policy_citations: list[str]


def assess_deal_risk(opportunity: dict[str, Any], policy_findings: dict[str, Any]) -> RiskAssessment:
    violations: list[str] = policy_findings.get("violations", [])
    citations: list[str] = policy_findings.get("citations", [])

    risk = 0.2
    discount = opportunity.get("discount_requested", 0)
    acv = opportunity.get("acv", 0)
    tier = opportunity.get("tier", "")
    payment_terms = opportunity.get("payment_terms", "net-30")

    if discount > 0.15:
        risk += 0.25
    if discount > 0.20:
        risk += 0.2
    if tier == "Tier-1 Retail" and discount > 0.15:
        risk += 0.2
        violations.append("Tier-1 retail cap exceeded: 15% max without VP Sales")
        citations.append("retail_channel_pricing_rules.md")
    if opportunity.get("volume_rebate_active") and discount > 0.10:
        risk += 0.15
        violations.append("Promo + volume rebate stacking prohibited")
        citations.append("promotional_pricing_policy.md")
    if payment_terms == "net-60" and acv > 250000:
        risk += 0.15
        citations.append("payment_terms_policy.md")

    requires_parallel = risk >= 0.7 or discount > 0.20
    approvers: list[str] = []

    if risk >= 0.5:
        approvers.append("Regional Director")
    if risk >= 0.65:
        approvers.append("VP Sales")
    if requires_parallel or payment_terms == "net-60":
        if "Finance" not in approvers:
            approvers.append("Finance")

    approvers = list(dict.fromkeys(approvers))
    if requires_parallel and len(approvers) < 2:
        approvers.extend(["VP Sales", "Finance"])
        approvers = list(dict.fromkeys(approvers))

    return RiskAssessment(
        risk_score=round(min(risk, 1.0), 2),
        requires_hitl=risk >= 0.5,
        requires_parallel_approval=requires_parallel,
        approvers=approvers,
        violations=violations,
        policy_citations=list(dict.fromkeys(citations)),
    )