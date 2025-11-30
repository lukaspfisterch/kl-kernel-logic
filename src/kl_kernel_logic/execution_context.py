"""
Execution context and per-request policy flags.

The context attaches identity and lightweight execution policy
to a single CAEL/Kernel run.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class ExecutionPolicy:
    """
    Minimal per-request policy flags.

    These flags can be inspected by PolicyEngine implementations or
    by CAEL to derive execution behavior (for example timeouts).
    """

    allow_network: bool = False
    allow_filesystem: bool = False
    timeout_seconds: Optional[float] = None

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize policy to a plain dict for logging or transport.
        """
        return {
            "allow_network": self.allow_network,
            "allow_filesystem": self.allow_filesystem,
            "timeout_seconds": self.timeout_seconds,
            "metadata": dict(self.metadata),
        }

    @staticmethod
    def from_dict(data: Optional[Dict[str, Any]]) -> "ExecutionPolicy":
        """
        Rebuild an ExecutionPolicy from a dict representation.

        If data is None, a default policy is returned.
        """
        if data is None:
            return ExecutionPolicy()

        return ExecutionPolicy(
            allow_network=bool(data.get("allow_network", False)),
            allow_filesystem=bool(data.get("allow_filesystem", False)),
            timeout_seconds=data.get("timeout_seconds"),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass
class ExecutionContext:
    """
    Execution context for a single request.

    Carries:
      - user_id: logical identity of the caller
      - request_id: id for correlation and tracing
      - policy: optional ExecutionPolicy (per-request overrides)
      - metadata: free-form context information
    """

    user_id: str
    request_id: str

    policy: Optional[ExecutionPolicy] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def policy_or_default(self) -> ExecutionPolicy:
        """
        Return the attached policy or a default instance.

        This is safe to call from CAEL and policy adapters without
        needing to check for None.
        """
        if self.policy is not None:
            return self.policy
        return ExecutionPolicy()

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the context to a dict for logging or transport.
        """
        return {
            "user_id": self.user_id,
            "request_id": self.request_id,
            "policy": self.policy.to_dict() if self.policy is not None else None,
            "metadata": dict(self.metadata),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ExecutionContext":
        """
        Rebuild an ExecutionContext from a dict representation.
        """
        policy_data = data.get("policy")
        policy = (
            ExecutionPolicy.from_dict(policy_data) if policy_data is not None else None
        )

        return ExecutionContext(
            user_id=str(data["user_id"]),
            request_id=str(data["request_id"]),
            policy=policy,
            metadata=dict(data.get("metadata", {})),
        )
