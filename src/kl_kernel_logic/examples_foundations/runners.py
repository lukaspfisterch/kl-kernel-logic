"""
Runnable helpers for foundational examples.

These are convenience entrypoints to demonstrate KL end-to-end on deterministic
operations. They print the bundled {psi, execution} result.
"""

from pprint import pprint

from kl_kernel_logic import (
    PsiDefinition,
    OperationType,
    EffectClass,
    ExecutionPolicy,
    ExecutionContext,
    Kernel,
)
from .operations import (
    Grid1D,
    solve_poisson_1d,
    integrate_trajectory_1d,
    smooth_measurements,
)


def run_poisson_example() -> dict:
    psi = PsiDefinition(
        operation_type=OperationType.TRANSFORM,
        logical_binding="foundations.numerics.poisson_1d",
        effect_class=EffectClass.NON_STATE_CHANGING,
        constraints=(
            "Input: 1D scalar grid. "
            "Output: 1D scalar grid. "
            "Deterministic. Grid length <= 4096."
        ),
    )
    policy = ExecutionPolicy(
        allow_network=False,
        allow_filesystem=False,
        timeout_seconds=30,
    )
    ctx = ExecutionContext(
        user_id="foundations-numerics",
        request_id="poisson-1d-demo-001",
        policy=policy,
    )

    rho_grid = Grid1D(values=[0.0, 1.0, 0.0], spacing=0.1)
    kernel = Kernel()
    return kernel.execute(
        psi=psi,
        ctx=ctx,
        task=solve_poisson_1d,
        rho=rho_grid,
    )


def run_trajectory_example() -> dict:
    psi = PsiDefinition(
        operation_type=OperationType.TRANSFORM,
        logical_binding="foundations.mechanics.trajectory_1d",
        effect_class=EffectClass.NON_STATE_CHANGING,
        constraints=(
            "Input: initial position and velocity, force, mass, time step and step count. "
            "Output: sequence of positions over time. "
            "Deterministic for given parameters."
        ),
    )
    policy = ExecutionPolicy(
        allow_network=False,
        allow_filesystem=False,
        timeout_seconds=10,
    )
    ctx = ExecutionContext(
        user_id="foundations-mechanics",
        request_id="traj-1d-demo-001",
        policy=policy,
    )
    kernel = Kernel()
    return kernel.execute(
        psi=psi,
        ctx=ctx,
        task=integrate_trajectory_1d,
        x0=0.0,
        v0=0.0,
        dt=0.01,
        steps=100,
        force=1.0,
        mass=1.0,
    )


def run_smoothing_example() -> dict:
    psi = PsiDefinition(
        operation_type=OperationType.TRANSFORM,
        logical_binding="foundations.signals.smoothing",
        effect_class=EffectClass.NON_STATE_CHANGING,
        constraints=(
            "Input: 1D scalar series, length <= 10_000. "
            "Output: 1D scalar series of the same length. "
            "Deterministic three point moving average."
        ),
    )
    policy = ExecutionPolicy(
        allow_network=False,
        allow_filesystem=False,
        timeout_seconds=5,
    )
    ctx = ExecutionContext(
        user_id="foundations-signals",
        request_id="smooth-demo-001",
        policy=policy,
    )
    kernel = Kernel()
    return kernel.execute(
        psi=psi,
        ctx=ctx,
        task=smooth_measurements,
        values=[1.0, 2.0, 3.0, 4.0],
    )


def run_all_examples() -> None:
    pprint(run_poisson_example())
    pprint(run_trajectory_example())
    pprint(run_smoothing_example())


if __name__ == "__main__":
    run_all_examples()
