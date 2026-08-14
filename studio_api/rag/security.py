from __future__ import annotations

from dataclasses import dataclass


INJECTION_MARKERS = (
    "ignore previous instructions",
    "developer message",
    "system prompt",
    "exfiltrate",
    "disable safety",
    "call tool",
)


@dataclass(frozen=True)
class RagSecurityDecision:
    allowed: bool
    reason: str


def check_rag_request(prompt: str, *, enabled: bool = True) -> RagSecurityDecision:
    if not enabled:
        return RagSecurityDecision(False, "rag-kill-switch-disabled")
    lowered = prompt.lower()
    for marker in INJECTION_MARKERS:
        if marker in lowered:
            return RagSecurityDecision(False, f"prompt-injection-marker:{marker}")
    return RagSecurityDecision(True, "allowed")


def assert_same_tenant(request_tenant: str, chunk_tenant: str) -> RagSecurityDecision:
    if request_tenant != chunk_tenant:
        return RagSecurityDecision(False, "tenant-isolation-violation")
    return RagSecurityDecision(True, "allowed")
