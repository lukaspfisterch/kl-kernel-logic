"""
Deterministic foundational operations used to exercise KL end-to-end.

These are intentionally simple: numeric placeholders that focus on
structure, policy checks, and traceability rather than performance.
"""

from dataclasses import dataclass
from typing import Iterable, List


@dataclass
class Grid1D:
    values: List[float]
    spacing: float

    def __post_init__(self) -> None:
        if self.spacing <= 0:
            raise ValueError("Grid spacing must be positive")
        if len(self.values) < 3:
            raise ValueError("Grid must contain at least 3 points")

    @property
    def length(self) -> int:
        return len(self.values)


def solve_poisson_1d(rho: Grid1D) -> Grid1D:
    """
    Solve d²phi/dx² = rho with Dirichlet boundary conditions (phi[0]=phi[-1]=0)
    using a simple tridiagonal solver. This is a deterministic stand-in for
    a real numeric kernel.
    """
    n = rho.length
    dx = rho.spacing

    # Tridiagonal coefficients for interior points
    a = [-1.0] * (n - 2)
    b = [2.0] * (n - 1)
    c = [-1.0] * (n - 2)
    d = [r * dx * dx for r in rho.values[1:-1]]

    # Thomas algorithm (forward elimination)
    for i in range(1, n - 1):
        m = a[i - 1] / b[i - 1]
        b[i] = b[i] - m * c[i - 1]
        d[i] = d[i] - m * d[i - 1]

    # Back substitution
    phi_internal = [0.0] * (n - 2)
    phi_internal[-1] = d[-1] / b[-1]
    for i in range(n - 3, -1, -1):
        phi_internal[i] = (d[i] - c[i] * phi_internal[i + 1]) / b[i]

    phi = [0.0] + phi_internal + [0.0]
    return Grid1D(values=phi, spacing=dx)


def integrate_trajectory_1d(
    x0: float,
    v0: float,
    dt: float,
    steps: int,
    force: float,
    mass: float,
) -> List[float]:
    """
    Integrate position over discrete steps under constant force.
    Returns the list of positions (including initial).
    """
    if dt <= 0:
        raise ValueError("dt must be positive")
    if steps < 1:
        raise ValueError("steps must be at least 1")
    if mass == 0:
        raise ValueError("mass must be non-zero")

    x = x0
    v = v0
    positions = [x]
    a = force / mass

    for _ in range(steps):
        v += a * dt
        x += v * dt
        positions.append(x)

    return positions


def smooth_measurements(values: Iterable[float], window: int = 3) -> List[float]:
    """
    Apply a simple moving average with the specified window (>=1).
    Edges use the available values (no padding).
    """
    vals = list(values)
    if window < 1:
        raise ValueError("window must be >= 1")
    if not vals:
        return []

    half = window // 2
    smoothed: List[float] = []

    for i in range(len(vals)):
        start = max(0, i - half)
        end = min(len(vals), i + half + 1)
        window_vals = vals[start:end]
        smoothed.append(sum(window_vals) / len(window_vals))

    return smoothed
