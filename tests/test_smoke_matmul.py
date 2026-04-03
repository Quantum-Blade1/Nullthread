"""Smoke tests on reference matmul.ptx."""

from __future__ import annotations

from pathlib import Path

from nullthread.analyze import analyze_ptx
from nullthread.models import ViolationKind

FIXTURE = Path(__file__).resolve().parent / "kernels" / "matmul.ptx"


def test_matmul_finds_race_and_coalescing() -> None:
    r = analyze_ptx(FIXTURE, use_ai=False, pass_names=["race", "coalescing"])
    kinds = {d.finding.kind for d in r.findings}
    assert ViolationKind.RACE_CONDITION in kinds
    assert ViolationKind.UNCOALESCED_ACCESS in kinds


def test_all_passes_run() -> None:
    r = analyze_ptx(FIXTURE, use_ai=False)
    kinds = {d.finding.kind for d in r.findings}
    assert ViolationKind.RACE_CONDITION in kinds
    assert ViolationKind.WARP_DIVERGENCE in kinds
    assert ViolationKind.OCCUPANCY_LIMIT in kinds
