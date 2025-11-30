# KL Kernel Logic

**KL Kernel Logic is a small deterministic execution substrate designed to run both deterministic and nondeterministic operations under explicit constraints. It does not try to orchestrate. It provides a clean, auditable execution core that higher-level systems can build on.**

[![PyPI version](https://img.shields.io/pypi/v/kl-kernel-logic.svg)](https://pypi.org/project/kl-kernel-logic/)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Status](https://img.shields.io/badge/Status-Alpha-orange)
[![License](https://img.shields.io/badge/License-MIT-green)](https://github.com/lukaspfisterch/kl-kernel-logic/blob/main/LICENSE)

KL Kernel Logic separates the *definition* of an operation (Psi) from its *execution* (CAEL + Kernel).  
It gives you a small deterministic core that can run both fully deterministic tasks and nondeterministic ones (including LLM calls) with a clear execution trace.

**What you get:**
- Declarative operation model (Psi)
- Deterministic kernel execution with structured traces
- Versioned envelopes for transport and audit
- Policy-ready execution bridge (timeouts, effect classes)
- Examples for deterministic math, system calls, and AI tasks

```bash
pip install kl-kernel-logic
```

```python
from kl_kernel_logic import PsiDefinition, CAEL, CAELConfig

def uppercase(text: str) -> str:
    return text.upper()

psi = PsiDefinition(
    psi_type="text.uppercase",
    domain="text",
    effect="pure",
)

cael = CAEL(config=CAELConfig())
trace = cael.execute(psi=psi, task=uppercase, text="Hello KL")
print(trace.describe())
```

**Below you find architecture details, policy model, timeout handling, and design notes.**

## Table of Contents
- [Overview](#overview)
- [Use Cases](#use-cases)
- [Core Concepts](#core-concepts)
- [Architecture](#architecture)
- [Features](#features)
- [Timeout & Multiprocessing](#timeout--multiprocessing)
- [Policy & Audit](#policy--audit)
- [Repository Structure](#repository-structure)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Quick Example](#quick-example)
- [Policy Example](#policy-example)
- [AI/LLM Example](#aillm-example)
- [Foundations Examples](#foundations-examples)
- [Tests](#tests)
- [Roadmap](#roadmap)
- [FAQ](#faq)
- [Contributing](#contributing)
- [License](#license)

## Overview

KL Kernel Logic provides a minimal but expressive grammar for defining operations (Psi) and executing them under explicit constraints (CAEL). It addresses a gap in modern AI/automation stacks:

"How do we ensure reproducible and auditable execution when integrating AI or semi-deterministic components?"

KL solves this by:
- defining operations in a declarative schema
- transporting them via versioned envelopes
- executing them through a deterministic kernel
- producing a trace bundle suitable for governance and audit

The framework imposes no domain-specific semantics. It is a binding layer, designed for system builders, AI platform developers, and engineers who need clarity and operational trust.

## Use Cases

KL is designed for tasks that require controlled execution with transparent audit trails:

### Controlled AI Calls
- Route LLM requests with full input/output tracing
- Track nondeterminism explicitly
- Enforce timeouts and network policies

### Reproducible Computation
- Scientific workflows
- Deterministic mathematical operations
- Testable pipelines

### Governed System Tasks
- Controlled filesystem or network access
- Operation-level auditability
- Policy enforcement before execution

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
- policy evaluation
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

- Declarative operation model (Psi)
- Versioned metadata envelope
- Deterministic kernel execution
- Serializable execution traces
- Policy-ready CAEL layer
- Clean separation of logic and execution
- Support for deterministic foundations and semi-deterministic AI tasks
- Reference implementations and examples included
- Fully testable and predictable runtime behavior

## Timeout & Multiprocessing

KL 0.3.0 introduces timeout enforcement via multiprocessing. When a timeout is specified, tasks execute in a separate process and are terminated if they exceed the deadline. **If no timeout is active, execution runs in the main process without multiprocessing overhead.**

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

### Multiprocessing Constraints
When a timeout is enforced, tasks execute in a separate process using Python's multiprocessing module with spawn context. Spawn is the default on Windows and macOS, and available on Linux. This imposes a pickling constraint:

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
- **ExecutionPolicy**: Optional per-request flags (timeout_seconds, allow_network, allow_filesystem) that can be evaluated by PolicyEngine implementations
- **Policy Evaluation**: Blocks execution before Kernel if policies are violated
- **Audit Reports**: Deterministic, JSON-serializable execution records with traces
- **Envelope Versioning**: PsiEnvelope carries UUID, timestamp, and optional metadata for traceability

Future extensions:

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

### From PyPI (Recommended)

```bash
pip install kl-kernel-logic
```

### From Source (Development)

```bash
git clone https://github.com/lukaspfisterch/kl-kernel-logic.git
cd kl-kernel-logic

python -m venv .venv
# Windows
.\.venv\Scripts\Activate.ps1
# Linux/macOS
source .venv/bin/activate

pip install -e .
```

### Verify Installation

```bash
python -c "import kl_kernel_logic; print(kl_kernel_logic.__version__)"
```

### Run Tests (Development)

```bash
pytest -q
```

## Quick Start

Install and run your first KL operation:

```bash
# Install
pip install kl-kernel-logic

# Verify
python -c "import kl_kernel_logic; print(f'KL v{kl_kernel_logic.__version__} ready!')"
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

## AI/LLM Example

Execute LLM calls with full governance and audit trail:

```python
from kl_kernel_logic import (
    CAEL,
    PsiDefinition,
    ExecutionContext,
    ExecutionPolicy
)
import anthropic  # pip install anthropic

def call_claude(prompt: str) -> str:
    """Simple Claude API wrapper."""
    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text

# Define the operation
psi = PsiDefinition(
    psi_type="llm.anthropic.completion",
    domain="ai",
    effect="ai",  # Marks as AI operation
    description="Claude AI completion"
)

# Execution context with user identity and policy
ctx = ExecutionContext(
    user_id="user_123",
    request_id="req_456",
    policy=ExecutionPolicy(
        timeout_seconds=30,
        allow_network=True
    )
)

# Execute with full audit trail
cael = CAEL()
trace = cael.execute(
    psi=psi,
    task=call_claude,
    ctx=ctx,
    prompt="Explain quantum computing in simple terms"
)

# Audit information available
print(f"User: {trace.envelope.metadata['user_id']}")
print(f"Started: {trace.started_at}")
print(f"Runtime: {trace.runtime_ms}ms")
print(f"Success: {trace.success}")
if trace.success:
    print(f"Response: {trace.output[:100]}...")
```

**Output:**
```
User: user_123
Started: 2025-11-29T15:30:45.123Z
Runtime: 2341.5ms
Success: True
Response: Quantum computing is a revolutionary approach to computation that harnesses the principles...
```

Every LLM call is:
- ✅ Logged with user identity
- ✅ Timed and traced
- ✅ Policy-controlled (timeout, network access)
- ✅ Auditable for compliance

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

### v0.4.0
- Extended `PolicyEngine` interface (access to envelope + context)
- JSONL/NDJSON trace export
- Trace schema validation (JSON Schema)
- `PsiConstraints` validation in CAEL (opt-in)

"Future considerations (no timeline)"

## FAQ

**Q: Is KL production-ready?**  
A: KL is designed for production-style deterministic execution, but still in alpha to refine scope and API shape. Status "alpha" refers to the limited feature scope, not to stability.

**Q: Does KL work with any LLM provider?**  
A: Yes. KL is provider-agnostic. Write a simple wrapper function for any API (Anthropic, OpenAI, Azure, local models) and execute it via `CAEL.execute()`.

**Q: What's the performance overhead?**  
A: Minimal. Core execution adds ~1-2ms. Multiprocessing timeout adds ~50-100ms for process spawn.

**Q: Can I use KL without AI/LLMs?**  
A: Absolutely. KL works for any operation requiring governance: system calls, database operations, API calls, mathematical computations.

**Q: How do I implement custom policies?**  
A: Implement the `PolicyEngine` interface. See `DefaultSafePolicyEngine` in `policy.py` as reference.

**Q: Can I disable policy enforcement?**  
A: You can inject a permissive `PolicyEngine` that allows everything, but this is not recommended.

**Q: Can I use KL in closed-source/commercial projects?**  
A: Yes. MIT License permits commercial use without restrictions.

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
