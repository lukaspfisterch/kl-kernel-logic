# Changelog

All notable changes to KL Kernel Logic will be documented in this file.

This project follows [Keep a Changelog](https://keepachangelog.com/) and [Semantic Versioning](https://semver.org/).

---

## [0.3.3] – 2025-11-30

**Status:** Minimal, stable, theory-aligned core.

### Changed

- Codebase reduced and consolidated to ~700 LOC
- API surface simplified and frozen for 0.3.x
- Kernel and CAEL execution paths unified and cleaned up
- Policy system reduced to minimal PolicyEngine interface

### Added

- Full API reference (`docs/api_reference.md`)
- Theory-to-code mapping (`docs/execution_theory_in_code.md`)
- Updated architecture overview and examples

### Removed

- Multiprocessing timeout enforcement
- Non-essential utilities and experimental features
- Complex policy adapters not aligned with minimal core

### Fixed

- Type signatures aligned with implementation
- Documentation consistency across all files
- Cross-references and formatting issues

### Theory Alignment

- **Δ** (atomic step) → `Kernel.execute()`
- **V** (behaviour) → list of `ExecutionTrace`
- **t** (logical time) → trace index + runtime
- **G** (governance) → `PolicyEngine`
- **L** (boundaries) → `ExecutionPolicy` + constraints

### Migration Notes

- No breaking changes from 0.3.2
- Removed policy extensions should be implemented in orchestrators

---

## [0.3.1]

Internal refactoring of policy and trace handling.

---

## [0.3.0]

Initial public alpha release.

---

## [0.1.0]

Initial implementation.
