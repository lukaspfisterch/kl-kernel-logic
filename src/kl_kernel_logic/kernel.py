"""
Deterministic execution kernel.

Receives a PsiDefinition, an optional PsiEnvelope and a callable task.
Executes the task once and returns a structured ExecutionTrace.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from time import perf_counter
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence
from uuid import uuid4

from .psi import PsiDefinition
from .psi_envelope import PsiEnvelope


@dataclass
class ExecutionTrace:
    """
    Single execution record.

    Captures:
      - logical intent (psi)
      - transport metadata (envelope)
      - outcome (success, output, error)
      - timing (started_at, finished_at, runtime_ms)
      - governance hooks (trace_id, parent_trace_id, policy_decisions)
      - free form metadata
    """

    psi: PsiDefinition
    envelope: PsiEnvelope

    success: bool
    output: Any
    error: Optional[str]

    started_at: str
    finished_at: str
    runtime_ms: float

    trace_id: str = field(default_factory=lambda: str(uuid4()))
    parent_trace_id: Optional[str] = None

    policy_decisions: List[Mapping[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def describe(self) -> Dict[str, Any]:
        """
        Serializable representation of the execution trace.

        Keys are stable and additive. Existing keys are not renamed.
        """
        return {
            "trace_id": self.trace_id,
            "parent_trace_id": self.parent_trace_id,
            "psi": self.psi.describe(),
            "envelope": self.envelope.describe(),
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "runtime_ms": self.runtime_ms,
            "policy_decisions": [dict(d) for d in self.policy_decisions],
            "metadata": dict(self.metadata),
        }


class Kernel:
    """
    Minimal execution engine.

    No policy logic.
    No orchestration.
    Only executes a callable once and returns an ExecutionTrace.
    """

    def execute(
        self,
        *,
        psi: PsiDefinition,
        task: Callable[..., Any],
        envelope: Optional[PsiEnvelope] = None,
        parent_trace_id: Optional[str] = None,
        policy_decisions: Optional[Sequence[Mapping[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> ExecutionTrace:
        """
        Execute a task under a given Psi and optional envelope.

        Exceptions are captured into ExecutionTrace.error and never bubble up.
        """

        # Ensure envelope exists
        env = envelope if envelope is not None else PsiEnvelope(psi=psi)

        # Normalise optional collections
        policy_list: List[Mapping[str, Any]] = (
            list(policy_decisions) if policy_decisions is not None else []
        )
        meta: Dict[str, Any] = dict(metadata) if metadata is not None else {}

        # RFC 3339 UTC timestamps
        started_dt = datetime.now(timezone.utc)
        started_at = started_dt.isoformat(timespec="milliseconds")
        t0 = perf_counter()

        success = False
        output: Any = None
        error_msg: Optional[str] = None

        try:
            output = task(**kwargs)
            success = True
        except Exception as exc:
            success = False
            error_msg = f"{exc.__class__.__name__}: {exc}"

        finished_dt = datetime.now(timezone.utc)
        finished_at = finished_dt.isoformat(timespec="milliseconds")
        runtime_ms = (perf_counter() - t0) * 1000.0

        return ExecutionTrace(
            psi=psi,
            envelope=env,
            success=success,
            output=output,
            error=error_msg,
            started_at=started_at,
            finished_at=finished_at,
            runtime_ms=runtime_ms,
            parent_trace_id=parent_trace_id,
            policy_decisions=policy_list,
            metadata=meta,
        )
