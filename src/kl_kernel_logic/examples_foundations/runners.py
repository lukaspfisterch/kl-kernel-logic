"""
Runnable helpers for foundational examples.

These are convenience entrypoints to demonstrate KL end-to-end on deterministic
operations. They print the bundled {psi, envelope, execution} result.
"""

from pprint import pprint
from typing import Any, Dict

from kl_kernel_logic import (
    PsiDefinition,
    PsiConstraints,
    ExecutionPolicy,
    ExecutionContext,
    CAEL,
    CAELConfig,
)
from .operations import (
    Grid1D,
    solve_poisson_1d,
    integrate_trajectory_1d,
    smooth_measurements,
)


def run_poisson_example() -> Dict[str, Any]:
    psi = PsiDefinition(
        psi_type="foundations.poisson_1d",
        domain="math",
        effect="pure",
        description="1D Poisson equation solver",
        constraints=PsiConstraints(
            scope="numerics",
            format="Grid1D input/output",
            extra={"max_grid_size": 4096},
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
    cael = CAEL(config=CAELConfig())
    trace = cael.execute(
        psi=psi,
        task=solve_poisson_1d,
        ctx=ctx,
        rho=rho_grid,
    )
    return trace.describe()


def run_trajectory_example() -> Dict[str, Any]:
    psi = PsiDefinition(
        psi_type="foundations.trajectory_1d",
        domain="math",
        effect="pure",
        description="1D trajectory integration",
        constraints=PsiConstraints(
            scope="mechanics",
            temporal="deterministic_simulation",
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

    cael = CAEL(config=CAELConfig())
    trace = cael.execute(
        psi=psi,
        task=integrate_trajectory_1d,
        ctx=ctx,
        x0=0.0,
        v0=0.0,
        dt=0.01,
        steps=100,
        force=1.0,
        mass=1.0,
    )
    return trace.describe()


def run_smoothing_example() -> Dict[str, Any]:
    psi = PsiDefinition(
        psi_type="foundations.smoothing",
        domain="math",
        effect="pure",
        description="Three-point moving average",
        constraints=PsiConstraints(
            scope="signals",
            format="1D scalar series",
            extra={"max_length": 10000},
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

    cael = CAEL(config=CAELConfig())
    trace = cael.execute(
        psi=psi,
        task=smooth_measurements,
        ctx=ctx,
        values=[1.0, 2.0, 3.0, 4.0],
    )
    return trace.describe()


def run_all_examples() -> None:
    pprint(run_poisson_example())
    pprint(run_trajectory_example())
    pprint(run_smoothing_example())


if __name__ == "__main__":
    run_all_examples()
