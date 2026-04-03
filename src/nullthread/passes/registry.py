"""Pass registry and parallel execution."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed

from nullthread.models import ControlFlowGraph, Finding, ParsedPTX, SymbolTable
from nullthread.passes.barrier import BarrierPass
from nullthread.passes.coalescing import CoalescingPass
from nullthread.passes.divergence import DivergencePass
from nullthread.passes.occupancy import OccupancyPass
from nullthread.passes.race import RacePass

PASS_NAMES = ("race", "barrier", "coalescing", "occupancy", "divergence")


def get_pass(name: str):
    m = {
        "race": RacePass(),
        "barrier": BarrierPass(),
        "coalescing": CoalescingPass(),
        "occupancy": OccupancyPass(),
        "divergence": DivergencePass(),
    }
    if name not in m:
        raise ValueError(f"Unknown pass: {name}. Choose from {PASS_NAMES}")
    return m[name]


def run_passes(
    names: list[str],
    parsed: ParsedPTX,
    cfgs: dict[str, ControlFlowGraph],
    symtabs: dict[str, SymbolTable],
    max_workers: int | None = None,
) -> list[Finding]:
    """Run selected passes (parallel by default)."""
    if not names:
        return []
    findings: list[Finding] = []
    with ThreadPoolExecutor(max_workers=max_workers or min(8, len(names))) as ex:
        futs = {ex.submit(get_pass(n).run, parsed, cfgs, symtabs): n for n in names}
        for fut in as_completed(futs):
            findings.extend(fut.result())
    return findings
