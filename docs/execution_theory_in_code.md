# Execution Theory in Code

**KL Execution Theory v1.0 defines the minimal 5-element chain for deterministic, auditable execution. KL Kernel Logic is the reference implementation of this theory.**

This document maps the abstract 5-element chain (Δ → V → t → G(V) → SS) to concrete constructs in KL Kernel Logic, demonstrating that KL Kernel Logic is not an arbitrary design, but a direct implementation of a minimal, domain-neutral execution model.

**See also:** [kl_execution_theory_v1.md](kl_execution_theory_v1.md) for the complete formal specification.

---

## Overview

**KL Execution Theory v1.0** defines the 5-element execution chain:

```
Δ → V → t → G(V) → SS
```

1. **Δ (Delta)** - Atomic state transition
2. **V (Behaviour)** - Ordered sequence of transitions
3. **t (Time)** - Logical time derived from position in V
4. **G(V) (Governance)** - Policy function evaluated over behaviour
5. **SS (Shadow State)** - Derived audit state from governance evaluation

**KL Kernel Logic** implements these as Python constructs:

| Element | Code Manifestation |
|---------|-------------------|
| Δ | `Kernel.execute()` call |
| V | Sequence of `ExecutionTrace` objects |
| t | List index + `runtime_ms`, `started_at`, `finished_at` |
| G(V) | `PolicyEngine.evaluate()` + governance over trace sequences |
| SS | `ExecutionTrace` records + `AuditReport` + trace persistence |

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

## 4. G(V) (Governance Function)

### Theory

From KL Execution Theory v1.0:

```
G : V → D

Governance is a function that evaluates the entire behaviour sequence V and produces a decision D.
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

## 5. SS (Shadow State)

### Theory

From KL Execution Theory v1.0:

```
SS = G(V) evaluated and persisted

The Shadow State is the derived governance state that emerges from applying 
the governance function G over the behaviour V.
- Derived (computed from V via G)
- Persistent (recorded for audit, replay, compliance)
- Non-executing (does not affect future execution)
- Complete (captures all governance decisions)
```

### Implementation

In KL, Shadow State is expressed through:

1. **`ExecutionTrace`** - records each Δ with governance metadata
2. **`AuditReport`** - aggregates governance data
3. **`PolicyDecision`** - embedded governance decisions
4. **Trace persistence** - external storage for audit

**Example 1: Shadow State in ExecutionTrace**

```python
from kl_kernel_logic import Kernel, PsiDefinition

psi = PsiDefinition(
    psi_type="math.add",
    domain="math",
    effect="pure"
)

kernel = Kernel()
trace = kernel.execute(psi=psi, task=lambda a, b: a + b, a=1, b=2)

# trace is part of Shadow State - it records:
# - What was executed (psi)
# - What was the result (output)
# - When it happened (started_at, finished_at)
# - How long it took (runtime_ms)
# - Whether it succeeded (success)
```

**Example 2: Shadow State with governance**

```python
from kl_kernel_logic import CAEL, CAELConfig, ExecutionContext, ExecutionPolicy

psi = PsiDefinition(
    psi_type="io.write",
    domain="io",
    effect="io"
)

ctx = ExecutionContext(
    user_id="user_123",
    policy=ExecutionPolicy(allow_filesystem=False)
)

cael = CAEL(config=CAELConfig())

try:
    trace = cael.execute(psi=psi, task=some_io_task, ctx=ctx)
except PolicyViolationError as exc:
    # The policy decision is part of Shadow State
    # It records: what was attempted, why it was blocked, when
    pass
```

**Example 3: Shadow State aggregation**

```python
from kl_kernel_logic import build_audit_report

# V - behaviour sequence
traces = [trace_0, trace_1, trace_2]

# SS - shadow state for each trace
for trace in traces:
    report = build_audit_report(trace)
    # report contains:
    # - run_id
    # - trace details (psi, output, timing)
    # - generated_at timestamp
    # Store report for compliance/audit
