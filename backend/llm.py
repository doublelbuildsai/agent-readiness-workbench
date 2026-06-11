from __future__ import annotations

from typing import Any

from openai import OpenAI

from backend.config import settings


def llm_available() -> bool:
    return bool(settings.llm_api_key)


async def summarize_deal_brief(opportunity: dict[str, Any], mode: str) -> str | None:
    if not llm_available():
        return None

    client = OpenAI(api_key=settings.llm_api_key, base_url=settings.llm_base_url)
    prompt = (
        f"Write a 2-sentence executive brief for a {mode} revenue agent run. "
        f"Account: {opportunity['account']}, ACV: ${opportunity['acv']:,}, "
        f"discount: {opportunity['discount_requested']:.0%}. Be specific, no hype."
    )

    try:
        response = client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": "You write concise B2B revenue operations briefs."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=120,
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception:
        return None