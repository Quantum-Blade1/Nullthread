"""Orchestrate parse → CFG → passes → diagnosis → report."""

from __future__ import annotations

from pathlib import Path

from nullthread.ai.config import AISettings
from nullthread.ai.diagnose import diagnose_findings
from nullthread.cfg.builder import build_cfg_for_kernels
from nullthread.models import AnalysisResult
from nullthread.parser.ptx import parse_ptx_file, scan_unsupported_features
from nullthread.passes.registry import PASS_NAMES, run_passes


def analyze_ptx(
    ptx_path: str | Path,
    *,
    pass_names: list[str] | None = None,
    use_ai: bool = True,
    ai_settings: AISettings | None = None,
    cache_root: Path | None = None,
) -> AnalysisResult:
    """Run full pipeline on a PTX file."""
    path = Path(ptx_path)
    text = path.read_text(encoding="utf-8", errors="replace")
    unsupported = scan_unsupported_features(text)

    parsed = parse_ptx_file(path)
    cfgs, symtabs = build_cfg_for_kernels(parsed)

    names = list(pass_names) if pass_names is not None else list(PASS_NAMES)
    findings = run_passes(names, parsed, cfgs, symtabs)

    settings = ai_settings or AISettings()
    diagnosed = diagnose_findings(findings, use_ai=use_ai, settings=settings, cache_root=cache_root)

    return AnalysisResult(
        ptx_path=str(path.resolve()),
        findings=diagnosed,
        kernel_names=list(parsed.kernels),
        unsupported_notes=unsupported,
    )
