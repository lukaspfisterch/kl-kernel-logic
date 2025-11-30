"""
KL Kernel Logic core package.

Exposes the main building blocks for defining and executing operations
under the KL model.
"""

# Psi layer
from .psi import PsiDefinition, PsiConstraints
from .psi_envelope import PsiEnvelope

# Kernel & CAEL
from .kernel import Kernel, ExecutionTrace
from .cael import CAEL, CAELConfig, PolicyViolationError

# Policy system
from .policy import (
    PolicyDecision,
    PolicyEngine,
    DefaultSafePolicyEngine,
)

# Audit reporting
from .audit import AuditReport, build_audit_report

# Execution context (identity + per-request constraints)
from .execution_context import ExecutionPolicy, ExecutionContext


__all__ = [
    # Psi
    "PsiDefinition",
    "PsiConstraints",
    "PsiEnvelope",

    # Kernel and CAEL
    "Kernel",
    "ExecutionTrace",
    "CAEL",
    "CAELConfig",
    "PolicyViolationError",

    # Policy layer
    "PolicyDecision",
    "PolicyEngine",
    "DefaultSafePolicyEngine",

    # Audit
    "AuditReport",
    "build_audit_report",

    # Execution context
    "ExecutionPolicy",
    "ExecutionContext",
]


__version__ = "0.3.1"
