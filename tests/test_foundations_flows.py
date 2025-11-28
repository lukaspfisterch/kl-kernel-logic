import pytest

import kl_kernel_logic as kl
from kl_kernel_logic.examples_foundations.operations import (
    Grid1D,
    integrate_trajectory_1d,
    smooth_measurements,
    solve_poisson_1d,
)


def _base_ctx(
    user: str,
    req: str,
    allow_fs: bool = False,
    allow_network: bool = False,
) -> kl.ExecutionContext:
    policy = kl.ExecutionPolicy(
        allow_network=allow_network,
        allow_filesystem=allow_fs,
        timeout_seconds=5,
    )
    return kl.ExecutionContext(user_id=user, request_id=req, policy=policy)


def test_poisson_deterministic_and_trace():
    psi = kl.PsiDefinition(
        operation_type=kl.OperationType.TRANSFORM,
        logical_binding="foundations.numerics.poisson_1d",
        effect_class=kl.EffectClass.NON_STATE_CHANGING,
    )
    ctx = _base_ctx("u", "req-poisson")
    rho = Grid1D(values=[0.0, 1.0, 0.0], spacing=0.1)
    kernel = kl.Kernel()

    result = kernel.execute(psi, ctx, task=solve_poisson_1d, rho=rho)

    phi: Grid1D = result["execution"]["result"]
    assert isinstance(phi, Grid1D)
    assert phi.values == pytest.approx([0.0, 0.005, 0.0])
    trace = result["execution"]["trace"]
    assert trace[0]["stage"] == "start"
    assert trace[-1]["stage"] == "end"


def test_policy_denies_filesystem():
    psi = kl.PsiDefinition(
        operation_type=kl.OperationType.TRANSFORM,
        logical_binding="foundations.signals.smoothing",
        effect_class=kl.EffectClass.NON_STATE_CHANGING,
    )
    ctx = _base_ctx("u", "req-fs-deny", allow_fs=False)
    kernel = kl.Kernel()

    with pytest.raises(PermissionError):
        kernel.execute(
            psi,
            ctx,
            task=smooth_measurements,
            values=[1.0, 2.0],
            needs_fs=True,
        )
    assert kernel.executor.trace_log[-1]["stage"] == "error"


def test_policy_denies_network():
    psi = kl.PsiDefinition(
        operation_type=kl.OperationType.TRANSFORM,
        logical_binding="foundations.signals.smoothing",
        effect_class=kl.EffectClass.NON_STATE_CHANGING,
    )
    ctx = _base_ctx("u", "req-net-deny", allow_network=False)
    kernel = kl.Kernel()

    with pytest.raises(PermissionError):
        kernel.execute(
            psi,
            ctx,
            task=smooth_measurements,
            values=[1.0],
            needs_network=True,
        )
    assert kernel.executor.trace_log[-1]["stage"] == "error"


def test_smoothing_deterministic_and_trace():
    psi = kl.PsiDefinition(
        operation_type=kl.OperationType.TRANSFORM,
        logical_binding="foundations.signals.smoothing",
        effect_class=kl.EffectClass.NON_STATE_CHANGING,
    )
    ctx = _base_ctx("u", "req-smooth")
    kernel = kl.Kernel()

    first = kernel.execute(
        psi,
        ctx,
        task=smooth_measurements,
        values=[1.0, 2.0, 3.0, 4.0],
    )
    second = kernel.execute(
        psi,
        ctx,
        task=smooth_measurements,
        values=[1.0, 2.0, 3.0, 4.0],
    )

    assert first["execution"]["result"] == [1.5, 2.0, 3.0, 3.5]
    assert first["execution"]["result"] == second["execution"]["result"]
    assert first["execution"]["trace"][0]["stage"] == "start"
    assert first["execution"]["trace"][-1]["stage"] == "end"
    assert second["execution"]["trace"][0]["stage"] == "start"
    assert second["execution"]["trace"][-1]["stage"] == "end"


def test_trajectory_positions_expected():
    psi = kl.PsiDefinition(
        operation_type=kl.OperationType.TRANSFORM,
        logical_binding="foundations.mechanics.trajectory_1d",
        effect_class=kl.EffectClass.NON_STATE_CHANGING,
    )
    ctx = _base_ctx("u", "req-traj")
    kernel = kl.Kernel()

    result = kernel.execute(
        psi,
        ctx,
        task=integrate_trajectory_1d,
        x0=0.0,
        v0=0.0,
        dt=0.1,
        steps=3,
        force=1.0,
        mass=1.0,
    )

    positions = result["execution"]["result"]
    assert positions == pytest.approx([0.0, 0.01, 0.03, 0.06])
    trace = result["execution"]["trace"]
    assert trace[0]["stage"] == "start"
    assert trace[-1]["stage"] == "end"
