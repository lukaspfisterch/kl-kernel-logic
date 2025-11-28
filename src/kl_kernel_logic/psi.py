"""
Psi Layer

Defines the principle characteristics of an AI operation.
Psi describes the logical essence of an operation before execution.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class OperationType(Enum):
    READ = "read"
    WRITE = "write"
    TRANSFORM = "transform"
    CLASSIFY = "classify"
    VALIDATE = "validate"
    DIAGNOSE = "diagnose"


class EffectClass(Enum):
    STATE_CHANGING = "state-changing"
    NON_STATE_CHANGING = "non-state-changing"
    SINGLE_STEP = "single-step"
    MULTI_STEP = "multi-step"
    DETERMINISTIC = "deterministic"
    NONDETERMINISTIC = "nondeterministic"


@dataclass
class PsiDefinition:
    """
    Describes what an operation is at a logical level.

    It is agnostic of concrete tooling and infrastructure.
    """

    operation_type: OperationType
    logical_binding: str
    effect_class: EffectClass
    constraints: Optional[str] = None

    def describe(self) -> dict:
        """
        Return a serialisable description of the operation.
        """
        return {
            "operation_type": self.operation_type.value,
            "logical_binding": self.logical_binding,
            "effect_class": self.effect_class.value,
            "constraints": self.constraints,
        }
