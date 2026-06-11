from __future__ import annotations

import re
from pathlib import Path

from backend.config import POLICIES_DIR


def _tokenize(text: str) -> set[str]:
    return {token.lower() for token in re.findall(r"[a-zA-Z0-9%]+", text)}


def _load_documents() -> list[dict[str, str]]:
    documents: list[dict[str, str]] = []
    for path in sorted(POLICIES_DIR.glob("*.md")):
        documents.append({"source": path.name, "content": path.read_text(encoding="utf-8")})
    return documents


def search(query: str, limit: int = 3) -> dict:
    query_tokens = _tokenize(query)
    scored: list[tuple[float, dict[str, str]]] = []

    for doc in _load_documents():
        content_tokens = _tokenize(doc["content"])
        overlap = len(query_tokens & content_tokens)
        if overlap:
            scored.append((overlap / max(len(query_tokens), 1), doc))

    scored.sort(key=lambda item: item[0], reverse=True)
    hits = [
        {
            "source": doc["source"],
            "excerpt": doc["content"][:280].replace("\n", " ").strip(),
            "score": round(score, 2),
        }
        for score, doc in scored[:limit]
    ]

    return {"query": query, "hits": hits, "count": len(hits)}