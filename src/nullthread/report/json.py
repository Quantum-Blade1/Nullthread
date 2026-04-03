"""JSON report."""

from __future__ import annotations

import json
from typing import Any

from nullthread.models import AnalysisResult


def render_json(result: AnalysisResult) -> str:
    payload: dict[str, Any] = {
        "ptx_path": result.ptx_path,
        "kernels": result.kernel_names,
        "unsupported_notes": result.unsupported_notes,
        "findings": [],
    }
    for d in result.findings:
        f = d.finding
        payload["findings"].append(
            {
                "kind": f.kind.value,
                "severity": f.severity.value,
                "kernel": f.kernel_name,
                "line": f.line,
                "message": f.message,
                "evidence": f.evidence,
                "metadata": f.metadata,
                "diagnosis": {
                    "explanation": d.explanation,
                    "consequence": d.consequence,
                    "fix_suggestion": d.fix_suggestion,
                    "severity_rationale": d.severity_rationale,
                    "source": d.source,
                },
            }
        )
    return json.dumps(payload, indent=2)
