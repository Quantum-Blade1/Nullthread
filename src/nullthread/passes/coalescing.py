"""Global memory coalescing hints (heuristic)."""

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

_STRIDE = re.compile(r"\bmul\.(?:lo|wide)?\s+[^,]+,\s*[^,]+,\s*(\d+)", re.I)
_TID_IN_LD = re.compile(r"%tid|tid\.|threadIdx", re.I)


class CoalescingPass:
    name = "coalescing"

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
            for idx, ins in enumerate(insts):
                if ins.memory_space != MemorySpace.GLOBAL or not ins.is_read:
                    continue
                raw = ins.raw
                window = "\n".join(i.raw for i in insts[max(0, idx - 5) : idx + 1])
                m = _STRIDE.search(raw) or _STRIDE.search(window)
                stride = int(m.group(1)) if m else None
                tid_here = bool(_TID_IN_LD.search(raw))
                if not tid_here and (stride is None or stride < 4):
                    continue
                if stride is not None and stride < 4 and not tid_here:
                    continue
                line = ins.location.source_line or ins.location.ptx_line
                msg = (
                    f"Global load may be uncoalesced (stride hint: {stride})."
                    if stride is not None and stride >= 4
                    else "Global load uses thread-dependent addressing - verify warp coalescing."
                )
                findings.append(
                    Finding(
                        kind=ViolationKind.UNCOALESCED_ACCESS,
                        severity=Severity.WARNING,
                        kernel_name=kname,
                        line=line,
                        message=msg,
                        evidence=ins.raw,
                        metadata={
                            "ptx_line": ins.location.ptx_line,
                            "stride_hint": stride,
                            "thread_indexed": tid_here,
                        },
                    )
                )
        return findings
