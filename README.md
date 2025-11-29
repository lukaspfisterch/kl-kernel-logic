# KL Kernel Logic

**Version 0.3.0** | Lightweight, deterministic, governance-ready execution framework.

# KL Kernel Logic

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Status](https://img.shields.io/badge/Status-Alpha-orange)
[![Tests](https://github.com/lukaspfisterch/kl-kernel-logic/actions/workflows/tests.yml/badge.svg)](https://github.com/lukaspfisterch/kl-kernel-logic/actions/workflows/tests.yml)
[![License](https://img.shields.io/badge/License-MIT-green)](https://github.com/lukaspfisterch/kl-kernel-logic/blob/main/LICENSE)

KL Kernel Logic separates the declarative definition of an operation (Psi) from its controlled execution (CAEL + Kernel), enabling:

- reproducible computation
- policy-aligned execution
- inspectable and auditable run results
- clean integration paths for both deterministic code and AI-based components

The goal is not to build yet another orchestration system, but to provide the minimum deterministic substrate on which safe, inspectable, policy-driven computation can be built.

## Table of Contents
- Overview
- Core Concepts
- Architecture
- Features
- Timeout & Multiprocessing
- Policy & Audit
- Repository Structure
- Installation
- Quick Example
- Policy Example
- Foundations Examples
- Tests
- Roadmap
- License

## Overview
KL Kernel Logic provides a minimal but expressive grammar for defining operations (Psi) and executing them under explicit constraints (CAEL). It addresses a gap in modern AI/automation stacks:

"How do we ensure reproducible and auditable execution when integrating AI or semi-deterministic components?"

KL solves this by:

- defining operations in a declarative schema
- transporting them via versioned envelopes
- executing them through a deterministic kernel
- producing a trace bundle suitable for governance and audit

The framework imposes no domain-specific semantics. It is a binding layer, designed for system builders, AI platform developers, and engineers who need clarity and operational trust.

## Core Concepts
### Psi (Principle Definition Layer)
Psi describes the essence of an operation, independent of its technical execution:

- psi_type: fully qualified operation identifier (e.g. "foundations.poisson_1d")
- domain: logical domain (e.g. "math", "io", "governance")
- effect: execution characteristic (e.g. "pure", "read", "write", "external", "ai")
- version: schema version (default "0.3.0")
- constraints: structured PsiConstraints object for policy anchoring
- optional description, tags, and metadata

Psi is immutable and serializable.

### Effect Classes

KL distinguishes effect classes to describe the nature of an operation:

- **pure**: deterministic computation with no side effects
- **read**: read-only operations (config lookup, data retrieval)
- **io**: filesystem operations (read/write)
- **external**: network operations (API calls, external services)
- **ai**: AI/LLM operations (may be nondeterministic)

The `DefaultSafePolicyEngine` evaluates these effects:
- Allows: `pure`, `read`, `ai`
- Blocks: `io`, `external`

**Important:** The `DefaultSafePolicyEngine` marks `ai` operations as `deterministic=False`. This is critical for audit interpretation and governance reporting, but **does not block execution**. AI operations are allowed by default, but their nondeterministic nature is explicitly tracked in every `PolicyDecision` and `ExecutionTrace` for downstream audit systems.

This classification enables policy-based control and audit traceability without requiring knowledge of the underlying implementation.

### PsiEnvelope (Transport & Meta Layer)
A versioned, auditable container that carries:

- the Psi definition
- a UUID envelope identifier
- creation timestamp
- optional metadata
- optional signature

Envelopes form the basis for trace bundling, governance, and audit.

### CAEL (Controlled AI Execution Layer)
A wrapper providing:

- basic validation
- envelope creation or enrichment
- constraint mapping
- optional (future) policy evaluation
- value-safe, exception-capturing execution

CAEL does not execute tasks itself. It delegates to the Kernel.

### Kernel
The lowest-level execution engine. It receives a Psi + envelope + callable, executes the callable, and returns a deterministic ExecutionTrace.

The Kernel is intentionally minimal:

- no business logic
- no policy logic
- no orchestration logic

It focuses only on clean execution and structured trace output.

## Architecture
```text
Client / App / Orchestrator
            |
            v
+-------------------------------+
|        KL Kernel Logic        |
+-------------------------------+
       |                   |
       v                   v
   Psi Definition     Controlled Execution (CAEL)
         \               /
          \             /
           +-----------+
           |  Kernel   |
           +-----------+
                 |
                 v
      Deterministic Ops / AI Models / External APIs
```

Each run produces a trace bundle:

```text
{
  psi: {...},
  envelope: {...},
  execution: {
      success: true,
      output: ...,
      error: null,
      started_at: "2025-11-29T14:23:45.123Z",
      finished_at: "2025-11-29T14:23:45.456Z",
      runtime_ms: 333.0
  }
}
```

## Features
- - Declarative operation model (Psi)
- Versioned metadata envelope
- Deterministic kernel execution
- Serializable execution traces
- Policy-ready CAEL layer
- Clean separation of logic and execution
- Support for deterministic foundations and semi-deterministic AI tasks
- Reference implementations and examples included
- Fully testable and predictable runtime behavior

## Timeout & Multiprocessing
KL 0.3.0 introduces timeout enforcement via multiprocessing. When a timeout is specified, tasks execute in a separate process and are terminated if they exceed the deadline.

### Timeout Precedence
Timeouts are resolved in the following order (highest to lowest priority):

1. **Per-call `timeout_seconds` kwarg** passed to `CAEL.execute()`
2. **`ExecutionContext.policy.timeout_seconds`** from the request context
3. **`CAELConfig.default_timeout_seconds`** global configuration
4. **No timeout** if none of the above are specified

Example:

```python
from kl_kernel_logic import CAEL, CAELConfig, ExecutionContext, ExecutionPolicy

cael = CAEL(config=CAELConfig(default_timeout_seconds=10))
ctx = ExecutionContext(
    user_id="user1",
    request_id="req1",
    policy=ExecutionPolicy(timeout_seconds=5)
)

# Per-call kwarg takes precedence: 3 seconds
trace = cael.execute(psi=psi, task=my_task, ctx=ctx, timeout_seconds=3)
```

### Multiprocessing Constraints (Windows & Linux)
When a timeout is enforced, tasks execute in a separate process using Python's multiprocessing module with spawn context (for Windows compatibility). This imposes a pickling constraint:

Tasks must be defined at module top-level (not as lambdas or nested functions) to be serializable across process boundaries.

**Not allowed:**

```python
# ❌ Lambda (not picklable)
cael.execute(psi=psi, task=lambda x: x.upper(), timeout_seconds=5)

# ❌ Nested function (not picklable)
def outer():
    def inner(x):
        return x.upper()
    cael.execute(psi=psi, task=inner, timeout_seconds=5)
```

**Allowed:**

```python
# ✅ Module-level function
def my_task(x: str) -> str:
    return x.upper()

cael.execute(psi=psi, task=my_task, timeout_seconds=5)

# ✅ Callable class with __call__
class MyTask:
    def __call__(self, x: str) -> str:
        return x.upper()

cael.execute(psi=psi, task=MyTask(), timeout_seconds=5)
```

**Note:** If no timeout is specified, tasks can be arbitrary callables (including lambdas and nested functions) since they execute in the same process.

### Timeout Behavior
- On timeout: execution is terminated, `ExecutionTrace.success` is `False`, `ExecutionTrace.error` contains `"TimeoutError: execution exceeded timeout"`
- The worker process is forcibly terminated after the timeout expires
- No partial results are returned if the task did not complete

## Policy & Audit
KL 0.3.0 includes a policy engine and audit layer:

- **PolicyEngine Interface**: Extensible policy evaluation via strategy pattern
- **DefaultSafePolicyEngine**: Effect-based policy evaluation (pure, read, io, external, ai)
- **Policy Evaluation**: Blocks execution before Kernel if policies are violated
- **Audit Reports**: Deterministic, JSON-serializable execution records with traces
- **Envelope Versioning**: PsiEnvelope carries UUID, timestamp, and optional metadata for traceability

Future versions expand on:

- enriched policy language (capabilities, role-based access)
- input/output scrubbing and validation schemas
- signature validation and crypto
- formalized trace schemas (JSON Schema / OpenAPI)
- governance connectors (JSONL, NDJSON, SIEM integrations)

## Repository Structure
```
src/kl_kernel_logic/
    psi.py                # Declarative operation definitions
    psi_envelope.py       # Versioned transport container
    kernel.py             # Deterministic execution engine
    cael.py               # Execution wrapper & policy bridge
    execution_context.py  # Policy and context types
    policy.py             # Policy templates and evaluation
    audit.py              # Audit report builder
    examples/
    examples_foundations/

tests/
docs/
```

- **psi.py**: Operation definition layer
- **psi_envelope.py**: Versioned metadata transport
- **kernel.py**: Low-level execution
- **cael.py**: Policy evaluation and constraint handling
- **execution_context.py**: User and policy context types
- **policy.py**: PolicyEngine interface and DefaultSafePolicyEngine
- **audit.py**: Audit report generation from execution traces
- **examples**: Reference implementations
- **examples_foundations**: Deterministic mathematical operations (Poisson, trajectory, smoothing)
- **tests**: Full test coverage
- **docs**: Architecture and usage guides

## Installation
```powershell
git clone https://github.com/lukaspfisterch/kl-kernel-logic.git
cd kl-kernel-logic

python -m venv .venv
# Windows
.\.venv\Scripts\Activate.ps1
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
```

Run tests:

```bash
pytest -q
```

## Quick Example
```python
from kl_kernel_logic import (
    PsiDefinition, PsiConstraints,
    PsiEnvelope, CAEL, CAELConfig
)


def uppercase(text: str) -> str:
    return text.upper()


psi = PsiDefinition(
    psi_type="text.transform",
    domain="text",
    effect="pure",
)

cael = CAEL(config=CAELConfig())

trace = cael.execute(
    psi=psi,
    task=uppercase,
    text="Hello World"
)

print(trace.describe())
```

### Output (simplified)
```text
{
  "psi": {...},
  "envelope": {...},
  "success": true,
  "output": "HELLO WORLD",
  "error": null,
  "runtime_ms": 0.123,
  "metadata": {}
}
```

## Policy Example
KL 0.3.0 uses the PolicyEngine pattern for extensible policy evaluation:

```python
from kl_kernel_logic import (
    PsiDefinition,
    CAEL, CAELConfig,
    PolicyViolationError
)
from kl_kernel_logic.policy import DefaultSafePolicyEngine

# Define an I/O operation
psi_io = PsiDefinition(
    psi_type="filesystem.write",
    domain="io",
    effect="io",  # Will be blocked by DefaultSafePolicyEngine
)

# CAEL uses DefaultSafePolicyEngine by default
cael = CAEL()

try:
    trace = cael.execute(psi=psi_io, task=write_file)
except PolicyViolationError as e:
    print(f"Blocked by {e.policy_name}: {e.reason}")
```

Run the foundation examples:

```bash
python -m kl_kernel_logic.examples_foundations.runners
```

## Foundations Examples
Location: `src/kl_kernel_logic/examples_foundations/`

Contains deterministic operations such as:

- Poisson equation solver (1D)
- Sliding-window smoothing
- Simple measurement integration

These examples demonstrate:

- reproducibility
- effect classes (single-step, multi-step, deterministic)
- usage of Psi and CAEL without AI dependencies

## Tests
Execute the suite:

```bash
pytest -q
```

Validates:

- Psi semantics
- envelope structure
- kernel execution correctness
- CAEL envelope handling and metadata merging
- deterministic foundation operations
- policy engine evaluation

## Roadmap
- Full policy execution layer
- Configurable trace schemas
- First-class JSONL/NDJSON telemetry
- Web-based inspection UI (interactive trace viewer)
- Multi-operation workflows (chains, DAGs, state machines)
- Expanded deterministic libraries
- LLM adapter layer (controlled nondeterminism)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

For bug reports and feature requests, please use the [GitHub Issues](https://github.com/lukaspfisterch/kl-kernel-logic/issues).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2025 Lukas Pfister
