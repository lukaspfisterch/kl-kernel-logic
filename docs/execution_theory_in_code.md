# Execution Theory in Code

This document maps the abstract axioms from **[KL Execution Theory](https://github.com/lukaspfisterch/kl-execution-theory)** to concrete constructs in KL Kernel Logic.

The goal is to demonstrate that KL Kernel Logic is not an arbitrary design, but a direct implementation of a minimal, domain-neutral execution model.

---

## Overview

**KL Execution Theory** defines five axioms:

1. **Δ (Delta)** - Atomic state transitions
2. **V (Behaviour)** - Ordered sequence of transitions
3. **t (Time)** - Logical time as index
4. **G (Governance)** - Derived policy evaluation
5. **L (Boundaries)** - Derived constraint geometry

**KL Kernel Logic** implements these as Python constructs:

| Axiom | Code Manifestation |
|-------|-------------------|
| Δ | `Kernel.execute()` call |
| V | Sequence of `ExecutionTrace` objects |
| t | `runtime_ms`, `started_at`, `finished_at` |
| G | `PolicyEngine.evaluate()` + `PolicyDecision` |
| L | `ExecutionPolicy` + `DefaultSafePolicyEngine` |

---

## 1. Δ (Atomic State Transition)

### Theory

From `axioms/01_delta.md`:

```
Δ : S → S

A Delta is an indivisible mapping between states.
- Atomic (no observable substructure)
- Deterministic (same input → same output)
- No side channels (no hidden state, randomness, or time dependencies)
```

### Implementation

In KL Kernel Logic, **one Delta = one `Kernel.execute()` call**.

```python
from kl_kernel_logic import Kernel, PsiDefinition

def uppercase(text: str) -> str:
    return text.upper()

psi = PsiDefinition(
    psi_type="text.uppercase",
    domain="text",
    effect="pure"
)

kernel = Kernel()
trace = kernel.execute(psi=psi, task=uppercase, text="hello")
# This entire execution is one Δ
```

**Properties preserved:**

- **Atomicity**: The kernel executes the task once, captures the result, and returns a complete trace. No partial states are observable.
- **Determinism**: Same `psi` + same `task` + same `kwargs` → same `output` (for deterministic tasks).
- **No side channels**: The kernel does not inject randomness, time-dependent logic, or hidden global state into the execution. External dependencies must be explicit in `kwargs`.

---

## 2. V (Behaviour)

### Theory

From `axioms/02_behavior.md`:

```
V = { Δ₀, Δ₁, Δ₂, …, Δₙ }

Behaviour is the ordered sequence of all executed Deltas.
- Total order (no branching, no concurrency)
- Complete (all transitions are in V)
- Sequential determinism (entire sequence is deterministic)
```

### Implementation

In KL, behaviour is **a list of `ExecutionTrace` objects** produced by sequential kernel calls.

```python
from kl_kernel_logic import Kernel, PsiDefinition

kernel = Kernel()

# V - behaviour sequence
traces = []

# Δ₀
trace_0 = kernel.execute(psi=psi_add, task=add, a=1, b=2)
traces.append(trace_0)

# Δ₁
trace_1 = kernel.execute(psi=psi_multiply, task=multiply, a=trace_0.output, b=3)
traces.append(trace_1)

# Δ₂
trace_2 = kernel.execute(psi=psi_format, task=format_result, value=trace_1.output)
traces.append(trace_2)

# traces is now V = { Δ₀, Δ₁, Δ₂ }
```

**Properties preserved:**

- **Total order**: Each trace has an implicit index in the list. The list itself defines the order.
- **Completeness**: All executed operations are captured as traces. Nothing is hidden.
- **Sequential determinism**: Given the same initial state and same sequence of operations, the resulting `traces` list is identical.

---

## 3. t (Logical Time)

### Theory

From `axioms/03_time.md`:

```
t = index(V)

Time is not physical. It is the position of a Delta in the sequence V.
- Derived from behaviour (not fundamental)
- Discrete (integer indices)
- Order-preserving (i < j means Δᵢ happens before Δⱼ)
```

### Implementation

In KL, logical time is represented by:

1. **Index in the trace list** - position in V
2. **`started_at` / `finished_at`** - RFC 3339 timestamps (for human audit)
3. **`runtime_ms`** - duration of single Δ (for performance analysis)

```python
# Logical time = index
for t, trace in enumerate(traces):
    print(f"t={t}: {trace.psi.psi_type}")
    print(f"  Started:  {trace.started_at}")
    print(f"  Finished: {trace.finished_at}")
    print(f"  Runtime:  {trace.runtime_ms}ms")
```

**Properties preserved:**

- **Derived**: Time only exists through execution. No execution → no time.
- **Discrete**: Each trace has a distinct index `t`.
- **Order-preserving**: If `t_i < t_j`, then `traces[t_i]` executed before `traces[t_j]`.

**Important**: The RFC 3339 timestamps (`started_at`, `finished_at`) are **metadata for human audit**. They are not part of the logical time model. Logical time is purely structural (index-based).

---

## 4. G (Governance)

### Theory

From `axioms/04_governance.md`:

```
G = f(V)

Governance is a function over behaviour.
- Non-executing (does not modify V)
- Behaviour-derived (depends only on V)
- Deterministic evaluation (same V → same decision)
- Domain-neutral (structure, not semantics)
```

### Implementation

In KL, governance is implemented through the **`PolicyEngine` interface**.

```python
from kl_kernel_logic import PolicyEngine, PolicyDecision, PsiDefinition

class DefaultSafePolicyEngine(PolicyEngine):
    def evaluate(self, psi: PsiDefinition) -> PolicyDecision:
        effect = (psi.effect or "").strip().lower()
        policy_name = "default_safe_policy"

        if effect in {"pure", "read", "ai"}:
            return PolicyDecision(
                policy_name=policy_name,
                allowed=True,
                reason=f"effect '{effect}' is allowed"
            )

        return PolicyDecision(
            policy_name=policy_name,
            allowed=False,
            reason=f"effect '{effect}' is not allowed"
        )
```

**Properties preserved:**

- **Non-executing**: `PolicyEngine.evaluate()` does not execute the task. It only inspects the `PsiDefinition` and returns a decision.
- **Behaviour-derived**: The decision is based on observable properties (effect class, constraints).
- **Deterministic**: Same `psi` → same `PolicyDecision`.
- **Domain-neutral**: The engine evaluates structure (effect, constraints), not domain semantics.

**Governance over sequences:**

For governance over an entire behaviour sequence V, you would evaluate each trace:

```python
def evaluate_behaviour(traces: List[ExecutionTrace]) -> bool:
    """G(V) - governance function over behaviour."""
    policy_engine = DefaultSafePolicyEngine()
    
    for trace in traces:
        decision = policy_engine.evaluate(trace.psi)
        if not decision.allowed:
            return False  # Behaviour violates policy
    
    return True  # Behaviour is compliant
```

---

## 5. L (Boundaries)

### Theory

From `axioms/05_boundaries.md`:

```
L = g(V)

Boundaries describe which regions of behaviour are permitted or forbidden.
- Behaviour-derived (computed from V)
- Non-executing (does not enforce, only describes)
- Structural (geometry of constraints)
```

### Implementation

In KL, boundaries are expressed through:

1. **`ExecutionPolicy`** - per-request constraint flags
2. **`PsiConstraints`** - declarative governance anchors
3. **`DefaultSafePolicyEngine`** - effect-based safe/unsafe regions

**Example 1: ExecutionPolicy boundaries**

```python
from kl_kernel_logic import ExecutionPolicy

# Define constraint boundaries
policy = ExecutionPolicy(
    allow_network=False,        # Boundary: no external calls
    allow_filesystem=False,     # Boundary: no IO operations
    timeout_seconds=5.0         # Boundary: time limit
)

# These flags describe the allowed region of behaviour
# Enforcement is separate (in CAEL or orchestrator)
```

**Example 2: Effect-based boundaries**

```python
# DefaultSafePolicyEngine defines effect boundaries:

ALLOWED_REGION = {"pure", "read", "ai"}
FORBIDDEN_REGION = {"io", "external"}

# A PsiDefinition with effect="pure" is inside the allowed region
# A PsiDefinition with effect="io" is inside the forbidden region
```

**Example 3: Constraint boundaries**

```python
from kl_kernel_logic import PsiConstraints

constraints = PsiConstraints(
    scope="local",              # Boundary: cannot access system-wide state
    format="json",              # Boundary: must produce JSON output
    temporal="bounded",         # Boundary: must complete in finite time
    reversibility="reversible"  # Boundary: must be undoable
)
```

**Properties preserved:**

- **Behaviour-derived**: Boundaries are evaluated based on observable properties (effect, constraints, policy flags).
- **Non-executing**: `ExecutionPolicy` and `PsiConstraints` do not enforce limits themselves. They describe them. Enforcement happens in CAEL or orchestrator.
- **Structural**: Boundaries define geometry (inside/outside allowed regions), not procedural logic.

**Boundary evaluation over sequences:**

```python
def evaluate_boundaries(traces: List[ExecutionTrace]) -> Dict[str, Any]:
    """L(V) - boundary analysis over behaviour."""
    total_runtime = sum(trace.runtime_ms for trace in traces)
    effects_used = {trace.psi.effect for trace in traces}
    
    return {
        "total_runtime_ms": total_runtime,
        "effects_used": effects_used,
        "within_time_budget": total_runtime < 10000,  # 10s limit
        "within_effect_boundary": effects_used <= {"pure", "read", "ai"}
    }
```

---

## Tests as Proofs

The test suite validates that the implementation preserves the axiom properties:

| Test File | Validates |
|-----------|-----------|
| `test_kernel_basic.py` | Δ properties (atomicity, determinism, exception capture) |
| `test_foundations_flows.py` | V construction (ordered sequences, composition) |
| `test_runtime_ms.py` | t measurement (timing, logical ordering) |
| `test_policy_templates.py` | G evaluation (policy decisions, determinism) |
| `test_constraints.py` | L validation (constraint checking, boundary geometry) |
| `test_audit_report.py` | Trace capture (completeness, serialization) |

---

## Why This Matters

The alignment between theory and implementation provides:

### 1. Replayability

Since V is a complete ordered sequence of Deltas, and each Delta is deterministic, **the entire execution is replayable**.

### 2. Auditability

Governance can be evaluated **without re-executing** the behaviour.

### 3. Domain Portability

The same abstract structure applies across domains:

- **Finance**: Order = Δ, Order book history = V, Risk check = G, Position limits = L
- **Biology**: Reaction = Δ, Reaction pathway = V, Conservation law = G, Concentration bounds = L
- **AI**: Inference = Δ, Inference chain = V, Safety policy = G, Model usage limits = L

KL Kernel Logic provides a **domain-neutral substrate** for all these cases.

### 4. Formal Correctness

The theory provides:

- **Axioms** that define what deterministic execution means
- **Proofs** that properties like replayability emerge from the axioms
- **Test suite** that validates implementation preserves axiom properties

This is not accidental design. It's **axiomatic engineering**.

---

## Summary

KL Kernel Logic is a **concrete realization** of KL Execution Theory:

| **Abstraction** | **Realization** |
|-----------------|-----------------|
| S (state space) | Python input/output structures |
| Δ (atomic transition) | `Kernel.execute()` call |
| V (behaviour) | `List[ExecutionTrace]` |
| t (logical time) | List index + `runtime_ms` |
| T (trace) | `ExecutionTrace` object |
| G (governance) | `PolicyEngine` + evaluation functions |
| L (boundaries) | `ExecutionPolicy` + `PsiConstraints` |

This is not an implementation detail. It's the **design principle**.

The theory guarantees:
- Determinism
- Replayability
- Auditability
- Domain neutrality

The code delivers on that guarantee.

