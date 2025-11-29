"""
CAEL - Constraint And Execution Layer

Thin wrapper around the Kernel for validating Psi, evaluating policies
and managing envelopes.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional

from .psi import PsiDefinition
from .psi_envelope import PsiEnvelope
from .execution_context import ExecutionContext
from .kernel import Kernel, ExecutionTrace
from .policy import PolicyEngine, DefaultSafePolicyEngine


class PolicyViolationError(Exception):
    """
    Raised when CAEL blocks execution due to a policy decision.
    
    This replaces the old PolicyViolation exception.
    """
    
    def __init__(self, message: str, policy_name: str, reason: str) -> None:
        super().__init__(message)
        self.message = message
        self.policy_name = policy_name
        self.reason = reason
    
    def __str__(self) -> str:
        return f"{self.message} (policy={self.policy_name}, reason={self.reason})"


@dataclass(frozen=True)
class CAELConfig:
    """
    Static configuration for CAEL.

    Kept intentionally small for the core library.
    """

    default_version: str = "1.0"
    enforce_envelope: bool = False
    # Policy engine for pre-execution evaluation (defaults to DefaultSafePolicyEngine)
    policy_engine: Optional[PolicyEngine] = None
    # Optional default timeout applied when no per-call override or ctx policy present
    default_timeout_seconds: Optional[int] = None


class CAEL:
    """
    Minimal CAEL implementation.

    Responsibilities:
    - basic Psi validation hook
    - policy evaluation before execution via PolicyEngine
    - envelope creation or enrichment
    - delegation to Kernel
    """

    def __init__(self, kernel: Optional[Kernel] = None, config: Optional[CAELConfig] = None) -> None:
        self.kernel = kernel or Kernel()
        self.config = config or CAELConfig()
        # Use DefaultSafePolicyEngine if none provided
        self.policy_engine = self.config.policy_engine or DefaultSafePolicyEngine()

    def execute(
        self,
        psi: PsiDefinition,
        task: Callable[..., Any],
        *,
        envelope: Optional[PsiEnvelope] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ctx: Optional[ExecutionContext] = None,
        **kwargs: Any,
    ) -> ExecutionTrace:
        # 1) validation hook
        self._validate_psi(psi)

        # 2) policy evaluation via PolicyEngine
        decision = self.policy_engine.evaluate(psi)
        if not decision.allowed:
            raise PolicyViolationError(
                message="Execution blocked by policy",
                policy_name=decision.policy_name,
                reason=decision.reason,
            )

        # Legacy per-call control flags adapter (backwards compatibility)
        # If callers pass explicit flags like `needs_fs` or `needs_network`,
        # honour them against the provided ExecutionContext.policy where available
        if ctx is not None:
            if kwargs.get("needs_network") and not ctx.policy.allow_network:
                raise PolicyViolationError(
                    message="Operation requires network access but policy forbids it",
                    policy_name="execution_context",
                    reason="needs_network flag set but allow_network=False"
                )
            if kwargs.get("needs_fs") and not ctx.policy.allow_filesystem:
                raise PolicyViolationError(
                    message="Operation requires filesystem access but policy forbids it",
                    policy_name="execution_context",
                    reason="needs_fs flag set but allow_filesystem=False"
                )

        # 3) context metadata
        ctx_meta: Dict[str, Any] = {}
        if ctx is not None:
            ctx_meta = {
                "user_id": ctx.user_id,
                "request_id": ctx.request_id,
                "policy": {
                    "allow_network": ctx.policy.allow_network,
                    "allow_filesystem": ctx.policy.allow_filesystem,
                    "timeout_seconds": ctx.policy.timeout_seconds,
                    "max_tokens": ctx.policy.max_tokens,
                },
            }

        combined_meta: Dict[str, Any] = {}
        if metadata:
            combined_meta.update(metadata)
        if ctx_meta:
            combined_meta.update(ctx_meta)

        # 4) envelope handling
        if envelope is None:
            envelope = PsiEnvelope(
                psi=psi,
                version=self.config.default_version,
                metadata=combined_meta or None,
            )
        elif combined_meta:
            merged = dict(envelope.metadata or {})
            merged.update(combined_meta)
            envelope = PsiEnvelope(
                psi=envelope.psi,
                version=envelope.version,
                envelope_id=envelope.envelope_id,
                timestamp=envelope.timestamp,
                metadata=merged,
                signature=envelope.signature,
            )

        # 5) delegate to kernel
        # Determine timeout precedence (highest -> lowest):
        #  - explicit per-call kwarg `timeout_seconds`
        #  - ExecutionContext.policy.timeout_seconds (per-request)
        #  - CAELConfig.default_timeout_seconds (global default)
        timeout = None
        # allow explicit per-call override
        if "timeout_seconds" in kwargs:
            timeout = kwargs.pop("timeout_seconds")
        if timeout is None and ctx is not None:
            timeout = ctx.policy.timeout_seconds
        if timeout is None:
            timeout = self.config.default_timeout_seconds

        trace = self.kernel.execute(psi=psi, task=task, envelope=envelope, timeout_seconds=timeout, **kwargs)
        return trace

    def _validate_psi(self, psi: PsiDefinition) -> None:
        """
        Hook for structural or policy based Psi validation.

        Left intentionally as a no-op in the core package and can be
        extended in higher level integrations.
        """
        return


__all__ = ["CAELConfig", "CAEL", "PolicyViolationError"]