```

**Properties preserved:**

- **Derived**: Shadow State is computed from execution traces via governance evaluation.
- **Persistent**: Traces and audit reports can be stored externally (JSONL, database).
- **Non-executing**: Shadow State observes and records, does not command.
- **Complete**: All governance decisions, policy evaluations, and execution outcomes are captured.

**Shadow State evaluation over sequences:**

```python
def analyze_shadow_state(traces: List[ExecutionTrace]) -> Dict[str, Any]:
    """Analyze Shadow State (governance record) from behaviour V."""
    total_runtime = sum(trace.runtime_ms for trace in traces)
    effects_used = {trace.psi.effect for trace in traces}
    success_count = sum(1 for trace in traces if trace.success)
    
    return {
        "total_transitions": len(traces),
        "successful_transitions": success_count,
        "total_runtime_ms": total_runtime,
        "effects_used": effects_used,
        "governance_compliant": all(
            trace.psi.effect in {"pure", "read", "ai"} 
            for trace in traces
        )
    }
```

---

## Tests as Proofs

The test suite validates that the implementation preserves the 5-element chain properties:

| Test File | Validates |
|-----------|-----------|
| `test_kernel_basic.py` | Δ properties (atomicity, determinism, exception capture) |
| `test_foundations_flows.py` | V construction (ordered sequences, composition) |
| `test_runtime_ms.py` | t measurement (timing, logical ordering) |
| `test_policy_templates.py` | G(V) evaluation (policy decisions, determinism) |
| `test_audit_report.py` | SS capture (trace completeness, serialization, audit records) |
| `test_constraints.py` | Constraint validation (governance anchoring) |

---

## Why This Matters

The alignment between theory and implementation provides:

### 1. Replayability

Since V is a complete ordered sequence of Deltas, and each Delta is deterministic, **the entire execution is replayable**.

### 2. Auditability

Governance can be evaluated **without re-executing** the behaviour.

### 3. Domain Portability

The same 5-element chain applies across domains:

- **Finance**: Order = Δ, Order book = V, t = trade sequence index, Risk check = G(V), Audit log = SS
- **Biology**: Reaction = Δ, Pathway = V, t = reaction sequence index, Conservation law = G(V), Lab record = SS
- **AI**: Inference = Δ, Inference chain = V, t = call sequence index, Safety policy = G(V), Inference trace = SS
- **Computation**: Function call = Δ, Call stack = V, t = execution index, Resource policy = G(V), Execution log = SS

KL Kernel Logic provides a **domain-neutral substrate** for all these cases.

### 4. Formal Correctness

The theory provides:

- **5-element chain** (Δ → V → t → G(V) → SS) that defines deterministic execution
- **Formal specification** in [docs/kl_execution_theory_v1.md](kl_execution_theory_v1.md)
- **Properties** that emerge from the chain (replayability, auditability, determinism)
- **Test suite** that validates implementation preserves chain properties

This is not accidental design. It's **axiomatic engineering**.

---

## Summary

KL Kernel Logic is a **concrete realization** of KL Execution Theory v1.0:

| **Abstraction** | **Realization** |
|-----------------|-----------------|
| S (state space) | Python input/output structures |
| Δ (atomic transition) | `Kernel.execute()` call |
| V (behaviour) | `List[ExecutionTrace]` |
| t (logical time) | List index + `runtime_ms` |
| G(V) (governance function) | `PolicyEngine` + evaluation over trace sequences |
| SS (shadow state) | `ExecutionTrace` + `AuditReport` + trace persistence |

The 5-element chain is fully implemented:

```
Δ → V → t → G(V) → SS
```

This is not an implementation detail. It's the **design principle**.

The theory guarantees:
- Deterministic execution
- Replayable behaviour
- Complete auditability
- Transparent governance
- Domain neutrality

The code delivers on that guarantee.

