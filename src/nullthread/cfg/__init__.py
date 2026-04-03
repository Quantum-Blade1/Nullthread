"""Thread-annotated CFG construction."""

from nullthread.cfg.builder import build_cfg_for_kernels
from nullthread.cfg.graph import ControlFlowGraph

__all__ = ["build_cfg_for_kernels", "ControlFlowGraph"]
