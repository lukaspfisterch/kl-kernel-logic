"""
CAEL Layer

Controlled AI Execution Layer.
Defines how an operation is carried out with policy, guardrails,
and a minimal trace.
"""

from dataclasses import dataclass
from typing import Callable, Any, Dict, Optional, List


@dataclass
class ExecutionPolicy:
    """
    Technical guardrails for the execution.
    """

    allow_network: bool = False
    allow_filesystem: bool = False
    max_tokens: Optional[int] = None
    timeout_seconds: Optional[int] = None


@dataclass
class ExecutionContext:
    """
    Context for a single execution path.
    """

    user_id: str
    request_id: str
    policy: ExecutionPolicy


class CAELExecutor:
    """
    Minimal executor that applies policy checks and keeps a trace.
    """

    def __init__(self) -> None:
        self.trace_log: List[Dict[str, Any]] = []

    def run(self, task: Callable[..., Any], ctx: ExecutionContext, **kwargs) -> Dict[str, Any]:
        """
        Execute a callable under a given execution context.

        The task receives only the functional parameters.
        Control flags like needs_network are handled by CAEL.
        """
        # Reset trace per execution to avoid leaking entries across runs.
        self.trace_log = []
        self._trace("start", ctx, kwargs)

        if not ctx.policy.allow_network and kwargs.get("needs_network"):
            self._trace("error", ctx, {"error": "network access forbidden"})
            raise PermissionError("Operation requires network access but policy forbids it")

        if not ctx.policy.allow_filesystem and kwargs.get("needs_fs"):
            self._trace("error", ctx, {"error": "filesystem access forbidden"})
            raise PermissionError("Operation requires filesystem access but policy forbids it")

        # Remove control flags before calling the task
        safe_kwargs = {
            key: value
            for key, value in kwargs.items()
            if key not in {"needs_network", "needs_fs"}
        }

        try:
            result = task(**safe_kwargs)
        except Exception as exc:  # pragma: no cover - bubbled but traced
            self._trace("error", ctx, {"error": type(exc).__name__})
            raise

        self._trace("end", ctx, {"result_type": type(result).__name__})
        return {"result": result, "trace": list(self.trace_log)}

    def _trace(self, stage: str, ctx: ExecutionContext, extra: Optional[Dict[str, Any]] = None) -> None:
        entry: Dict[str, Any] = {
            "stage": stage,
            "user_id": ctx.user_id,
            "request_id": ctx.request_id,
        }
        if extra:
            entry["extra"] = extra
        self.trace_log.append(entry)
