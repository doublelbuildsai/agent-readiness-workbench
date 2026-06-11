from __future__ import annotations

from typing import Any


def validate_config(opportunity: dict[str, Any]) -> dict[str, Any]:
    products = opportunity.get("products", [])
    issues: list[str] = []

    if not products:
        issues.append("No products configured")
    if opportunity.get("discount_requested", 0) > 0.30:
        issues.append("Discount exceeds CPQ maximum (30%)")

    return {
        "valid": len(issues) == 0,
        "sku_count": len(products),
        "bundle_count": max(1, len(products) // 4),
        "issues": issues,
    }


def generate_quote(opportunity: dict[str, Any], approved_discount: float | None = None) -> dict[str, Any]:
    discount = approved_discount if approved_discount is not None else opportunity.get("discount_requested", 0)
    acv = opportunity.get("acv", 0)
    net_acv = round(acv * (1 - discount), 2)

    return {
        "quote_id": f"SG-Q-{opportunity['id'].split('-')[-1].upper()}",
        "account": opportunity["account"],
        "list_price": acv,
        "discount_pct": discount,
        "net_price": net_acv,
        "payment_terms": opportunity.get("payment_terms", "net-30"),
        "products": opportunity.get("products", []),
        "status": "draft",
    }