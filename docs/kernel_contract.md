# Kernel Contract (v0.5.0)

This document defines Kernel-level guarantees and non-guarantees for kl-kernel-logic. It is implementation-specific and intentionally separate from KL Execution Theory.

## Normative Reference

This contract is normative only with respect to:

- KL Execution Theory v0.1.0  
  https://github.com/lukaspfisterch/kl-execution-theory

## Contract Extraction (Current Surface)
- Kernel.execute calls the task exactly once for valid inputs.
- Kernel.execute never raises; failures are captured in the trace.
- A trace is produced exactly once per execution, including failure.
- CAEL executes steps strictly in order and stops on first failure.
- CAEL emits traces only for executed steps.

## Kernel Contract v0.5.0 (Normative)

### Execution Semantics
- A task MUST be invoked exactly once per execution when inputs are valid.
- A trace MUST be produced exactly once per execution, even on failure.
- No retries, compensation, or recovery logic MUST be performed.

### Determinism Guarantees
Deterministic core fields are:
- psi
- success
- failure_code
- exception_type

Observational and non-deterministic fields are:
- run_id, started_at, finished_at, runtime_ms
- output, error, exception_repr
- metadata, kernel_meta

- Determinism MUST hold across re-runs, machines, and time only when task behavior and inputs are deterministic.
- Observational fields MUST NOT be used for ordering or semantic claims.

### Time Semantics
- Wall-clock timestamps are observational only.
- Logical ordering MUST NOT depend on timestamps.
- Deterministic mode MUST provide fixed time and run_id when providers are not supplied.
- In deterministic mode, runtime_ms MUST be 0.0.

### Failure Taxonomy
Failure codes are normalized and stable:
- OK
- TASK_EXCEPTION
- INVALID_INPUT
- KERNEL_ERROR

Exception messages MAY be recorded but MUST NOT affect determinism.

### Trace Immutability and Auditability
- ExecutionTrace MUST be frozen after creation.
- metadata and kernel_meta MUST be frozen at capture time.
- Trace mutation after creation MUST be forbidden.

### Canonical Trace Representation
- ExecutionTrace.to_dict() MUST provide a canonical mapping.
- ExecutionTrace.to_json() MUST provide canonical JSON with stable key order and ISO-8601 timestamps.
- Non-serializable values MUST be represented explicitly in canonical form.
- ExecutionTrace.digest() MUST hash the canonical form with observational fields excluded.
- The digest MUST exclude: run_id, started_at, finished_at, runtime_ms, output, error, exception_repr, metadata, kernel_meta.

### CAEL (Ordered Execution)
- Steps MUST be validated before execution.
- Execution MUST be strictly ordered.
- Execution MUST stop immediately on the first failure.
- Traces MUST be emitted only for executed steps.
- Failure semantics MUST be unambiguous via CaelResult.failure_code and failure_message.

## Non-Guarantees
- Determinism of task behavior.
- Governance, policy, or boundary evaluation.
- Orchestration beyond ordered execution.
- Domain semantics beyond trace capture.

## Metadata and kernel_meta
- metadata belongs to the execution call and is treated as opaque pass-through.
- kernel_meta is an operational projection and not part of KL Execution Theory.
- Tests may validate kernel_meta only against Kernel contracts, not axioms.

## Relationship to Theory and DBL
- KL Execution Theory defines axioms for behavior and derivations from V.
- Kernel provides an execution substrate and observable projections for higher layers.
- DBL and governance layers are responsible for policy and boundary evaluation.
