import pytest

import kl_kernel_logic as kl
from kl_kernel_logic.examples_foundations.operations import (
    Grid1D,
    solve_poisson_1d,
    integrate_trajectory_1d,
    smooth_measurements,
)


def _base_ctx(user: str, req: str, allow_fs: bool = False) -> kl.ExecutionContext:
    policy = kl.ExecutionPolicy(allow_network=False, allow_filesystem=allow_fs, timeout_seconds=5)
    return kl.ExecutionContext(user_id=user, request_id=req, policy=policy)


def test_poisson_deterministic_and_trace():
    psi = kl.PsiDefinition(
        operation_type=kl.OperationType.TRANSFORM,
        logical_binding="foundations.numerics.poisson_1d",
        effect_class=kl.EffectClass.NON_STATE_CHANGING,
    )
    ctx = _base_ctx("u", "req-poisson")
    rho = Grid1D(values=[0.0, 1.0, 0.0, -1.0, 0.0], spacing=0.1)
    kernel = kl.Kernel()

    result = kernel.execute(psi, ctx, task=solve_poisson_1d, rho=rho)

    assert result["psi"]["logical_binding"] == "foundations.numerics.poisson_1d"
    phi: Grid1D = result["execution"]["result"]
    assert isinstance(phi, Grid1D)
    assert phi.values[0] == 0.0 and phi.values[-1] == 0.0
    assert len(result["execution"]["trace"]) >= 2
    assert result["execution"]["trace"][0]["stage"] == "start"
    assert result["execution"]["trace"][-1]["stage"] == "end"


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
            needs_fs=True,  # trigger policy check
        )


def test_smoothing_deterministic():
    psi = kl.PsiDefinition(
        operation_type=kl.OperationType.TRANSFORM,
        logical_binding="foundations.signals.smoothing",
        effect_class=kl.EffectClass.NON_STATE_CHANGING,
    )
    ctx = _base_ctx("u", "req-smooth")
    kernel = kl.Kernel()

    result = kernel.execute(
        psi,
        ctx,
        task=smooth_measurements,
        values=[1.0, 2.0, 3.0, 4.0],
    )

    assert result["execution"]["result"] == [1.5, 2.0, 3.0, 3.5]


def test_trajectory_positions_increase():
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
    assert positions == sorted(positions)
