# Contract Test Matrix (KL Execution Theory -> KL Kernel Logic)

This matrix defines executable Given/When/Then tests derived from KL Execution Theory failure modes and axiom minimal contracts. It is the source of truth for pytest contract tests in kl-kernel-logic v0.5.0 and intentionally stays minimal and deterministic.

## Table of Contents
- Failure Modes Index
- Test Matrix

## Failure Modes Index
- FM-1 Non-deterministic Delta (same state -> different output).
- FM-2 Behaviour incomplete (executed step missing from V).
- FM-3 Logical time ambiguous or not index-based.
- FM-4 Trace not reproducible given same s0 and V.
- FM-5 Governance decision not derivable from V (uses external state).
- FM-6 Boundary violation not deterministically demonstrable from V.
- FM-7 Observational time treated as semantic ordering (t_wall/t_perf used as t_index).
- FM-8 Governance or boundaries execute or modify behaviour.

## Scope / Non-Goals
The theory-based tests cover only axioms and derivations from V. `kernel_meta` is not part of theory verification; tests may check it only against Kernel contracts, not axioms, to avoid implying a theory guarantee.

## Test Matrix

### TM-001 (FM-1, A1-Delta)
- Intent: Verify Delta determinism and purity for a deterministic task.
- Given:
  - A deterministic task function f and a fixed input state s.
  - A Kernel execute call that wraps f into a single Delta.
- When:
  - Execute the same Delta twice with the same input state s.
- Then:
  - Output states are equal.
  - Trace indicates success for both runs and error is None.
  - No output field depends on external time or randomness.
- Notes:
  - Compare only deterministic fields; ignore timestamps if present.
Links: [Axiom 1: Delta](D:/DEV/projects/kl-execution-theory/axioms/01_delta.md)

### TM-002 (FM-2, A2-Behavior)
- Intent: Ensure behaviour V is complete and contains every executed Delta exactly once.
- Given:
  - An orchestrator that records each Kernel execution into a behaviour list V.
  - N deterministic Kernel executions.
- When:
  - The orchestrator appends each execution record to V.
- Then:
  - len(V) == N.
  - Each execution produces exactly one entry in V, and no entry is missing or duplicated.
Links: [Axiom 2: Behavior](D:/DEV/projects/kl-execution-theory/axioms/02_behavior.md)

### TM-003 (FM-4, A2-Behavior)
- Intent: Verify deterministic replay of behaviour and trace equivalence.
- Given:
  - Initial state s0 and a deterministic sequence of Deltas V.
  - A recorded trace T from executing V once.
- When:
  - Execute V again from the same s0 to produce T2.
- Then:
  - Final state from T2 equals final state from T.
  - Trace structure matches (same Delta sequence and state transitions).
- Notes:
  - Ignore t_wall and t_perf fields; compare logical ordering only.
Links: [Axiom 2: Behavior](D:/DEV/projects/kl-execution-theory/axioms/02_behavior.md), [Execution Semantics](D:/DEV/projects/kl-execution-theory/formal/execution_semantics.md)

### TM-004 (FM-3, A3-Time)
- Intent: Ensure logical time is derived from behaviour order.
- Given:
  - A behaviour list V with three executions in known order.
- When:
  - Assign t_index based on position in V.
- Then:
  - t_index values are [0, 1, 2] and map to the corresponding Deltas.
  - Ordering is preserved even if wall clock timestamps are equal.
Links: [Axiom 3: Time](D:/DEV/projects/kl-execution-theory/axioms/03_time.md), [Execution Semantics](D:/DEV/projects/kl-execution-theory/formal/execution_semantics.md)

### TM-005 (FM-7, A3-Time)
- Intent: Prevent use of observational time as semantic ordering.
- Given:
  - Two executions recorded in V order (Delta A then Delta B).
  - t_wall values where B has an earlier timestamp than A.
- When:
  - Derive ordering for any evaluation or replay.
- Then:
  - Ordering follows t_index from V (A before B), not t_wall or t_perf.
Links: [Axiom 3: Time](D:/DEV/projects/kl-execution-theory/axioms/03_time.md), [Execution Semantics](D:/DEV/projects/kl-execution-theory/formal/execution_semantics.md)

### TM-006 (FM-5, A4-Governance)
- Intent: Ensure governance decisions are derived only from behaviour V.
- Given:
  - A deterministic governance function G(V) that reads only V.
  - A fixed V and an external variable (e.g., wall clock) that changes.
- When:
  - Evaluate G(V) before and after the external variable changes.
- Then:
  - Governance decision D is identical for both evaluations.
Links: [Axiom 4: Governance](D:/DEV/projects/kl-execution-theory/axioms/04_governance.md)

### TM-007 (FM-8, A4-Governance)
- Intent: Ensure governance evaluation is non-executing and pure.
- Given:
  - A behaviour list V and a governance evaluation step.
- When:
  - Evaluate governance on V.
- Then:
  - V is unchanged (length and contents identical).
  - No additional Kernel executions occur during evaluation.
Links: [Axiom 4: Governance](D:/DEV/projects/kl-execution-theory/axioms/04_governance.md)

### TM-008 (FM-6, A5-Boundaries)
- Intent: Ensure boundary derivation is deterministic and behaviour-derived.
- Given:
  - A deterministic boundary function L(V) that computes a boundary representation B from V.
  - A fixed V and an external variable (e.g., wall clock) that changes.
- When:
  - Evaluate L(V) before and after the external variable changes.
- Then:
  - Boundary representation B is identical for both evaluations.
Links: [Axiom 5: Boundaries](D:/DEV/projects/kl-execution-theory/axioms/05_boundaries.md)

### TM-009 (FM-8, A5-Boundaries)
- Intent: Ensure boundary evaluation is non-executing and pure.
- Given:
  - A behaviour list V and a boundary evaluation step.
- When:
  - Evaluate boundaries on V.
- Then:
  - V is unchanged (length and contents identical).
  - No additional Kernel executions occur during evaluation.
Links: [Axiom 5: Boundaries](D:/DEV/projects/kl-execution-theory/axioms/05_boundaries.md)
