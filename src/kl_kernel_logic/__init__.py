"""
KL Kernel Logic core package.

The KL Execution Theory defines the minimal axioms any controlled execution
system must satisfy. KL Kernel Logic is the reference implementation of these axioms.

Exposes the fundamental building blocks for defining and executing operations
in the KL model.

Core axioms → Code mapping:
  Δ (atomic transitions)  → Kernel.execute()
  V (behaviour)           → ExecutionTrace sequences
  t (logical time)        → runtime_ms + trace indices
  G (governance)          → PolicyEngine evaluation
  L (boundaries)          → ExecutionPolicy + PsiConstraints

This module provides the stable public API for Psi definitions,
envelopes, execution, policy, and audit.

See docs/execution_theory_in_code.md for complete correspondence.
"""

# Psi layer
from .psi import PsiDefinition, PsiConstraints
from .psi_envelope import PsiEnvelope

# Kernel and CAEL
from .kernel import Kernel, ExecutionTrace
from .cael import CAEL, CAELConfig, PolicyViolationError

# Policy system
from .policy import (
    PolicyDecision,
    PolicyEngine,
    DefaultSafePolicyEngine,
)

# Execution context
from .execution_context import ExecutionPolicy, ExecutionContext

# Audit reporting
from .audit import AuditReport, build_audit_report


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

    # Execution context
    "ExecutionPolicy",
    "ExecutionContext",

    # Audit
    "AuditReport",
    "build_audit_report",
]

__version__ = "0.3.3"
