# Foundational operations for KL Kernel Logic

The foundational operations show how KL can describe and control deterministic computational steps before any broader orchestrator is built.

This document extends the concepts from the main README by providing concrete foundational operations used to exercise Psi, CAEL and the Kernel.


We use three examples:

1. `solve_poisson_1d` on a discrete grid  
2. `integrate_trajectory_1d` for a simple one dimensional motion  
3. `smooth_measurements` for a noisy measurement series

The focus is not numerical performance. The focus is on structure, policy and traceability for deterministic operations that can be described and inspected.

## Shared execution pattern

```text
Client --> Kernel --> CAEL --> Task (operation) --> CAEL --> Kernel --> Client
              |         ^          |
              |         |          +-- audit events (start, end, error)
              |         +-- policy checks (filesystem, timeout)
              +-- combined { psi, execution } bundle
```

Each operation defines:

- Psi: operation type, logical binding, effect class, constraints
- Policy: network and filesystem flags, timeout and optional token limits
- Task: deterministic implementation
- Trace: start, end and optionally error events with minimal metadata

## 1) solve_poisson_1d (numerics)

A simple numeric operation on a one dimensional grid. It acts as a deterministic, inspectable operation for KL.

**Psi**
```python
from kl_kernel_logic import PsiDefinition, OperationType, EffectClass

psi_poisson = PsiDefinition(
    operation_type=OperationType.TRANSFORM,
    logical_binding="foundations.numerics.poisson_1d",
    effect_class=EffectClass.NON_STATE_CHANGING,
    constraints=(
        "Input: 1D scalar grid. "
        "Output: 1D scalar grid. "
        "Deterministic. Grid length <= 4096."
    ),
)
```

**Policy and context**
```python
from kl_kernel_logic import ExecutionPolicy, ExecutionContext

policy_solver = ExecutionPolicy(
    allow_network=False,
    allow_filesystem=False,
    timeout_seconds=30,
)

ctx_solver = ExecutionContext(
    user_id="foundations-numerics",
    request_id="poisson-1d-demo-001",
    policy=policy_solver,
)
```

**Kernel execution**
```python
from kl_kernel_logic import Kernel
from kl_kernel_logic.examples_foundations.operations import Grid1D, solve_poisson_1d

rho_grid = Grid1D(values=[0.0, 1.0, 0.0], spacing=0.1)

kernel = Kernel()

result = kernel.execute(
    psi=psi_poisson,
    ctx=ctx_solver,
    task=solve_poisson_1d,
    rho=rho_grid,
)
```

**Result shape**
```text
{
  "psi": {...},
  "execution": {
    "result": Grid1D(...),
    "trace": [start_event, end_event]
  }
}
```

## 2) integrate_trajectory_1d (mechanics-flavoured numerics)

This example integrates a one dimensional trajectory under a constant force. It shows how a time stepping procedure can be represented as a foundational operation.

**Psi**
```python
psi_traj = PsiDefinition(
    operation_type=OperationType.TRANSFORM,
    logical_binding="foundations.mechanics.trajectory_1d",
    effect_class=EffectClass.NON_STATE_CHANGING,
    constraints=(
        "Input: initial position and velocity, force, mass, time step and step count. "
        "Output: sequence of positions over time. "
        "Deterministic for given parameters."
    ),
)
```

**Policy and execution**
```python
policy_traj = ExecutionPolicy(
    allow_network=False,
    allow_filesystem=False,
    timeout_seconds=10,
)

ctx_traj = ExecutionContext(
    user_id="foundations-mechanics",
    request_id="traj-1d-demo-001",
    policy=policy_traj,
)

kernel = Kernel()

result_traj = kernel.execute(
    psi=psi_traj,
    ctx=ctx_traj,
    task=integrate_trajectory_1d,
    x0=0.0,
    v0=0.0,
    dt=0.01,
    steps=100,
    force=1.0,
    mass=1.0,
)
```

The trace again records start and end, plus basic metadata about the run.

## 3) smooth_measurements (signals)

This example smooths a one dimensional series of measurements with a fixed kernel. It is a compact example for a deterministic data transformation.

**Psi**
```python
psi_smooth = PsiDefinition(
    operation_type=OperationType.TRANSFORM,
    logical_binding="foundations.signals.smoothing",
    effect_class=EffectClass.NON_STATE_CHANGING,
    constraints=(
        "Input: 1D scalar series, length <= 10_000. "
        "Output: 1D scalar series of the same length. "
        "Deterministic three point moving average."
    ),
)
```

**Policy and execution**
```python
policy_smooth = ExecutionPolicy(
    allow_network=False,
    allow_filesystem=False,
    timeout_seconds=5,
)

ctx_smooth = ExecutionContext(
    user_id="foundations-signals",
    request_id="smooth-demo-001",
    policy=policy_smooth,
)

kernel = Kernel()

values = [1.0, 2.0, 3.0, 4.0]

result_smooth = kernel.execute(
    psi=psi_smooth,
    ctx=ctx_smooth,
    task=smooth_measurements,
    values=values,
)
```

The result bundle can be logged or passed to higher level components that expect a structured `{ psi, execution }` record.

## Trace and audit expectations

For all foundational operations:

- `start`: `stage="start"`, includes at least `user_id` and `request_id`, optionally input size
- `end`: `stage="end"`, includes `result_type`, optionally shape or length
- `error`: recorded when policy blocks (for example `needs_fs` while disallowed) or when the task fails

## Minimum tests

For each foundational operation:

- Policy denial: network or filesystem forbidden leads to `PermissionError`
- Determinism: fixed input leads to fixed output (golden assertions)
- Trace integrity: ordered start and end events are present
- Timeout path: long running variants exercise timeout handling where applicable

## Scope and intent

The foundational operations are scaffolding to exercise Psi, CAEL and the Kernel on deterministic, inspectable tasks.

They provide a safe base for higher level orchestrator work before external systems are introduced. They are not production grade solvers. The goal is to demonstrate the execution grammar and observable behaviour of KL.
