import pytest

import kl_kernel_logic as kl
from kl_kernel_logic.examples_foundations.operations import (
    Grid1D,
    integrate_trajectory_1d,
    smooth_measurements,
    solve_poisson_1d,
)


def test_poisson_deterministic_result():
    psi = kl.PsiDefinition(
        psi_type="foundations.poisson_1d",
        domain="math",
        effect="pure",
    )
    rho = Grid1D(values=[0.0, 1.0, 0.0], spacing=0.1)
    kernel = kl.Kernel()

    trace = kernel.execute(psi=psi, task=solve_poisson_1d, rho=rho)
    data = trace.describe()

    phi: Grid1D = data["output"]
    assert isinstance(phi, Grid1D)
    assert phi.values == pytest.approx([0.0, 0.005, 0.0])
    assert data["success"] is True
    assert data["error"] is None


def test_smoothing_deterministic_and_repeatable():
    psi = kl.PsiDefinition(
        psi_type="foundations.smoothing",
        domain="math",
        effect="pure",
    )
    kernel = kl.Kernel()

    first = kernel.execute(
        psi=psi,
        task=smooth_measurements,
        values=[1.0, 2.0, 3.0, 4.0],
    ).describe()
    second = kernel.execute(
        psi=psi,
        task=smooth_measurements,
        values=[1.0, 2.0, 3.0, 4.0],
    ).describe()

    assert first["output"] == [1.5, 2.0, 3.0, 3.5]
    assert first["output"] == second["output"]
    assert first["success"] is True
    assert second["success"] is True


def test_trajectory_positions_expected():
    psi = kl.PsiDefinition(
        psi_type="foundations.trajectory_1d",
        domain="math",
        effect="pure",
    )
    kernel = kl.Kernel()

    data = kernel.execute(
        psi=psi,
        task=integrate_trajectory_1d,
        x0=0.0,
        v0=0.0,
        dt=0.1,
        steps=3,
        force=1.0,
        mass=1.0,
    ).describe()

    positions = data["output"]
    assert positions == pytest.approx([0.0, 0.01, 0.03, 0.06])
    assert data["success"] is True
    assert data["error"] is None
