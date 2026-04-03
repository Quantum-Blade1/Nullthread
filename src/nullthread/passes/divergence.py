"""Warp divergence hints: branches depending on thread indices."""

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

_TID = re.compile(r"%tid\.[xyz]|%laneid|%warpid", re.I)
_SETP = re.compile(r"^\s*setp", re.I)
_BRA = re.compile(r"^\s*@.*\bbra\b", re.I)


class DivergencePass:
    name = "divergence"

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
            if not _SETP.match(ins.raw) and not _BRA.match(ins.raw):
                continue
            if not _TID.search(ins.raw):
                continue
            line = ins.location.source_line or ins.location.ptx_line
            findings.append(
                Finding(
                    kind=ViolationKind.WARP_DIVERGENCE,
                    severity=Severity.WARNING,
                    kernel_name=ins.kernel_name,
                    line=line,
                    message="Control flow may depend on thread/lane id — possible warp divergence.",
                    evidence=ins.raw,
                    metadata={"ptx_line": ins.location.ptx_line},
                )
            )
        return findings
