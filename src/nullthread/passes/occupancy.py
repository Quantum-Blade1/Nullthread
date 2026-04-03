"""Theoretical occupancy hints from PTX resource declarations."""

from __future__ import annotations

import re
from pathlib import Path

from nullthread.models import (
    ControlFlowGraph,
    Finding,
    ParsedPTX,
    Severity,
    SymbolTable,
    ViolationKind,
)

_REG_BRA = re.compile(r"\.reg\s+\.(\w+)\s+%\w+<(\d+)>", re.I)
_SHARED_BYTES = re.compile(r"\.shared\s+\.align\s+\d+\s+\.b\d+\s+\w+\[(\d+)\]", re.I)


def _parse_kernel_header_block(text: str, kernel_name: str) -> tuple[int, int]:
    """Extract approximate register count and shared bytes from PTX text for one kernel."""
    # Find .entry kernel_name ... { ... } — simplified: slice from entry to matching close
    idx = text.find(f".entry {kernel_name}")
    if idx < 0:
        idx = text.find(f".entry\t{kernel_name}")
    if idx < 0:
        return 0, 0
    sub = text[idx : idx + 8000]
    reg_total = 0
    for m in _REG_BRA.finditer(sub):
        count = int(m.group(2))
        reg_total += count
    shared = 0
    sm = _SHARED_BYTES.search(sub)
    if sm:
        shared = int(sm.group(1))
    return reg_total, shared


class OccupancyPass:
    name = "occupancy"

    def run(
        self,
        parsed: ParsedPTX,
        cfgs: dict[str, ControlFlowGraph],
        symtabs: dict[str, SymbolTable],
    ) -> list[Finding]:
        findings: list[Finding] = []
        raw_text = Path(parsed.path).read_text(encoding="utf-8", errors="replace")
        by_kernel: dict[str, list] = {k: [] for k in parsed.kernels}
        for ins in parsed.instructions:
            if ins.kernel_name and ins.kernel_name in by_kernel:
                by_kernel[ins.kernel_name].append(ins)

        for k in parsed.kernels:
            regs, smem = _parse_kernel_header_block(raw_text, k)
            insts = by_kernel.get(k) or []
            first_line = (
                min((i.location.source_line or i.location.ptx_line) for i in insts)
                if insts
                else 1
            )
            if regs >= 128:
                findings.append(
                    Finding(
                        kind=ViolationKind.OCCUPANCY_LIMIT,
                        severity=Severity.INFO,
                        kernel_name=k,
                        line=first_line,
                        message=f"High register pressure (approx {regs} scalar regs declared) may limit occupancy.",
                        evidence=f"regs~{regs}, shared_bytes~{smem}",
                        metadata={"approx_registers": regs, "shared_bytes": smem},
                    )
                )
            if smem >= 48000:
                findings.append(
                    Finding(
                        kind=ViolationKind.OCCUPANCY_LIMIT,
                        severity=Severity.WARNING,
                        kernel_name=k,
                        line=first_line,
                        message=f"Large static shared allocation ({smem} bytes) may limit occupancy.",
                        evidence=f"shared_bytes~{smem}",
                        metadata={"approx_registers": regs, "shared_bytes": smem},
                    )
                )
        return findings
