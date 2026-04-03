"""Shared data models for IR, CFG, findings, and reports."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MemorySpace(str, Enum):
    GLOBAL = "global"
    SHARED = "shared"
    LOCAL = "local"
    REGISTER = "register"
    UNKNOWN = "unknown"


class Severity(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class ViolationKind(str, Enum):
    RACE_CONDITION = "RACE_CONDITION"
    BARRIER_IN_DIVERGENT_FLOW = "BARRIER_IN_DIVERGENT_FLOW"
    UNCOALESCED_ACCESS = "UNCOALESCED_ACCESS"
    OCCUPANCY_LIMIT = "OCCUPANCY_LIMIT"
    WARP_DIVERGENCE = "WARP_DIVERGENCE"
    UNSUPPORTED_FEATURE = "UNSUPPORTED_FEATURE"


@dataclass(frozen=True)
class SourceLocation:
    """Logical source line (from PTX .loc) or PTX line index."""

    ptx_line: int
    source_line: int | None = None


@dataclass
class Instruction:
    """One PTX instruction or directive line (normalized)."""

    opcode: str
    operands: str
    raw: str
    location: SourceLocation
    kernel_name: str | None
    is_barrier: bool = False
    is_branch: bool = False
    memory_space: MemorySpace | None = None
    is_write: bool = False
    is_read: bool = False


@dataclass
class BasicBlock:
    block_id: int
    instructions: list[Instruction] = field(default_factory=list)
    successors: list[int] = field(default_factory=list)
    predecessors: list[int] = field(default_factory=list)


@dataclass
class ControlFlowGraph:
    """Thread-annotated CFG for one kernel."""

    kernel_name: str
    blocks: list[BasicBlock]
    thread_index_hints: dict[str, str] = field(default_factory=dict)


@dataclass
class SymbolInfo:
    name: str
    space: MemorySpace
    dtype: str | None = None


@dataclass
class SymbolTable:
    """Per-kernel symbol table (simplified)."""

    kernel_name: str
    symbols: dict[str, SymbolInfo] = field(default_factory=dict)


@dataclass
class ParsedPTX:
    """Result of parsing a .ptx file."""

    path: str
    version: str | None
    target: str | None
    kernels: list[str]
    instructions: list[Instruction]
    loc_map: dict[int, int]  # ptx_line -> source line


@dataclass
class Finding:
    """Deterministic finding from an analysis pass."""

    kind: ViolationKind
    severity: Severity
    kernel_name: str
    line: int
    message: str
    evidence: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DiagnosedFinding:
    """Finding plus optional AI/template diagnosis."""

    finding: Finding
    explanation: str
    consequence: str
    fix_suggestion: str
    severity_rationale: str
    source: str  # "ai" | "template"


@dataclass
class AnalysisResult:
    """Full result of analyze()."""

    ptx_path: str
    findings: list[DiagnosedFinding]
    kernel_names: list[str]
    unsupported_notes: list[str] = field(default_factory=list)
