"""
Controlled AI Execution Layer (CAEL).

Bridges Psi + Kernel with policy evaluation and optional context handling.
"""

from dataclasses import dataclass
from typing import Any, Callable, Optional

from .kernel import Kernel, ExecutionTrace
from .psi import PsiDefinition
from .psi_envelope import PsiEnvelope
from .execution_context import ExecutionContext
from .policy import PolicyEngine, DefaultSafePolicyEngine, PolicyDecision


class PolicyViolationError(Exception):
    """
    Raised when a policy engine denies execution of a PsiDefinition.
    """

    def __init__(self, policy_name: str, reason: str) -> None:
        super().__init__(f"{policy_name}: {reason}")
        self.policy_name = policy_name
        self.reason = reason


@dataclass
class CAELConfig:
    """
    Configuration for CAEL.

    Currently:
      - policy_engine: strategy for policy evaluation
      - envelope_version: version string for new PsiEnvelope instances
    """

    policy_engine: PolicyEngine = DefaultSafePolicyEngine()
    envelope_version: str = "1.0"


class CAEL:
    """
    Controlled execution entry point.

    Responsibilities:
      - evaluate policies before execution
      - construct / reuse PsiEnvelope
      - delegate to Kernel
      - apply simple timeout classification based on ExecutionContext.policy
    """

    def __init__(
        self,
        config: Optional[CAELConfig] = None,
        kernel: Optional[Kernel] = None,
    ) -> None:
        self.config = config or CAELConfig()
        self.kernel = kernel or Kernel()

    def execute(
        self,
        psi: PsiDefinition,
        task: Callable[..., Any],
        ctx: Optional[ExecutionContext] = None,
        envelope: Optional[PsiEnvelope] = None,
        **kwargs: Any,
    ) -> ExecutionTrace:
        """
        Execute a task under the KL model.

        Steps:
          1. Policy evaluation (may raise PolicyViolationError)
          2. Envelope construction (if not provided)
          3. Kernel execution
          4. Attach policy decision to trace
          5. Classify timeouts based on ExecutionContext.policy.timeout_seconds
        """

        # 1. Policy evaluation
        decision: Optional[PolicyDecision] = None
        if self.config.policy_engine is not None:
            decision = self.config.policy_engine.evaluate(psi)
            if not decision.allowed:
                raise PolicyViolationError(
                    decision.policy_name,
                    decision.reason or "policy denied execution",
                )

        # 2. Envelope construction
        env = envelope or PsiEnvelope(
            psi=psi,
            version=self.config.envelope_version,
        )

        # 3. Kernel execution (no policy kwargs forwarded to task)
        trace = self.kernel.execute(
            psi=psi,
            task=task,
            envelope=env,
            **kwargs,
        )

        # 4. Attach policy decision to trace (if available)
        if decision is not None:
            trace.policy_decisions.append(
                {
                    "policy_name": decision.policy_name,
                    "allowed": decision.allowed,
                    "reason": decision.reason,
                }
            )
            # Set policy result summary for easier audit/logging
            trace.policy_result = "allow" if decision.allowed else "block"

        # 5. Timeout classification (post-hoc, based on measured runtime)
        timeout_seconds: Optional[float] = None
        if ctx is not None and ctx.policy is not None:
            timeout_seconds = ctx.policy.timeout_seconds

        if (
            timeout_seconds is not None
            and trace.runtime_ms is not None
            and trace.runtime_ms > timeout_seconds * 1000.0
        ):
            timeout_message = (
                f"TimeoutError: execution exceeded {timeout_seconds} seconds"
            )
            if trace.error:
                trace.error = f"{timeout_message}; original error: {trace.error}"
            else:
                trace.error = timeout_message
            trace.success = False
            trace.policy_result = "timeout"  # Mark as timeout violation

        return trace
