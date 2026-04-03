"""Minimal PTX parser: kernels, instructions, .loc lines, basic opcode classification."""

from __future__ import annotations

import re
from pathlib import Path

from nullthread.models import (
    Instruction,
    MemorySpace,
    ParsedPTX,
    SourceLocation,
)

# Line comment
_COMMENT = re.compile(r"//.*$")

# .loc file_id line col ...  -> source line is second number (common PTX convention)
_LOC = re.compile(r"^\s*\.loc\s+(\d+)\s+(\d+)")

# .version X.Y
_VERSION = re.compile(r"^\s*\.version\s+(\S+)")

# .target name
_TARGET = re.compile(r"^\s*\.target\s+(\S+)")

# Kernel entry: .visible .entry name or .entry name
_ENTRY = re.compile(
    r"^\s*(?:\.visible\s+)?\.entry\s+([a-zA-Z_][a-zA-Z0-9_$]*)"
)

# Function (non-entry) — clears kernel context
_FUNC = re.compile(r"^\s*\.func\b")

# Unsupported markers (explicit report)
_COOP = re.compile(r"cooperative|cg::|cuda::", re.I)
_WARP = re.compile(r"shfl_|reduce_|vote\.|warp\.|__shfl", re.I)
_DYN = re.compile(r"cudaLaunchDevice|vprintf|dynamic", re.I)


def _strip_comment(line: str) -> str:
    return _COMMENT.sub("", line).strip()


def _classify_memory(opcode_lower: str) -> MemorySpace | None:
    if ".shared" in opcode_lower or opcode_lower.startswith("atom.shared"):
        return MemorySpace.SHARED
    if ".global" in opcode_lower or opcode_lower.startswith("atom.global"):
        return MemorySpace.GLOBAL
    if ".local" in opcode_lower:
        return MemorySpace.LOCAL
    return None


def _is_barrier(opcode_lower: str) -> bool:
    return "bar.sync" in opcode_lower or "barrier" in opcode_lower


def _is_branch(opcode_lower: str) -> bool:
    return opcode_lower.startswith("bra") or opcode_lower.startswith("call")


def _read_write_flags(opcode_lower: str) -> tuple[bool, bool]:
    is_write = opcode_lower.startswith("st.") or "st.shared" in opcode_lower or "st.global" in opcode_lower
    is_read = opcode_lower.startswith("ld.") or "ld.shared" in opcode_lower or "ld.global" in opcode_lower
    if "atom." in opcode_lower:
        is_read = is_write = True
    return is_read, is_write


def _first_opcode_token(line: str) -> str | None:
    """First token is treated as opcode (e.g. ld.shared.f32)."""
    line = line.strip()
    if not line or line.startswith("."):
        return None
    if line.startswith("{"):
        return None
    if line.startswith("}"):
        return None
    # Predicate @p ...
    if line.startswith("@"):
        # strip predicate: @%p1 ld.global...
        rest = line.lstrip("@")
        # skip predicate register until space
        m = re.match(r"^%?\w+\s+(.+)$", rest)
        if m:
            line = m.group(1).strip()
        else:
            return None
    # Split first token
    m = re.match(r"^([a-zA-Z_][a-zA-Z0-9_.]*)\s*(.*)$", line)
    if not m:
        return None
    return m.group(1)


def parse_ptx_file(path: str | Path) -> ParsedPTX:
    """Parse a PTX file into a flat instruction list with kernel association."""
    p = Path(path)
    text = p.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    version: str | None = None
    target: str | None = None
    kernels: list[str] = []
    instructions: list[Instruction] = []
    loc_map: dict[int, int] = {}

    active_kernel: str | None = None
    kernel_brace_depth = 0

    ptx_line_no = 0
    current_source_line: int | None = None

    for raw_line in lines:
        ptx_line_no += 1
        line = _strip_comment(raw_line)
        if not line:
            continue

        vm = _VERSION.match(line)
        if vm:
            version = vm.group(1)
            continue
        tm = _TARGET.match(line)
        if tm:
            target = tm.group(1)
            continue

        lm = _LOC.match(line)
        if lm:
            current_source_line = int(lm.group(2))
            loc_map[ptx_line_no] = current_source_line
            continue

        em = _ENTRY.search(line)
        if em:
            kn = em.group(1)
            if kn not in kernels:
                kernels.append(kn)
            active_kernel = kn
            kernel_brace_depth = 0
            continue

        if _FUNC.match(line) and ".entry" not in line:
            active_kernel = None
            kernel_brace_depth = 0
            continue

        if active_kernel:
            prev_depth = kernel_brace_depth
            kernel_brace_depth += line.count("{") - line.count("}")
            if kernel_brace_depth < 0:
                kernel_brace_depth = 0
            if prev_depth > 0 and kernel_brace_depth == 0:
                active_kernel = None

        opcode = _first_opcode_token(line)
        if opcode is None:
            continue

        opcode_lower = opcode.lower()
        loc = SourceLocation(ptx_line=ptx_line_no, source_line=current_source_line)
        mem = _classify_memory(opcode_lower)
        is_read, is_write = _read_write_flags(opcode_lower)

        in_kernel_body = bool(active_kernel and kernel_brace_depth > 0)
        instr = Instruction(
            opcode=opcode,
            operands=line.split(maxsplit=1)[1] if " " in line else "",
            raw=line,
            location=loc,
            kernel_name=active_kernel if in_kernel_body else None,
            is_barrier=_is_barrier(opcode_lower),
            is_branch=_is_branch(opcode_lower),
            memory_space=mem,
            is_write=is_write,
            is_read=is_read,
        )
        instructions.append(instr)

    return ParsedPTX(
        path=str(p),
        version=version,
        target=target,
        kernels=kernels,
        instructions=instructions,
        loc_map=loc_map,
    )


def scan_unsupported_features(text: str) -> list[str]:
    """Return human-readable notes for out-of-scope constructs (best-effort)."""
    notes: list[str] = []
    if _COOP.search(text):
        notes.append("Cooperative groups / CG API may be present — full support not implemented.")
    if _WARP.search(text):
        notes.append("Warp-level primitives may be present — analysis may be incomplete.")
    if _DYN.search(text):
        notes.append("Dynamic parallelism may be referenced — not supported.")
    return notes
