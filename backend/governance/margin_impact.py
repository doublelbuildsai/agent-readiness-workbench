from __future__ import annotations

from typing import Any


def compute_unauthorized_margin_impact(opportunity: dict[str, Any]) -> dict[str, float]:
    """Dollars given away beyond policy-compliant pricing (cap breach + illegal stacking)."""
    acv = float(opportunity.get("acv", 0))
    discount = float(opportunity.get("discount_requested", 0))
    tier = opportunity.get("tier", "")

    cap_pct = 0.15 if tier == "Tier-1 Retail" else 0.10
    cap_excess_pct = max(0.0, discount - cap_pct)

    stacking_pct = 0.0
    if opportunity.get("volume_rebate_active") and discount > 0.10:
        stacking_pct = float(opportunity.get("volume_rebate_pct", 0.05))

    cap_excess_dollars = round(acv * cap_excess_pct, 2)
    stacking_dollars = round(acv * stacking_pct, 2)
    total_dollars = round(cap_excess_dollars + stacking_dollars, 2)

    return {
        "cap_excess_dollars": cap_excess_dollars,
        "stacking_dollars": stacking_dollars,
        "total_dollars": total_dollars,
    }