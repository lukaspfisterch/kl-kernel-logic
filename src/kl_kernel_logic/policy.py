"""
Policy system for KL Kernel Logic.

Minimal interface + default policy implementation.
"""

from dataclasses import dataclass
from typing import Optional

from .psi import PsiDefinition


@dataclass
class PolicyDecision:
    """
    Result of a policy evaluation for a given PsiDefinition.
    """

    policy_name: str
    allowed: bool
    reason: Optional[str] = None


class PolicyEngine:
    """
    Abstract policy evaluation interface.

    Implementations decide whether a given PsiDefinition is allowed to execute.
    """

    def evaluate(self, psi: PsiDefinition) -> PolicyDecision:
        raise NotImplementedError("PolicyEngine.evaluate() must be implemented")


class DefaultSafePolicyEngine(PolicyEngine):
    """
    Effect-based default policy.

    Semantics:
      - allow:   effect in {"pure", "read", "ai"}
      - deny:    effect in {"io", "external"} or anything else
    """

    def evaluate(self, psi: PsiDefinition) -> PolicyDecision:
        effect = (psi.effect or "").strip().lower()
        # Stable, test-friendly policy name
        policy_name = "default_safe_policy"

        if effect in {"pure", "read", "ai"}:
            return PolicyDecision(
                policy_name=policy_name,
                allowed=True,
                reason=f"effect '{effect}' is allowed under {policy_name}",
            )

        # Block everything else (including "io" and "external")
        return PolicyDecision(
            policy_name=policy_name,
            allowed=False,
            reason=f"effect '{effect}' is not allowed under {policy_name}",
        )
