# KL Kernel Logic
Version: **0.5.0**

A small deterministic execution model core.

KL Kernel Logic provides three components:

- `PsiDefinition`: operation definition (what)
- `Kernel`: atomic execution primitive (how)
- `CAEL`: sequential behaviour order (in what order)

It does not handle orchestration, governance, or policy. Those belong to higher layers.

[![PyPI version](https://img.shields.io/pypi/v/kl-kernel-logic.svg)](https://pypi.org/project/kl-kernel-logic/)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## Status

KL Kernel Logic v0.5.0 is a hardened, contract-stable kernel.

It is a concrete, stateless execution substrate derived from earlier KL Execution Theory work and compatible with the newer authoritative foundation defined in:
https://github.com/lukaspfisterch/execution-without-normativity

This version defines and enforces:
- deterministic execution scope
- normalized failure taxonomy
- immutable, canonical execution traces
- stable trace digests suitable for downstream derivation (DBL)

The kernel is considered **frozen** unless the theory contract is reopened.

---

## Kernel Contract

The normative kernel contract is defined here:

- [`docs/kernel_contract.md`](docs/kernel_contract.md)

All behavior, determinism guarantees, and failure semantics are governed
exclusively by this contract.

---

## Determinism

Determinism applies to the declared deterministic trace core only.
Observational fields (e.g. wall-clock timestamps, run_id, exception text)
are explicitly excluded and MUST NOT be used for derivation or control flow.

---

## Installation

```bash
pip install kl-kernel-logic
```

---

## Core Concepts

### PsiDefinition

A minimal logical operation descriptor. The core treats `PsiDefinition` as opaque. It stores and passes through these values but never interprets them.

```python
PsiDefinition(
    psi_type: str,
    name: str,
    metadata: Mapping[str, Any] | None = None,
)
```

PsiDefinition metadata is purely descriptive and never enters the Kernel or the ExecutionTrace unless explicitly passed to `Kernel.execute()`.

### Kernel

A deterministic execution engine. Deterministic in its execution model, not in the behaviour of user-provided tasks. Given a `PsiDefinition` and a callable, the Kernel executes the task and returns an `ExecutionTrace`.

Semantics:

- `task` is called exactly once with `**kwargs`
- `success` is `True` if and only if no exception is raised by `task`
- `output` contains the return value on success, `None` on failure
- `runtime_ms` is measured via a monotonic perf counter (observational)
- in deterministic mode, `runtime_ms` is forced to 0.0
- `run_id` is unique per execution (observational)
- in deterministic mode, `run_id` is provided by deterministic providers and may be stable

The Kernel never interprets metadata, never makes policy decisions, and never retries. Kernel implements ? as atomicity of execution and observation, not as state change. State belongs to user logic.

### ExecutionTrace

Immutable record of a single Kernel execution.

Fields:

- `psi`: the PsiDefinition used
- `run_id`: unique identifier for this execution
- `success`: `True` if task completed without exception
- `output`: return value of task (or `None` on failure)
- `error`: exception message (or `None` on success)
- `exception_type`: exception class name (or `None`)
- `exception_repr`: repr of exception (or `None`)
- `failure_code`: normalized kernel-level failure code
- `started_at`: UTC datetime when execution started (wall clock)
- `finished_at`: UTC datetime when execution finished (wall clock)
- `runtime_ms`: elapsed time in milliseconds (monotonic perf counter, observational)
- `metadata`: the metadata dict passed to `Kernel.execute()`, not from PsiDefinition
- `kernel_meta`: frozen kernel-level observational metadata

Time carries two layers: observational wall-clock time (UTC timestamps) and monotonic duration (runtime_ms). runtime_ms is suitable for per-step duration measurement, and ordering is established by CAEL step index, not by temporal fields.

The core never mutates traces after creation.

Fields marked as observational MUST NOT be used for ordering or semantic derivation.

Operational projection note: `kernel_meta` (if present) is an implementation-level observable and is not part of KL Execution Theory. It must not be treated as axiomatic state or used to redefine behavior semantics.

### CAEL

Sequential Atomic Execution Layer. Runs a sequence of independent `(psi, task, kwargs)` steps via a single Kernel instance in deterministic order.

Semantics:

- Steps are executed in order
- If a step fails, execution stops immediately
- `CaelResult.success` is `True` if and only if all steps succeeded
- `CaelResult.final_output` is the output of the last successful step, or `None` if the first step fails
- `CaelResult.traces` is the ordered list of `ExecutionTrace` objects (only executed steps)
- `CaelResult.failure_code` indicates the failure reason when execution stops
- `CaelResult.failure_message` carries the associated observational error message

CAEL does not pass output from one step to the next. Each step receives its own independent `kwargs`. It does not include retry logic, routing, or governance. CAEL establishes a total order over execution steps, independent of temporal measurements.

---

## Usage

### Basic Kernel Execution

```python
from kl_kernel_logic import Kernel, PsiDefinition

psi = PsiDefinition(
    psi_type="llm.call",
    name="example",
    metadata={"model": "dummy"},
)

def task(prompt: str):
    return prompt.upper()

kernel = Kernel()
trace = kernel.execute(psi=psi, task=task, prompt="hello")

print(trace.success)  # True
print(trace.output)   # "HELLO"
```

### CAEL with Independent Steps

```python
from kl_kernel_logic import Kernel, PsiDefinition
from kl_kernel_logic.cael import CAEL, CaelStep

kernel = Kernel()
cael = CAEL(kernel=kernel)

steps = [
    CaelStep(
        psi=PsiDefinition(psi_type="task", name="step-1"),
        task=lambda x: x + 1,
        kwargs={"x": 1},
    ),
    CaelStep(
        psi=PsiDefinition(psi_type="task", name="step-2"),
        task=lambda x: x * 10,
        kwargs={"x": 2},
    ),
]

result = cael.run(steps)

print(result.success)
print(len(result.traces))
```

---

## Scope and Non-Goals

KL Kernel Logic deliberately does not define:

- policy or governance logic (G)
- boundary logic (L)
- orchestration beyond CAEL
- persistence, storage, or network transport
- concurrency or parallelism models
- execution retries or compensation
- model selection or routing

---

## Conceptual Lineage

- Execution Without Normativity is the authoritative axiomatic foundation.  
  https://github.com/lukaspfisterch/execution-without-normativity
- KL Execution Theory is a historical transitional reference for KL concepts.  
  https://github.com/lukaspfisterch/kl-execution-theory
- KL Kernel Logic is a concrete, stateless execution kernel derived from that lineage.
- Higher layers such as DBL, governance, and domain runners build on top.

---

## KL Execution Theory

This kernel was originally aligned with KL Execution Theory. That theory remains a historical and transitional reference for KL concepts, but it has been superseded as the canonical axiomatic foundation by Execution Without Normativity.

- https://github.com/lukaspfisterch/kl-execution-theory

