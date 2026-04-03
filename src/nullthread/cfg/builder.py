"""Build basic blocks and thread-index hints from parsed PTX."""

from __future__ import annotations

import re

from nullthread.models import BasicBlock, ControlFlowGraph, Instruction, ParsedPTX, SymbolTable

# tid.x / %tid.x / ctaid.x
_TID = re.compile(r"%tid\.[xyz]|tid\.[xyz]", re.I)
_CTAID = re.compile(r"%ctaid\.[xyz]|ctaid\.[xyz]", re.I)


def _extract_thread_hints(instructions: list[Instruction]) -> dict[str, str]:
    hints: dict[str, str] = {}
    for ins in instructions:
        if "mov" in ins.opcode.lower() and _TID.search(ins.raw):
            hints[f"ptx_{ins.location.ptx_line}"] = "thread_index"
        if _CTAID.search(ins.raw):
            hints[f"ptx_{ins.location.ptx_line}"] = "block_index"
    return hints


def _split_blocks(instructions: list[Instruction]) -> list[BasicBlock]:
    """Split on branches and labels (heuristic)."""
    if not instructions:
        return [BasicBlock(block_id=0)]

    blocks: list[BasicBlock] = []
    current: list[Instruction] = []
    bid = 0

    def flush() -> None:
        nonlocal bid, current
        if current:
            blocks.append(BasicBlock(block_id=bid, instructions=current))
            bid += 1
            current = []

    for ins in instructions:
        # Start new block after branch or at label-like position
        if ins.is_branch and current:
            flush()
        current.append(ins)
        if ins.is_branch:
            flush()

    if current:
        flush()

    if not blocks:
        blocks = [BasicBlock(block_id=0)]

    # Sequential successors
    for i, b in enumerate(blocks):
        if i + 1 < len(blocks):
            b.successors.append(blocks[i + 1].block_id)
            blocks[i + 1].predecessors.append(b.block_id)

    return blocks


def build_cfg_for_kernels(
    parsed: ParsedPTX,
) -> tuple[dict[str, ControlFlowGraph], dict[str, SymbolTable]]:
    """One CFG per kernel; symbol tables are minimal placeholders for extension."""
    by_kernel: dict[str, list[Instruction]] = {k: [] for k in parsed.kernels}
    for ins in parsed.instructions:
        if ins.kernel_name and ins.kernel_name in by_kernel:
            by_kernel[ins.kernel_name].append(ins)

    cfgs: dict[str, ControlFlowGraph] = {}
    symtabs: dict[str, SymbolTable] = {}

    for kname, insts in by_kernel.items():
        hints = _extract_thread_hints(insts)
        blocks = _split_blocks(insts)
        cfgs[kname] = ControlFlowGraph(kernel_name=kname, blocks=blocks, thread_index_hints=hints)
        symtabs[kname] = SymbolTable(kernel_name=kname, symbols={})

    return cfgs, symtabs
