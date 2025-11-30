from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any


"""
Psi layer for KL Kernel Logic.

Defines:
- canonical constraint constants (ALLOWED_*_VALUES)
- PsiConstraints: governance anchor for a PsiDefinition
- PsiDefinition: declarative description of an operation

Public methods kept minimal but compatible with tests:
- PsiConstraints.validate()
- PsiConstraints.is_empty()
- PsiDefinition.assert_minimal_valid()
- PsiDefinition.psi_key()
- PsiDefinition.describe()
"""


# ---------------------------------------------------------------------------
# Canonical constraint domains (imported by tests)
# ---------------------------------------------------------------------------

ALLOWED_SCOPE_VALUES: Tuple[str, ...] = (
    "local",
    "session",
    "system",
)

ALLOWED_FORMAT_VALUES: Tuple[str, ...] = (
    "opaque",
    "text",
    "json",
)

ALLOWED_TEMPORAL_VALUES: Tuple[str, ...] = (
    "instant",
    "bounded",
    "stream",
)

ALLOWED_REVERSIBILITY_VALUES: Tuple[str, ...] = (
    "reversible",
    "irreversible",
)


# ---------------------------------------------------------------------------
# PsiConstraints – governance anchor
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PsiConstraints:
    """
    Governance anchor for a PsiDefinition.

    All fields are optional. When present, they are validated
    against the corresponding ALLOWED_*_VALUES constants.

    Important:
    - Construction never raises.
    - validate() performs the checks and may raise ValueError.
    """

    scope: Optional[str] = None
    format: Optional[str] = None
    temporal: Optional[str] = None
    reversibility: Optional[str] = None
    extra: Dict[str, str] = field(default_factory=dict)

    def validate(self) -> None:
        """
        Validate the constraint values against the canonical sets.

        Raises:
            ValueError if any field contains an invalid value.
        """
        if self.scope is not None and self.scope not in ALLOWED_SCOPE_VALUES:
            raise ValueError(
                f"Invalid constraint scope: '{self.scope}'. "
                f"Allowed: {ALLOWED_SCOPE_VALUES}"
            )

        if self.format is not None and self.format not in ALLOWED_FORMAT_VALUES:
            raise ValueError(
                f"Invalid constraint format: '{self.format}'. "
                f"Allowed: {ALLOWED_FORMAT_VALUES}"
            )

        if self.temporal is not None and self.temporal not in ALLOWED_TEMPORAL_VALUES:
            raise ValueError(
                f"Invalid temporal '{self.temporal}'. "
                f"Allowed: {ALLOWED_TEMPORAL_VALUES}"
            )

        if (
            self.reversibility is not None
            and self.reversibility not in ALLOWED_REVERSIBILITY_VALUES
        ):
            raise ValueError(
                f"Invalid reversibility '{self.reversibility}'. "
                f"Allowed: {ALLOWED_REVERSIBILITY_VALUES}"
            )

    def is_empty(self) -> bool:
        """
        Return True if no constraint field is set.

        Used by tests to distinguish 'no constraints' from 'constrained'.
        """
        return (
            self.scope is None
            and self.format is None
            and self.temporal is None
            and self.reversibility is None
            and not self.extra
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        JSON-serializable representation of the constraints.
        """
        return {
            "scope": self.scope,
            "format": self.format,
            "temporal": self.temporal,
            "reversibility": self.reversibility,
            "extra": dict(self.extra),
        }

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "PsiConstraints":
        """
        Construct constraints from a previously serialized dict.
        """
        if not data:
            return cls()
        return cls(
            scope=data.get("scope"),
            format=data.get("format"),
            temporal=data.get("temporal"),
            reversibility=data.get("reversibility"),
            extra=dict(data.get("extra") or {}),
        )


# ---------------------------------------------------------------------------
# PsiDefinition – declarative operation description
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PsiDefinition:
    """
    Declarative description of an operation under the KL model.

    Fields:
    - psi_type: fully qualified logical identifier of the operation
    - domain: logical domain (e.g. "math", "io", "ai")
    - effect: execution effect class (e.g. "pure", "read", "io", "external", "ai")
    - schema_version: version of the Psi schema itself (default: "1.0")
    - constraints: PsiConstraints instance used for governance anchoring
    - description, tags, metadata: optional descriptive fields
    - correlation_id: optional correlation identifier for tracing across systems
    - criticality: optional criticality level ("low", "medium", "high")
    """

    psi_type: str
    domain: str
    effect: str
    schema_version: str = "1.0"
    constraints: PsiConstraints = field(default_factory=PsiConstraints)
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)
    
    # Optional meta-fields for tracing and governance (added in 0.3.4)
    correlation_id: Optional[str] = None
    criticality: Optional[str] = None

    # ------------------------------------------------------------------
    # Core helpers
    # ------------------------------------------------------------------

    def assert_minimal_valid(self) -> None:
        """
        Minimal validity checks for a PsiDefinition.

        Required:
        - psi_type must be non-empty
        - domain must be non-empty
        - effect must be non-empty
        """
        if not self.psi_type:
            raise ValueError("psi_type must not be empty")
        if not self.domain:
            raise ValueError("domain must not be empty")
        if not self.effect:
            raise ValueError("effect must not be empty")

    def psi_key(self) -> str:
        """
        Stable key for identifying this PsiDefinition.

        Combines psi_type and schema_version.
        """
        return f"{self.psi_type}@{self.schema_version}"

    def describe(self) -> Dict[str, Any]:
        """
        Human/audit oriented representation of this PsiDefinition.

        For now, identical to to_dict(), but kept as a separate method
        for clarity and compatibility with existing callers.
        """
        return self.to_dict()

    def to_dict(self) -> Dict[str, Any]:
        """
        Lossless, JSON-serializable representation of this PsiDefinition.
        """
        return {
            "psi_type": self.psi_type,
            "domain": self.domain,
            "effect": self.effect,
            "schema_version": self.schema_version,
            "constraints": self.constraints.to_dict(),
            "description": self.description,
            "tags": list(self.tags),
            "metadata": dict(self.metadata),
            "correlation_id": self.correlation_id,
            "criticality": self.criticality,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PsiDefinition":
        """
        Reconstruct a PsiDefinition from a dict produced by to_dict().
        """
        constraints_data = data.get("constraints") or {}
        
        # Backward compatibility: accept both "version" and "schema_version"
        schema_version = data.get("schema_version") or data.get("version", "1.0")
        
        return cls(
            psi_type=data["psi_type"],
            domain=data["domain"],
            effect=data["effect"],
            schema_version=schema_version,
            constraints=PsiConstraints.from_dict(constraints_data),
            description=data.get("description"),
            tags=list(data.get("tags") or []),
            metadata=dict(data.get("metadata") or {}),
            correlation_id=data.get("correlation_id"),
            criticality=data.get("criticality"),
        )
