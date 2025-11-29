"""
Audit reporting for KL Kernel Logic.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict

from .kernel import ExecutionTrace


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


@dataclass(frozen=True)
class AuditReport:
    """
    High level audit view over an execution trace.

    It captures:
    - when the report was generated
    - a serialised view of the execution trace
    """

    generated_at: str
    trace: Dict[str, Any]

    def describe(self) -> Dict[str, Any]:
        """
        Serialisable representation of the audit report.
        """
        return {
            "generated_at": self.generated_at,
            "trace": self.trace,
        }


def build_audit_report(trace: ExecutionTrace) -> AuditReport:
    """
    Build a standard audit report from an ExecutionTrace.
    """
    return AuditReport(
        generated_at=_utc_timestamp(),
        trace=trace.describe(),
    )


__all__ = ["AuditReport", "build_audit_report"]
