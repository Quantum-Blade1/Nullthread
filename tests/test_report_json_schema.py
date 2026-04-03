"""JSON report shape for CI consumers."""

from __future__ import annotations

import json
from pathlib import Path

from nullthread.analyze import analyze_ptx
from nullthread.report.json import render_json

FIXTURE = Path(__file__).resolve().parent / "kernels" / "matmul.ptx"


def test_json_has_expected_keys() -> None:
    r = analyze_ptx(FIXTURE, use_ai=False, pass_names=["race"])
    text = render_json(r)
    data = json.loads(text)
    assert "ptx_path" in data
    assert "kernels" in data
    assert "findings" in data
    assert "unsupported_notes" in data
    assert isinstance(data["findings"], list)
    if data["findings"]:
        f0 = data["findings"][0]
        for k in ("kind", "severity", "kernel", "line", "message", "evidence", "diagnosis"):
            assert k in f0
        d = f0["diagnosis"]
        for k in ("explanation", "consequence", "fix_suggestion", "severity_rationale", "source"):
            assert k in d
