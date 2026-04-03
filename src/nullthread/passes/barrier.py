"""Detect barriers under divergence (predicated bar.sync)."""

from __future__ import annotations

import re

from nullthread.models import (
    ControlFlowGraph,
    Finding,
    ParsedPTX,
    Severity,
    SymbolTable,
    ViolationKind,
)

_PRED_BAR = re.compile(r"^\s*@\s*%?\w+\s+.*bar\.sync|barrier", re.I)


class BarrierPass:
    name = "barrier"

    def run(
        self,
        parsed: ParsedPTX,
        cfgs: dict[str, ControlFlowGraph],
        symtabs: dict[str, SymbolTable],
    ) -> list[Finding]:
        findings: list[Finding] = []
        for ins in parsed.instructions:
            if not ins.kernel_name:
                continue
            if not ins.is_barrier:
                continue
            raw = ins.raw.strip()
            if raw.startswith("@"):
                line = ins.location.source_line or ins.location.ptx_line
                findings.append(
                    Finding(
                        kind=ViolationKind.BARRIER_IN_DIVERGENT_FLOW,
                        severity=Severity.CRITICAL,
                        kernel_name=ins.kernel_name,
                        line=line,
                        message="Barrier appears predicated — possible divergent __syncthreads pattern.",
                        evidence=ins.raw,
                        metadata={"ptx_line": ins.location.ptx_line},
                    )
                )
            elif _PRED_BAR.match(ins.raw):
                line = ins.location.source_line or ins.location.ptx_line
                findings.append(
                    Finding(
                        kind=ViolationKind.BARRIER_IN_DIVERGENT_FLOW,
                        severity=Severity.WARNING,
                        kernel_name=ins.kernel_name,
                        line=line,
                        message="Barrier may be under divergent control flow (heuristic).",
                        evidence=ins.raw,
                        metadata={"ptx_line": ins.location.ptx_line},
                    )
                )
        return findings
