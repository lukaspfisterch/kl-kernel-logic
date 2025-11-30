from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4

from .psi import PsiDefinition

"""
Psi envelope layer for KL Kernel Logic.

PsiEnvelope is a transparent, versioned transport container for PsiDefinition.
It adds identifiers and timestamps required for traceability and audit.
"""


def _utc_now_iso() -> str:
    """
    Return current UTC time as an ISO 8601 string.
    """
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class PsiEnvelope:
    """
    Versioned transport container for Psi definitions.

    Fields:
    - psi:         the declarative PsiDefinition
    - version:     schema version of the envelope
    - envelope_id: unique identifier for this envelope
    - timestamp:   creation time in ISO 8601 (UTC)
    - metadata:    optional free-form metadata
    - signature:   optional external signature or checksum
    """

    psi: PsiDefinition
    version: str = "0.3.3"
    envelope_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: str = field(default_factory=_utc_now_iso)
    metadata: Dict[str, Any] = field(default_factory=dict)
    signature: Optional[str] = None

    def describe(self) -> Dict[str, Any]:
        """
        Human/audit oriented representation of this envelope.

        For now, identical to to_dict(), but kept as a separate method
        for compatibility with ExecutionTrace.describe().
        """
        return self.to_dict()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "psi": self.psi.describe(),
            "version": self.version,
            "envelope_id": self.envelope_id,
            "timestamp": self.timestamp,
            "metadata": dict(self.metadata),
            "signature": self.signature,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PsiEnvelope":
        return cls(
            psi=PsiDefinition.from_dict(data["psi"]),
            version=data.get("version", "0.3.3"),
            envelope_id=data.get("envelope_id", str(uuid4())),
            timestamp=data.get("timestamp") or _utc_now_iso(),
            metadata=dict(data.get("metadata") or {}),
            signature=data.get("signature"),
        )
