"""Anthropic Messages API via httpx (optional dependency)."""

from __future__ import annotations

import json
import re
import time
from typing import Any

from nullthread.ai.prompts import STRICT_RETRY, SYSTEM_PROMPT, user_prompt_for_finding
from nullthread.models import Finding

_JSON_OBJECT = re.compile(r"\{[\s\S]*\}")


def _parse_json_loose(text: str) -> dict[str, Any] | None:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    m = _JSON_OBJECT.search(text)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            return None
    return None


def diagnose_with_anthropic(
    finding: Finding,
    *,
    api_key: str,
    model: str,
    timeout: float = 60.0,
) -> dict[str, str] | None:
    try:
        import httpx
    except ImportError:
        return None

    user = user_prompt_for_finding(
        finding.kind.value,
        finding.kernel_name,
        finding.line,
        finding.evidence,
    )

    def call(user_content: str) -> dict[str, str] | None:
        payload = {
            "model": model,
            "max_tokens": 1024,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": user_content}],
        }
        r = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json=payload,
            timeout=timeout,
        )
        r.raise_for_status()
        data = r.json()
        parts = data.get("content") or []
        text = "".join(p.get("text", "") for p in parts if isinstance(p, dict))
        obj = _parse_json_loose(text)
        if not obj:
            return None
        keys = ("explanation", "consequence", "fix_suggestion", "severity_rationale")
        if not all(k in obj for k in keys):
            return None
        return {k: str(obj[k]) for k in keys}

    for attempt in range(3):
        out = call(user if attempt == 0 else STRICT_RETRY + "\n\n" + user)
        if out:
            return out
        time.sleep(0.5 * (2**attempt))
    return None
