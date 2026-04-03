"""Static template fallback per violation kind."""

from __future__ import annotations

from nullthread.models import Finding, ViolationKind


def template_diagnosis(f: Finding) -> dict[str, str]:
    k = f.kind
    if k == ViolationKind.RACE_CONDITION:
        return {
            "explanation": (
                "Shared memory may be written by one thread and read by another without a "
                "synchronizing barrier in between."
            ),
            "consequence": "Non-deterministic output depending on scheduling.",
            "fix_suggestion": "Insert a barrier (e.g. __syncthreads / bar.sync) between the write and dependent reads.",
            "severity_rationale": "Correctness risk — marked critical.",
        }
    if k == ViolationKind.BARRIER_IN_DIVERGENT_FLOW:
        return {
            "explanation": "A barrier appears only on some control-flow paths or under a predicate.",
            "consequence": "Undefined behavior per CUDA rules; possible deadlock or corruption.",
            "fix_suggestion": "Ensure all threads reach the same barrier, or restructure branches.",
            "severity_rationale": "Barriers must not be divergent — high severity.",
        }
    if k == ViolationKind.UNCOALESCED_ACCESS:
        return {
            "explanation": "Global loads may not coalesce into minimal transactions.",
            "consequence": "Reduced effective memory bandwidth.",
            "fix_suggestion": "Align accesses to contiguous indices per warp (often row-major).",
            "severity_rationale": "Performance impact — warning.",
        }
    if k == ViolationKind.OCCUPANCY_LIMIT:
        return {
            "explanation": "Register or shared memory usage may limit active warps.",
            "consequence": "Lower throughput if occupancy is the bottleneck.",
            "fix_suggestion": "Reduce registers (spill less / simplify), shrink shared usage, or tune launch.",
            "severity_rationale": "Depends on workload — informational.",
        }
    if k == ViolationKind.WARP_DIVERGENCE:
        return {
            "explanation": "Branching may depend on per-thread state.",
            "consequence": "Warp may serialize both sides of branches.",
            "fix_suggestion": "Move divergent decisions out of hot loops or use warp-level primitives where valid.",
            "severity_rationale": "Performance warning.",
        }
    return {
        "explanation": f"Finding: {f.message}",
        "consequence": "Review PTX evidence and kernel semantics.",
        "fix_suggestion": "Narrow the pattern and re-run analysis.",
        "severity_rationale": "Heuristic finding.",
    }
