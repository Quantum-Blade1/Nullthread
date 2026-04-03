"""Race condition detection on shared memory (conservative)."""

from __future__ import annotations

import re

from nullthread.models import (
    ControlFlowGraph,
    Finding,
    MemorySpace,
    ParsedPTX,
    Severity,
    SymbolTable,
    ViolationKind,
)

# Operand that looks like shared address register
_ADDR = re.compile(r"\[(%[a-zA-Z0-9_]+)\]")


def _addr_reg_from_st(raw: str) -> str | None:
    m = _ADDR.search(raw)
    return m.group(1) if m else None


class RacePass:
    name = "race"

    def run(
        self,
        parsed: ParsedPTX,
        cfgs: dict[str, ControlFlowGraph],
        symtabs: dict[str, SymbolTable],
    ) -> list[Finding]:
        findings: list[Finding] = []
        by_kernel: dict[str, list] = {k: [] for k in parsed.kernels}
        for ins in parsed.instructions:
            if ins.kernel_name and ins.kernel_name in by_kernel:
                by_kernel[ins.kernel_name].append(ins)

        for kname, insts in by_kernel.items():
            i = 0
            while i < len(insts):
                ins = insts[i]
                op_low = ins.opcode.lower()
                if ins.memory_space == MemorySpace.SHARED and ins.is_write and "st." in op_low:
                    addr = _addr_reg_from_st(ins.raw)
                    write_line = ins.location.source_line or ins.location.ptx_line
                    j = i + 1
                    while j < len(insts):
                        n = insts[j]
                        n_low = n.opcode.lower()
                        if n.is_barrier:
                            break
                        if (
                            n.memory_space == MemorySpace.SHARED
                            and n.is_read
                            and "ld." in n_low
                            and addr
                            and addr in n.raw
                        ):
                            read_line = n.location.source_line or n.location.ptx_line
                            findings.append(
                                Finding(
                                    kind=ViolationKind.RACE_CONDITION,
                                    severity=Severity.CRITICAL,
                                    kernel_name=kname,
                                    line=write_line,
                                    message=(
                                        "Possible shared-memory race: read may observe write "
                                        "without intervening barrier."
                                    ),
                                    evidence=f"Write: {ins.raw}\nRead: {n.raw}",
                                    metadata={
                                        "write_ptx_line": ins.location.ptx_line,
                                        "read_ptx_line": n.location.ptx_line,
                                        "read_line": read_line,
                                    },
                                )
                            )
                            break
                        j += 1
                i += 1

        return findings
