import time

import pytest

import kl_kernel_logic as kl
from kl_kernel_logic.cael import PolicyViolationError


def slow_task(seconds: float = 1.0):
    time.sleep(seconds)
    return "done"


def write_task(filename: str, content: str) -> str:
    return f"wrote {len(content)} bytes"


def test_per_call_flags_blocked_by_context_policy():
    psi = kl.PsiDefinition(
        psi_type="filesystem.write",
        domain="io",
        effect="write",
    )

    cael = kl.CAEL()

    ctx = kl.ExecutionContext(
        user_id="u",
        request_id="req-flag",
        policy=kl.ExecutionPolicy(allow_network=False, allow_filesystem=False, timeout_seconds=5),
    )

    with pytest.raises(PolicyViolationError):
        cael.execute(psi=psi, task=write_task, ctx=ctx, filename="x", content="y", needs_fs=True)


def test_timeout_enforced_via_context_policy():
    psi = kl.PsiDefinition(
        psi_type="test.timeout_check",
        domain="test",
        effect="pure",
    )

    cael = kl.CAEL()

    # set a short timeout via ExecutionContext.policy
    ctx = kl.ExecutionContext(
        user_id="u",
        request_id="req-timeout",
        policy=kl.ExecutionPolicy(allow_network=False, allow_filesystem=False, timeout_seconds=1),
    )

    trace = cael.execute(psi=psi, task=slow_task, ctx=ctx, seconds=2)
    data = trace.describe()

    assert data["success"] is False
    assert data["error"] is not None
    assert "TimeoutError" in data["error"]
