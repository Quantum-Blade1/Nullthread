"""Parallel diagnosis with cache + template fallback."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from nullthread.ai.anthropic_backend import diagnose_with_anthropic
from nullthread.ai.cache import load_cache, save_cache
from nullthread.ai.config import AISettings
from nullthread.ai.templates import template_diagnosis
from nullthread.models import DiagnosedFinding, Finding


def _one(
    f: Finding,
    settings: AISettings,
    use_ai: bool,
    cache_root: Path | None,
) -> DiagnosedFinding:
    cache_dir = cache_root / "ai_cache" if cache_root else None
    if cache_dir and use_ai:
        cached = load_cache(cache_dir, f)
        if cached and all(k in cached for k in ("explanation", "consequence", "fix_suggestion", "severity_rationale")):
            return DiagnosedFinding(
                finding=f,
                explanation=cached["explanation"],
                consequence=cached["consequence"],
                fix_suggestion=cached["fix_suggestion"],
                severity_rationale=cached["severity_rationale"],
                source="ai",
            )

    if use_ai and settings.api_key and settings.backend.lower() == "anthropic":
        ai = diagnose_with_anthropic(f, api_key=settings.api_key, model=settings.llm_model)
        if ai and cache_dir:
            save_cache(cache_dir, f, ai)
        if ai:
            return DiagnosedFinding(
                finding=f,
                explanation=ai["explanation"],
                consequence=ai["consequence"],
                fix_suggestion=ai["fix_suggestion"],
                severity_rationale=ai["severity_rationale"],
                source="ai",
            )

    t = template_diagnosis(f)
    return DiagnosedFinding(
        finding=f,
        explanation=t["explanation"],
        consequence=t["consequence"],
        fix_suggestion=t["fix_suggestion"],
        severity_rationale=t["severity_rationale"],
        source="template",
    )


def diagnose_findings(
    findings: list[Finding],
    *,
    use_ai: bool,
    settings: AISettings | None = None,
    cache_root: Path | None = None,
    max_workers: int = 8,
) -> list[DiagnosedFinding]:
    settings = settings or AISettings()
    if not findings:
        return []
    out: list[DiagnosedFinding] = []
    with ThreadPoolExecutor(max_workers=min(max_workers, len(findings))) as ex:
        futs = {ex.submit(_one, f, settings, use_ai, cache_root): f for f in findings}
        for fut in as_completed(futs):
            out.append(fut.result())
    # Stable sort by severity then line
    order = {"critical": 0, "warning": 1, "info": 2}
    out.sort(key=lambda d: (order.get(d.finding.severity.value, 9), d.finding.line, d.finding.kind.value))
    return out
