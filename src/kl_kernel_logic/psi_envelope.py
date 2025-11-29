"""
Psi Envelope

Minimal, versioned container for transporting Psi definitions
through Kernel, CAEL, orchestrators and audit layers.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4

from .psi import PsiDefinition


def _utc_timestamp() -> str:
    """
    Return an ISO 8601 UTC timestamp with millisecond precision and trailing Z.
    """
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


@dataclass(frozen=True)
class PsiEnvelope:
    """
    Transparent, deterministic container carrying a PsiDefinition.

    Fields:
    - psi: the PsiDefinition being executed
    - version: schema or contract version
    - envelope_id: unique id for traceability and correlation
    - timestamp: ISO 8601 creation time (UTC, with trailing Z)
    - metadata: optional free form key value pairs for routing and audit
    - signature: optional signature representation
    """

    psi: PsiDefinition
    version: str
    envelope_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: str = field(default_factory=_utc_timestamp)
    metadata: Optional[Dict[str, Any]] = None
    signature: Optional[str] = None

    def describe(self) -> Dict[str, Any]:
        """
        Return a serialisable representation used by Kernel, CAEL and audit logs.
        """
        return {
            "version": self.version,
            "envelope_id": self.envelope_id,
            "timestamp": self.timestamp,
            "psi": self.psi.describe(),
            "metadata": self.metadata or {},
            "signature": self.signature,
        }


__all__ = ["PsiEnvelope"]
