"""Strict JSON prompts for LLM diagnosis."""

SYSTEM_PROMPT = """You are a senior GPU compiler engineer specializing in CUDA correctness and performance.
Respond ONLY with a single JSON object and no markdown, with exactly these keys:
"explanation", "consequence", "fix_suggestion", "severity_rationale".
"""


def user_prompt_for_finding(violation_type: str, kernel: str, line: int, ptx_evidence: str) -> str:
    return (
        f"Violation: {violation_type} at kernel {kernel} line {line}\n"
        f"PTX evidence:\n{ptx_evidence}\n"
        "Explain for a kernel author; be specific to this evidence."
    )


STRICT_RETRY = (
    "Your previous reply was invalid. Respond with ONLY one JSON object, keys: "
    "explanation, consequence, fix_suggestion, severity_rationale. No markdown, no preamble."
)
