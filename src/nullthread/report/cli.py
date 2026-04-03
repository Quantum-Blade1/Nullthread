"""Human-readable CLI report."""

from __future__ import annotations

from nullthread.models import AnalysisResult, Severity


def render_cli(result: AnalysisResult) -> str:
    lines: list[str] = []
    lines.append(f"File: {result.ptx_path}")
    lines.append(f"Kernels: {', '.join(result.kernel_names) or '(none)'}")
    if result.unsupported_notes:
        lines.append("")
        lines.append("[INFO] Unsupported / out-of-scope hints:")
        for n in result.unsupported_notes:
            lines.append(f"  - {n}")
    lines.append("")
    if not result.findings:
        lines.append("No issues reported by selected passes.")
        return "\n".join(lines)

    for d in result.findings:
        f = d.finding
        tag = _severity_tag(f.severity)
        loc = f"{f.kernel_name}:{f.line}"
        lines.append(f"{tag} {f.kind.value} at {loc}")
        lines.append(f"  {f.message}")
        lines.append(f"  Evidence:\n    {f.evidence.replace(chr(10), chr(10) + '    ')}")
        lines.append("  Diagnosis:")
        lines.append(f"    {d.explanation}")
        lines.append(f"    Consequence: {d.consequence}")
        lines.append(f"    Fix: {d.fix_suggestion}")
        lines.append(f"    (source: {d.source})")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _severity_tag(s: Severity) -> str:
    if s == Severity.CRITICAL:
        return "[CRITICAL]"
    if s == Severity.WARNING:
        return "[WARNING]"
    return "[INFO]"
