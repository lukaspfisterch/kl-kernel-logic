from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class PolicyDecision:
    """
    A single policy decision entry.

    It records:
    - policy_name: which policy evaluated the Psi
    - allowed: whether execution is allowed
    - reason: short human-readable explainability field
    - metadata: optional extra data
    """

    policy_name: str
    allowed: bool
    reason: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def describe(self) -> Dict[str, Any]:
        return {
            "policy_name": self.policy_name,
            "allowed": self.allowed,
            "reason": self.reason,
            "metadata": dict(self.metadata),
        }


class PolicyEngine:
    """
    Base policy engine interface for KL.

    Later versions can dispatch multiple policies, but KL 0.3.0
    only requires a single default policy.
    """

    def evaluate(self, psi) -> PolicyDecision:
        """
        Evaluate the PsiDefinition and return a PolicyDecision.

        Must be overridden by concrete implementations.
        """
        raise NotImplementedError


class DefaultSafePolicyEngine(PolicyEngine):
    """
    Minimal safe policy for KL 0.3.0.

    Rules:
    - effect="pure" is always allowed
    - effect="read" is allowed (configuration/lookup)
    - effect="io" is blocked
    - effect="external" is blocked
    - effect="ai" is allowed (but marked as nondeterministic placeholder)
    """

    def evaluate(self, psi) -> PolicyDecision:
        effect = psi.effect

        # Rule set
        if effect == "pure":
            return PolicyDecision(
                policy_name="default_safe",
                allowed=True,
                reason="pure operation",
            )

        if effect == "read":
            return PolicyDecision(
                policy_name="default_safe",
                allowed=True,
                reason="read-only operation",
            )

        if effect in {"io", "external"}:
            return PolicyDecision(
                policy_name="default_safe",
                allowed=False,
                reason=f"effect '{effect}' is not allowed under DefaultSafePolicyEngine",
            )

        if effect == "ai":
            return PolicyDecision(
                policy_name="default_safe",
                allowed=True,
                reason="ai operation (nondeterministic allowed placeholder)",
            )

        # Fallback
        return PolicyDecision(
            policy_name="default_safe",
            allowed=False,
            reason=f"unknown effect type '{effect}'",
        )
