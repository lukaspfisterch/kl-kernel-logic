"""
Audit report model for KL Kernel Logic.

Takes an ExecutionTrace and wraps it into a small, serialisable report
object that higher-level systems can store or forward.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from .kernel import ExecutionTrace


@dataclass
class AuditReport:
    """
    Minimal audit report.

    Attributes:
        run_id: Identifier of the execution run (mapped from trace_id).
        trace: Serialised execution trace (ExecutionTrace.describe()).
        created_at: ISO 8601 timestamp when the run started.
        metadata: Optional, user-provided metadata.
    """

    run_id: str
    trace: Dict[str, Any]
    created_at: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def describe(self) -> Dict[str, Any]:
        """
        Return a JSON-serialisable representation of the audit report.

        Field names are chosen to be stable for external consumers:
        - run_id
        - trace
        - generated_at  (mapped from created_at)
        - metadata
        """
        return {
            "run_id": self.run_id,
            "trace": self.trace,
            "generated_at": self.created_at,
            "metadata": dict(self.metadata),
        }


def build_audit_report(
    trace: ExecutionTrace,
    metadata: Optional[Dict[str, Any]] = None,
) -> AuditReport:
    """
    Create an AuditReport from a completed ExecutionTrace.

    The report uses:
      - run_id      := trace.trace_id
      - created_at  := trace.started_at (fallback: trace.finished_at)
      - trace       := trace.describe()
      - metadata    := provided dict or empty
    """
    report_metadata = metadata or {}

    created_at = trace.started_at or trace.finished_at
    return AuditReport(
        run_id=trace.trace_id,
        trace=trace.describe(),
        created_at=created_at,
        metadata=report_metadata,
    )
