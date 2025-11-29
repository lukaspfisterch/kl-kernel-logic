"""
Kernel

Executes operations under the KL model and produces execution traces.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional, List
from uuid import uuid4
import multiprocessing

from .psi import PsiDefinition
from .psi_envelope import PsiEnvelope


def _utc_timestamp() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


# Top-level worker to make multiprocessing spawn-safe on Windows
def _kernel_worker(q, func, kwargs):
    try:
        res = func(**kwargs)
        q.put(("ok", res))
    except Exception as e:
        q.put(("err", (type(e).__name__, str(e))))


@dataclass(frozen=True)
class ExecutionTrace:
    """
    Immutable record of a single execution.

    Fields:
    - psi: PsiDefinition that was executed
    - envelope: PsiEnvelope used for this run
    - success: True if the task completed without raising
    - output: return value from the task (if any)
    - error: textual representation of the error (if any)
    - started_at: UTC timestamp when execution started
    - finished_at: UTC timestamp when execution finished
    - metadata: optional execution level metadata

    KL 0.3.0 extensions:
    - trace_id: globally unique identifier for this execution
    - parent_trace_id: optional parent trace id for orchestrated runs
    - policy_decisions: list of policy-related information attached by CAEL
    - runtime_ms: optional runtime in milliseconds (may be None)
    """

    psi: PsiDefinition
    envelope: PsiEnvelope
    success: bool
    output: Any
    error: Optional[str]
    started_at: str
    finished_at: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    # KL 0.3.0 additions
    trace_id: str = field(default_factory=lambda: str(uuid4()))
    parent_trace_id: Optional[str] = None
    policy_decisions: List[Dict[str, Any]] = field(default_factory=list)
    runtime_ms: Optional[float] = None

    def describe(self) -> Dict[str, Any]:
        """
        Serialisable representation of the execution trace.

        Existing keys are preserved for backwards compatibility.
        New fields are additive.
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
    Minimal execution kernel.

    It does not apply policies or scheduling. It is responsible for:
    - calling the task
    - capturing timing
    - packaging everything into an ExecutionTrace
    """

    def execute(
        self,
        psi: PsiDefinition,
        task: Callable[..., Any],
        *,
        envelope: Optional[PsiEnvelope] = None,
        timeout_seconds: Optional[int] = None,
        **kwargs: Any,
    ) -> ExecutionTrace:
        """Execute a task and return an ExecutionTrace.

        If `timeout_seconds` is provided, the task is executed in a separate
        process and will be terminated if it does not complete in time.
        """
        if envelope is None:
            envelope = PsiEnvelope(psi=psi, version="1.0")

        started_dt = datetime.now(timezone.utc)
        started = _utc_timestamp()
        success = True
        result: Any = None
        error_msg: Optional[str] = None

        if timeout_seconds is None:
            # Simple direct call
            try:
                result = task(**kwargs)
            except Exception as exc:  # noqa: BLE001
                success = False
                error_msg = f"{type(exc).__name__}: {exc}"
        else:
            # Run in separate process to enforce timeout
            ctx = multiprocessing.get_context("spawn")
            q = ctx.Queue()
            p = ctx.Process(target=_kernel_worker, args=(q, task, kwargs))
            p.start()
            p.join(timeout_seconds)
            if p.is_alive():
                p.terminate()
                p.join()
                success = False
                error_msg = "TimeoutError: execution exceeded timeout"
            else:
                try:
                    status, payload = q.get_nowait()
                except Exception:
                    success = False
                    error_msg = "ExecutionError: no result returned"
                else:
                    if status == "ok":
                        result = payload
                    else:
                        success = False
                        err_type, err_text = payload
                        error_msg = f"{err_type}: {err_text}"

        finished_dt = datetime.now(timezone.utc)
        finished = _utc_timestamp()
        runtime_ms = (finished_dt - started_dt).total_seconds() * 1000.0

        return ExecutionTrace(
            psi=psi,
            envelope=envelope,
            success=success,
            output=result,
            error=error_msg,
            started_at=started,
            finished_at=finished,
            runtime_ms=runtime_ms,
            metadata={},
            # KL 0.3.0 fields keep their defaults unless explicitly set
        )


__all__ = ["ExecutionTrace", "Kernel"]
