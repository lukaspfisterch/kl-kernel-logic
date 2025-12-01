# KL Architecture

KL is a lightweight architectural model for structured AI execution in technical systems.
It focuses on the logical form of an AI operation and on the controlled execution path that follows from it.

KL implements **KL Execution Theory v1.0**, a formal execution model based on the 5-element chain: Δ → V → t → G(V) → SS.

KL consists of two complementary layers:

- **Psi**: the Principle Layer, describes what an operation is (defines Δ)
- **CAEL**: the Controlled AI Execution Layer, describes how an operation is carried out (executes Δ, produces V and SS)

---

## 1. Psi Layer: structure and essence

Psi defines the essential characteristics of an AI operation before it runs.

Psi answers:

- What type of operation is this  
  (read, write, transform, classify, validate, diagnose)
- Where is the logical binding  
  (infrastructure domain, data domain, identity domain, application domain)
- What effect class applies  
  (state changing versus non state changing, single step versus multi step,
   deterministic versus nondeterministic)
- Which structural constraints exist  
  (scope, format, reversibility, temporal or spatial bounds)

The Psi layer does not enforce policy.
It defines structure and essence in a compact, serialisable form.

---

## 2. CAEL Layer: controlled execution

CAEL receives a Psi description and an execution context.
It is responsible for:

- Applying execution policy  
  (network access, filesystem access, token limits, timeout)
- Checking preconditions derived from policy flags
- Executing the concrete task
- Recording a minimal execution trace

CAEL separates functional parameters from control flags.
The task sees only its functional input, CAEL enforces guardrails around it.

---

## 3. Kernel: binding Psi and CAEL

The KL Kernel binds Psi and CAEL into a single execution flow.

High level steps:

1. A caller creates a `PsiDefinition` that describes the operation.
2. A caller creates an `ExecutionContext` with a concrete `ExecutionPolicy`.
3. The caller chooses a task function that implements the operation.
4. The Kernel executes the task through CAEL under the given context.
5. The Kernel returns a combined record:

   - `psi`: the logical description of the operation
   - `execution`: result and trace from CAEL

This combined record can be logged, stored, or inspected as part of a larger AI execution fabric.

---

## 4. Theoretical Foundation

KL Kernel Logic implements **KL Execution Theory v1.0**, a formal 5-element execution chain:

```
Δ → V → t → G(V) → SS
```

**Architecture-to-Theory Mapping:**

| Theory Element | KL Architecture Component |
|----------------|---------------------------|
| Δ (Atomic transition) | `Kernel.execute()` call |
| V (Behaviour sequence) | Sequence of `ExecutionTrace` objects |
| t (Logical time) | Trace list index + timing metadata |
| G(V) (Governance function) | `PolicyEngine` + CAEL policy evaluation |
| SS (Shadow State) | `ExecutionTrace` + `AuditReport` + persistence |

**Layer Mapping:**

- **Psi layer** defines the intent of Δ (what will be transitioned)
- **CAEL layer** executes Δ under governance G(V)
- **Kernel** produces V (behaviour) and SS (shadow state)

The architecture is a direct realization of the theory. See [kl_execution_theory_v1.md](kl_execution_theory_v1.md) for the complete formal specification.

---

## 5. Extension Points

KL is intentionally small.
Typical extension points:

- Additional operation types or effect classes in the Psi layer
- Richer constraints, for example structured validation rules
- Extended policies in CAEL  
  (rate limits, resource classes, tenant boundaries)
- Integration with external audit stores or trace systems
- Higher level orchestration that chains several Kernel executions

The core idea stays stable:
separate the question what an operation is from the question how it is executed,
and connect both through a small, inspectable Kernel.
