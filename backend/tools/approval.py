from __future__ import annotations

from typing import Any


def route_parallel(approvers: list[str], deal_context: dict[str, Any]) -> dict[str, Any]:
    routes = [
        {
            "approver": approver,
            "status": "pending",
            "brief": {
                "account": deal_context.get("account"),
                "acv": deal_context.get("acv"),
                "discount_requested": deal_context.get("discount_requested"),
                "payment_terms": deal_context.get("payment_terms"),
                "violations": deal_context.get("violations", []),
            },
        }
        for approver in approvers
    ]
    return {
        "routing": "parallel",
        "approvers": approvers,
        "routes": routes,
        "estimated_hours": 24 if len(approvers) > 1 else 8,
    }


def check_authority(role: str, discount: float, acv: float) -> dict[str, Any]:
    limits = {
        "Sales Rep": (0.10, 150000),
        "Regional Director": (0.15, 350000),
        "VP Sales": (0.20, 1000000),
    }
    max_discount, max_acv = limits.get(role, (0.05, 50000))
    authorized = discount <= max_discount and acv <= max_acv
    return {
        "role": role,
        "authorized": authorized,
        "max_discount": max_discount,
        "max_acv": max_acv,
    }