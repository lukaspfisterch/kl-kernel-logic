# Changelog

All notable changes to KL Kernel Logic will be documented in this file.

This project follows [Keep a Changelog](https://keepachangelog.com/) and [Semantic Versioning](https://semver.org/).

---

## [0.5.0] - 2025-12-26

- Introduced normative kernel contract (RFC-style MUST/MAY)
- Formalized determinism scope and observational fields
- Normalized kernel failure taxonomy
- Enforced immutable, canonical execution traces
- Added trace digest suitable for downstream derivation
- Hardened CAEL validation and failure propagation

This is the first contract-stable kernel release.

---

## [0.4.0] – 2025-12-03

**Status:** Minimal, stable, frozen core.

### Changed

- Radical simplification: 2000 LOC → 700 LOC → **244 LOC** minimal core
- Core reduced to three files: `psi.py`, `kernel.py`, `cael.py`
- Public API frozen: `PsiDefinition`, `Kernel`, `ExecutionTrace`, `CAEL`, `CaelResult`
- Python requirement: 3.11+

### Removed

- `PsiConstraints`, `PsiEnvelope`
- `ExecutionPolicy`, `ExecutionContext`
- `PolicyEngine`, `DefaultSafePolicyEngine`
- `CAELConfig`, `PolicyViolationError`
- `AuditReport`, `build_audit_report`
- All policy, governance, and context handling (moved to higher layers)

### Added

- `CaelResult` as explicit return type for `CAEL.run()`
- Axiom tests (`test_axioms.py`) covering Δ, V, t, determinism, SS
- Public API smoke tests (`test_public_api.py`)

### Theory Alignment

- **Δ** (atomic execution) → `Kernel.execute()` as atomicity of execution and observation
- **V** (behaviour) → `CAEL.run()` establishes total order over execution steps
- **t** (logical time) → observable projections: wall-clock timestamps + monotonic duration
- **G, L** (governance, boundaries) → belong to higher layers

### Migration Notes

- Replace `CAEL(config=CAELConfig())` with `CAEL(kernel=Kernel())`
- Replace `cael.execute(psi, task, ctx, **kwargs)` with `cael.run([(psi, task, kwargs)])`
- Remove all policy/context parameters
- `PsiDefinition` now only has `psi_type`, `name`, `metadata`

---

## [0.3.4] – 2025-12-01

**Status:** Final pre-simplification release.

### Changed

- Renamed `PsiDefinition.version` → `schema_version` for clarity

### Added

- `PsiDefinition.correlation_id`
- `PsiDefinition.criticality`
- `ExecutionTrace.policy_result`

---

## [0.3.3] – 2025-11-30

Codebase reduced to ~700 LOC. API surface simplified.

---

## [0.3.0]

Initial public alpha release.

---

## [0.1.0]

Initial implementation.
