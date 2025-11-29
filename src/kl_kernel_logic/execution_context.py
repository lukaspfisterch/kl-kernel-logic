"""
Execution context and policy helpers for KL Kernel Logic.

These types provide a structured way to describe who triggers an
operation and under which execution policy it should run.

They are deliberately kept light weight so they can be used by
orchestrators, CLIs or services without constraining the core kernel.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ExecutionPolicy:
    """
    Declarative execution policy used by higher level components.

    Typical usage:
        policy = ExecutionPolicy(
            allow_network=False,
            allow_filesystem=False,
            timeout_seconds=5,
        )

    The kernel itself does not enforce these flags. They are intended
    for CAEL, orchestrators or adapters that interpret and enforce them.
    """

    allow_network: bool = False
    allow_filesystem: bool = False
    timeout_seconds: int = 30
    max_tokens: Optional[int] = None


@dataclass(frozen=True)
class ExecutionContext:
    """
    Execution context for a single operation run.

    Captures:
    - user_id: logical caller identity
    - request_id: id for tracing and correlation
    - policy: associated ExecutionPolicy
    """

    user_id: str
    request_id: str
    policy: ExecutionPolicy


__all__ = ["ExecutionPolicy", "ExecutionContext"]
