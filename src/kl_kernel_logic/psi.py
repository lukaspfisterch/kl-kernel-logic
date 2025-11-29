from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

#
# Allowed value sets for constraints.
# These are intentionally small and can be extended over time.
#

ALLOWED_SCOPE_VALUES = {
    "local",
    "session",
    "tenant",
    "cluster",
}

ALLOWED_FORMAT_VALUES = {
    "json",
    "ndjson",
    "binary",
    "text",
}

ALLOWED_TEMPORAL_VALUES = {
    "stateless",
    "session",
    "window",
}

ALLOWED_REVERSIBILITY_VALUES = {
    "reversible",
    "irreversible",
    "logged-only",
}


@dataclass(frozen=True)
class PsiConstraints:
    """
    Structured constraint block attached to a PsiDefinition.

    The primary role is to provide stable anchor points for policy
    evaluation without bloating the core contract. Validation is
    explicit and opt-in via `validate()`.
    """

    scope: Optional[str] = None
    format: Optional[str] = None
    temporal: Optional[str] = None
    reversibility: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def is_empty(self) -> bool:
        """Return True if no primary constraint field is set."""
        return (
            self.scope is None
            and self.format is None
            and self.temporal is None
            and self.reversibility is None
            and not self.extra
        )

    def validate(self) -> None:
        """
        Validate constraint values against the allowed sets.

        This method does not get called implicitly by the Kernel.
        It is intended for CAEL, policy adapters or configuration
        loaders that want to enforce stricter contracts.
        """
        if self.scope is not None and self.scope not in ALLOWED_SCOPE_VALUES:
            raise ValueError(
                f"Invalid constraint scope '{self.scope}'. "
                f"Allowed: {sorted(ALLOWED_SCOPE_VALUES)}"
            )

        if self.format is not None and self.format not in ALLOWED_FORMAT_VALUES:
            raise ValueError(
                f"Invalid constraint format '{self.format}'. "
                f"Allowed: {sorted(ALLOWED_FORMAT_VALUES)}"
            )

        if self.temporal is not None and self.temporal not in ALLOWED_TEMPORAL_VALUES:
            raise ValueError(
                f"Invalid constraint temporal '{self.temporal}'. "
                f"Allowed: {sorted(ALLOWED_TEMPORAL_VALUES)}"
            )

        if (
            self.reversibility is not None
            and self.reversibility not in ALLOWED_REVERSIBILITY_VALUES
        ):
            raise ValueError(
                f"Invalid constraint reversibility '{self.reversibility}'. "
                f"Allowed: {sorted(ALLOWED_REVERSIBILITY_VALUES)}"
            )

    def describe(self) -> Dict[str, Any]:
        """
        Serialisable representation of the constraint block.

        Used by audit and telemetry components. This is deliberately
        shallow and mirrors the public fields.
        """
        return {
            "scope": self.scope,
            "format": self.format,
            "temporal": self.temporal,
            "reversibility": self.reversibility,
            "extra": dict(self.extra),
        }


@dataclass(frozen=True)
class PsiDefinition:
    """
    Declarative definition of an operation in the KL Kernel.

    PsiDefinition describes WHAT should be executed, not HOW.
    It is intentionally domain agnostic and kept small to remain stable
    as a long lived contract between callers, CAEL and the Kernel.
    """

    # Identity and logical binding
    psi_type: str                         # e.g. "foundations.poisson_1d"
    domain: str                           # e.g. "math", "governance", "io"
    effect: str                           # e.g. "pure", "io", "external", "ai"

    # Versioning and human context
    version: str = "0.3.0"
    description: Optional[str] = None

    # Governance and policy anchor
    constraints: PsiConstraints = field(default_factory=PsiConstraints)

    # Non critical metadata
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def psi_key(self) -> str:
        """
        Stable logical key used by registries and orchestrators.

        Combines type and version. Version can later be mapped or pinned
        by higher level components (e.g. "latest:stable").
        """
        return f"{self.psi_type}@{self.version}"

    def assert_minimal_valid(self) -> None:
        """
        Local sanity check for construction time.

        Raises ValueError if required identity fields are missing or malformed.
        This is intentionally light weight and kept free of IO or external calls.
        """
        if not self.psi_type:
            raise ValueError("PsiDefinition.psi_type must not be empty")
        if not self.domain:
            raise ValueError("PsiDefinition.domain must not be empty")
        if not self.effect:
            raise ValueError("PsiDefinition.effect must not be empty")

    def describe(self) -> Dict[str, Any]:
        """
        Serialisable representation of the Psi definition.

        This is used by ExecutionTrace.describe() and audit helpers.
        """
        return {
            "psi_type": self.psi_type,
            "domain": self.domain,
            "effect": self.effect,
            "version": self.version,
            "description": self.description,
            "constraints": self.constraints.describe(),
            "tags": list(self.tags),
            "metadata": dict(self.metadata),
        }
