# KL – Kernel Logic

KL is a lightweight architectural model for structured AI execution in technical systems.
It separates the logical form of an AI operation from the controlled technical execution that follows from it.

KL consists of two complementary layers:

- **Psi** – the Principle Layer (what an operation is)
- **CAEL** – the Controlled AI Execution Layer (how an operation is carried out)

The complete architecture is documented in **[docs/01-kl-architecture.md](docs/01-kl-architecture.md)**.

---

## 1. Psi – Principle Layer

Psi defines the essential characteristics of an AI operation.
It describes everything that must be known before execution can take place.

Psi covers:

- **Operation type**
  read, write, transform, classify, validate, diagnose

- **Logical binding**
  infrastructure domain, data domain, identity domain, application domain

- **Effect class**
  state changing or non-state changing
  single step or multi-step
  deterministic or nondeterministic effect patterns

- **Structural constraints**
  scope, format, reversibility, temporal or spatial bounds

Psi does not enforce policy.
Psi defines structure and essence.

---

## 2. CAEL – Controlled AI Execution Layer

CAEL receives a Psi description and an execution context and turns it into a controlled, traceable run.

CAEL performs the execution of an operation based on the structure defined by Psi.
It provides technical consistency, controlled execution, and traceability.

CAEL includes:

- Input gate
- Context loader
- Psi-based constraint mapping
- Model orchestrator for LLMs, agents, tools and APIs
- Output validator
- Telemetry and logging

CAEL executes.
Psi defines what is being executed.

---

## 3. Kernel

The Kernel binds Psi and CAEL together.
It validates the operation definition, loads execution context, applies constraints, and orchestrates the controlled run.

The Kernel returns a single bundle `{ psi, execution }` that can be logged, stored, or forwarded into a larger orchestration fabric.

---

## 4. KL Architecture (text diagram)

```text
Clients / Systems / Apps
    |
    v
+------------------------+
|        KL Layer        |
|   (Kernel Logic Core)  |
+------------------------+
        |      |
        |      +------------------------------------------+
        |                                                 |
        v                                                 v
+------------------------+                    +---------------------------+
|          Psi           |                    |           CAEL            |
| Principle Layer        |                    | Controlled AI Execution   |
| (Operation Essence)    |                    | Layer                     |
+------------------------+                    +---------------------------+
| - Operation type       |                    | - Input Gate              |
| - Logical binding      |                    | - Context Loader          |
| - Effect class         |                    | - Psi Constraint Mapping  |
| - Structural limits    |                    | - Model Orchestrator      |
+------------------------+                    | - Output Validator        |
        |                                     | - Telemetry + Logging     |
        +-----------------[structural]--------+---------------------------+
                                                            |
                                                            v
                                                +--------------------------+
                                                |   AI Models and Tools    |
                                                |   (LLMs, Agents, APIs)   |
                                                +--------------------------+
                                                            |
                                                            v
                                                +--------------------------+
                                                | Target Systems and Data  |
                                                | (Infra, Apps, DBs)       |
                                                +--------------------------+
```

---

## 5. Implementation

The Python reference implementation lives under `src/kl_kernel_logic` and provides:

- Psi layer definitions
- CAEL execution layer with policies and tracing
- Kernel binder that unifies Psi and CAEL
- Example operations under `src/kl_kernel_logic/examples/`

A minimal test suite is included in `tests/`.

### Quick Start

**Windows:**
```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest
```

**Linux / macOS:**
```bash
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

---

## 6. Foundational operations

This repository includes deterministic examples called foundational operations.
They act as base operations before any higher level orchestrator is introduced.

- Current shipped example: `src/kl_kernel_logic/examples/text_simplify.py`
- Planned foundational set (see [docs/02-foundational-operations.md](docs/02-foundational-operations.md)) to live under `src/kl_kernel_logic/examples_foundations/`

Each foundational example defines:

- a `PsiDefinition` with operation type, logical binding, effect class, constraints  
- an `ExecutionPolicy` with realistic boundaries  
- a Kernel run that returns a bundled `{ psi, execution }` record, including trace and audit events

---

## 7. Integration with DBL

This bundle can be consumed by higher-level components such as a Deterministic Boundary Layer or other policy engines.
See the [`deterministic-boundary-layer`](../deterministic-boundary-layer) repository for integration patterns.

---

## Further Reading

For full architectural details, see: **[docs/01-kl-architecture.md](docs/01-kl-architecture.md)**
