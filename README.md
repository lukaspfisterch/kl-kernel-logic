# KL Kernel Logic

**KL Kernel Logic is a small deterministic execution substrate that separates the definition of an operation from its controlled execution. It does not orchestrate. It provides a clean, auditable execution core that higher-level systems can build on.**

[![PyPI version](https://img.shields.io/pypi/v/kl-kernel-logic.svg)](https://pypi.org/project/kl-kernel-logic/)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Status](https://img.shields.io/badge/Status-Alpha-orange)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

KL Kernel Logic separates the *definition* of an operation (Psi) from its *execution* (CAEL + Kernel).  
It gives you a small execution core that can run both fully deterministic tasks and nondeterministic ones (for example AI calls) with a clear execution trace.

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

## Table of Contents

- [Overview](#overview)
- [Core Concepts](#core-concepts)
- [Architecture](#architecture)
- [Policy and Context](#policy-and-context)
- [Audit](#audit)
- [Repository Structure](#repository-structure)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Foundations Examples](#foundations-examples)
- [Tests](#tests)
- [Theoretical Foundation](#theoretical-foundation)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Changelog](#changelog)

## Overview

KL Kernel Logic provides a minimal grammar for defining operations (Psi) and executing them under explicit constraints (CAEL). It addresses a simple question:

**How do we make execution transparent and auditable when deterministic and nondeterministic components are mixed?**

KL does this by:

- defining operations in a declarative schema (Psi)
- transporting them via versioned envelopes
- executing them through a small kernel
- producing structured traces that other systems can inspect and store

The framework is domain-neutral. It does not impose business semantics. It is a binding layer for system builders and AI platform engineers.

## Core Concepts

**For complete API documentation, see:** [docs/api_reference.md](docs/api_reference.md)

### Psi

Psi describes the essence of an operation, independent of its technical implementation:

- **psi_type**: fully qualified operation identifier (for example "foundations.poisson_1d")
- **domain**: logical domain (for example "math", "io", "ai")
- **effect**: execution characteristic (for example "pure", "read", "io", "external", "ai")
- **version**: schema version (default "0.3.3")
- **constraints**: PsiConstraints for policy anchoring
- optional **description**, **tags**, **metadata**

Psi is immutable and serialisable via `to_dict()`.

### Effect classes

Effect classes describe the nature of the operation:

- **pure** - deterministic computation without side effects
- **read** - read-only operations
- **io** - filesystem or similar side effects
- **external** - network or remote calls
- **ai** - AI or model calls that may be nondeterministic

The default policy engine uses these effect classes but does not hard-code any domain logic.

### PsiEnvelope

A PsiEnvelope is a versioned container around a Psi:

- carries the PsiDefinition
- adds **envelope_id** (UUID)
- adds creation **timestamp**
- optional **metadata** and **signature**

Envelopes give you a stable transport and audit container.

### Kernel

The Kernel is the lowest-level execution engine. It:

- receives PsiDefinition, optional PsiEnvelope and a callable task
- executes the callable exactly once
- captures any exception as a string
- measures timing
- returns an ExecutionTrace

The kernel does not apply policies and does not orchestrate.

### CAEL

The Controlled AI Execution Layer (CAEL):

- evaluates policies via a PolicyEngine
- builds or reuses a PsiEnvelope
- delegates execution to the Kernel
- records policy decisions in the resulting ExecutionTrace
- optionally classifies timeouts based on ExecutionContext.policy.timeout_seconds

CAEL is the main entry point for calling the kernel with governance hooks.

## Architecture

**For detailed architecture discussion, see:** [docs/01-kl-architecture.md](docs/01-kl-architecture.md)

Textual overview:

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
        Task / Function / Model
```

Each run produces a trace that bundles:

- logical intent (Psi)
- transport metadata (Envelope)
- execution outcome and timing (ExecutionTrace)

## Policy and Context

KL defines a small policy interface and a default policy engine.

```python
from kl_kernel_logic import (
    PsiDefinition,
    CAEL, CAELConfig,
    ExecutionContext, ExecutionPolicy,
)
from kl_kernel_logic import PolicyViolationError

psi = PsiDefinition(
    psi_type="filesystem.write_example",
    domain="io",
    effect="io",
)

ctx = ExecutionContext(
    user_id="user_123",
    request_id="req_456",
    policy=ExecutionPolicy(
        allow_network=False,
        allow_filesystem=False,
        timeout_seconds=2.0,
    ),
)

cael = CAEL(config=CAELConfig())

try:
    trace = cael.execute(psi=psi, task=some_io_task, ctx=ctx)
except PolicyViolationError as exc:
    print(f"Blocked by {exc.policy_name}: {exc.reason}")
```

The built-in **DefaultSafePolicyEngine**:

- allows **pure**, **read**, **ai**
- denies **io**, **external** by default

Timeout classification is derived from `ExecutionContext.policy.timeout_seconds` and the measured runtime.

## Audit

Audit is built on top of the execution trace.

```python
from kl_kernel_logic import Kernel, PsiDefinition, PsiEnvelope
from kl_kernel_logic import build_audit_report

psi = PsiDefinition(
    psi_type="config.read",
    domain="config",
    effect="read",
)

envelope = PsiEnvelope(psi=psi, version="1.0")
kernel = Kernel()

trace = kernel.execute(psi=psi, task=lambda: "ok", envelope=envelope)
report = build_audit_report(trace)

print(report.describe())
```

Audit reports are simple, serialisable objects that include:

- **run_id**
- **trace** (from ExecutionTrace.describe())
- **generated_at**
- optional **metadata**

## Repository Structure

```
src/kl_kernel_logic/
    __init__.py
    psi.py
    psi_envelope.py
    kernel.py
    cael.py
    execution_context.py
    policy.py
    audit.py
    examples_foundations/

tests/
docs/
    api_reference.md
    execution_theory_in_code.md
    01-kl-architecture.md
    02-foundational-operations.md
    roadmap.md
```

### Core Modules

- **psi.py** - PsiDefinition and PsiConstraints
- **psi_envelope.py** - versioned envelope
- **kernel.py** - execution kernel and ExecutionTrace
- **cael.py** - CAEL wrapper and CAELConfig
- **execution_context.py** - ExecutionContext and ExecutionPolicy
- **policy.py** - PolicyEngine, PolicyDecision, DefaultSafePolicyEngine
- **audit.py** - AuditReport and builder
- **examples_foundations** - deterministic reference operations

### Documentation

- **[api_reference.md](docs/api_reference.md)** - Complete API reference for 0.3.x
- **[execution_theory_in_code.md](docs/execution_theory_in_code.md)** - Theory to code mapping
- **[01-kl-architecture.md](docs/01-kl-architecture.md)** - Architecture overview
- **[02-foundational-operations.md](docs/02-foundational-operations.md)** - Foundation examples guide
- **[roadmap.md](docs/roadmap.md)** - Development roadmap

## Installation

### From PyPI

```bash
pip install kl-kernel-logic
```

### From source

```bash
git clone https://github.com/lukaspfisterch/kl-kernel-logic.git
cd kl-kernel-logic

python -m venv .venv
# Activate venv as usual

pip install -e .
```

## Quick Start

### Two Execution Modes

KL provides two execution modes:

#### 1. CAEL (Recommended for Production)

Use **CAEL** when you need:
- Policy evaluation and enforcement
- User context and request tracking
- Production-grade execution with governance

```python
from kl_kernel_logic import CAEL, CAELConfig, PsiDefinition, ExecutionContext, ExecutionPolicy

def add(a: int, b: int) -> int:
    return a + b

psi = PsiDefinition(
    psi_type="math.add",
    domain="math",
    effect="pure",
)

ctx = ExecutionContext(
    user_id="user_123",
    request_id="req_456",
    policy=ExecutionPolicy(timeout_seconds=1.0),
)

cael = CAEL(config=CAELConfig())
trace = cael.execute(psi=psi, task=add, ctx=ctx, a=1, b=2)

print(trace.output)          # 3
print(trace.success)         # True
print(trace.runtime_ms)      # float
```

#### 2. Kernel (Low-Level)

Use **Kernel** directly when you need:
- Full control without policy layer
- Testing and development
- Building custom orchestrators

```python
from kl_kernel_logic import Kernel, PsiDefinition

def add(a: int, b: int) -> int:
    return a + b

psi = PsiDefinition(
    psi_type="math.add",
    domain="math",
    effect="pure",
)

kernel = Kernel()
trace = kernel.execute(psi=psi, task=add, a=1, b=2)

print(trace.output)          # 3
print(trace.success)         # True
print(trace.runtime_ms)      # float
```

**Recommendation:** Start with **CAEL** for production. Use **Kernel** for testing or when building custom execution layers.

## Foundations Examples

The `examples_foundations` module contains deterministic operations such as:

- Poisson equation solver in 1D
- Sliding-window smoothing
- Simple trajectory integration

They are used in the test suite and serve as reference operations.

**See also:** [docs/02-foundational-operations.md](docs/02-foundational-operations.md) for detailed examples and patterns.

## Tests

Run all tests:

```bash
pytest
```

The suite covers:

- Psi semantics and constraints
- envelope behaviour
- kernel execution and trace structure
- CAEL policy bridge
- audit report generation
- foundation operations

## Theoretical Foundation

**The KL Execution Theory defines the minimal axioms any controlled execution system must satisfy. KL Kernel Logic is the reference implementation of these axioms.**

The theory defines five core axioms:

- **Δ** (atomic transitions)
- **V** (behaviour sequences)
- **t** (logical time)
- **G** (governance)
- **L** (boundaries)

A separate document describes how these axioms map to the implementation:

**[docs/execution_theory_in_code.md](docs/execution_theory_in_code.md)**

## Roadmap

### Current Focus (0.3.x)

- Maintaining API stability
- Bug fixes and polish
- Enhanced documentation and examples
- CI/CD automation

### Near Future (0.4.0)

- Richer PolicyEngine interface with context and history
- G(V) governance over trace sequences
- Standardized trace export (JSONL, NDJSON)
- Optional constraint validation

### Long Term (0.5.0+)

- Enterprise extensions as separate packages
- Async execution support
- Observability integrations
- Production-scale features

**See:** [docs/roadmap.md](docs/roadmap.md) for complete roadmap, versioning strategy, and non-goals.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

For bug reports and feature requests, please use the [GitHub Issues](https://github.com/lukaspfisterch/kl-kernel-logic/issues).

## License

MIT License. See [LICENSE](LICENSE) for details.

Copyright (c) 2025 Lukas Pfister

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed version history and migration notes.
