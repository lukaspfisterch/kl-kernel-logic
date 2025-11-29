"""
Tests for runtime_ms measurement in ExecutionTrace.
"""

import time

import kl_kernel_logic as kl


def slow_task(duration: float = 0.01) -> str:
    """Task that takes measurable time."""
    time.sleep(duration)
    return "completed"


def test_kernel_sets_runtime_ms_for_simple_task():
    """Kernel should calculate runtime_ms for simple tasks."""
    psi = kl.PsiDefinition(
        psi_type="test.simple",
        domain="test",
        effect="pure",
    )
    
    kernel = kl.Kernel()
    trace = kernel.execute(psi=psi, task=lambda: "ok")
    
    assert trace.runtime_ms is not None
    assert trace.runtime_ms >= 0.0
    assert trace.success is True


def test_kernel_sets_runtime_ms_for_slow_task():
    """Kernel should measure actual execution time."""
    psi = kl.PsiDefinition(
        psi_type="test.slow",
        domain="test",
        effect="pure",
    )
    
    kernel = kl.Kernel()
    trace = kernel.execute(psi=psi, task=slow_task, duration=0.01)
    
    assert trace.runtime_ms is not None
    assert trace.runtime_ms >= 10.0  # At least 10ms
    assert trace.success is True


def test_runtime_ms_present_in_trace_describe():
    """runtime_ms should be present in trace.describe() output."""
    psi = kl.PsiDefinition(
        psi_type="test.describe",
        domain="test",
        effect="pure",
    )
    
    kernel = kl.Kernel()
    trace = kernel.execute(psi=psi, task=lambda: "result")
    data = trace.describe()
    
    assert "runtime_ms" in data
    assert data["runtime_ms"] is not None
    assert data["runtime_ms"] >= 0.0


def test_cael_preserves_runtime_ms():
    """CAEL should pass through runtime_ms from Kernel."""
    psi = kl.PsiDefinition(
        psi_type="test.cael_runtime",
        domain="test",
        effect="pure",
    )
    
    cael = kl.CAEL()
    trace = cael.execute(psi=psi, task=slow_task, duration=0.01)
    
    assert trace.runtime_ms is not None
    assert trace.runtime_ms >= 10.0
    assert trace.success is True

