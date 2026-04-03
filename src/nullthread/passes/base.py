"""Pass protocol."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from nullthread.models import ControlFlowGraph, Finding, ParsedPTX, SymbolTable

if TYPE_CHECKING:
    pass


class AnalysisPass(Protocol):
    name: str

    def run(
        self,
        parsed: ParsedPTX,
        cfgs: dict[str, ControlFlowGraph],
        symtabs: dict[str, SymbolTable],
    ) -> list[Finding]: ...

