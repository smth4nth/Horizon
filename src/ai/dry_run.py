"""Dry-run AI client — returns mock responses without calling any LLM API."""

import json
import re
from typing import Optional

from .client import AIClient


def _extract_title(user: str) -> str:
    """Pull the Title field from a user prompt string."""
    m = re.search(r"^Title:\s*(.+)$", user, re.MULTILINE)
    return m.group(1).strip() if m else "[dry-run item]"


def _extract_summary(user: str) -> str:
    """Pull the Summary field from a user prompt string."""
    m = re.search(r"^Summary:\s*(.+)$", user, re.MULTILINE)
    return m.group(1).strip() if m else ""


class DryRunAIClient(AIClient):
    """AIClient that returns instant mock responses — no LLM calls, no API cost."""

    async def complete(
        self,
        system: str,
        user: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        if "deduplication" in system:
            return json.dumps({"duplicates": []})

        if "concepts" in system:
            return json.dumps({"queries": []})

        if "technical writer" in system:
            title = _extract_title(user)
            summary = _extract_summary(user) or title
            return json.dumps({
                "title_en": title,
                "title_zh": title,
                "whats_new_en": f"{title}.",
                "whats_new_zh": f"{title}。",
                "why_it_matters_en": "[dry-run]",
                "why_it_matters_zh": "[dry-run]",
                "key_details_en": "[dry-run]",
                "key_details_zh": "[dry-run]",
                "background_en": "",
                "background_zh": "",
                "community_discussion_en": "",
                "community_discussion_zh": "",
                "sources": [],
            })

        if "translator" in system.lower():
            title = _extract_title(user)
            summary = _extract_summary(user) or title
            return json.dumps({"title_zh": title, "summary_zh": summary})

        # Default: content analysis scoring
        title = _extract_title(user)
        return json.dumps({
            "score": 8.0,
            "reason": "[dry-run]",
            "summary": title,
            "tags": ["dry-run"],
        })
