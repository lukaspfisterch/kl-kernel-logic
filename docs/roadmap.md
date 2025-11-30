# KL Kernel Logic – Roadmap

**Version 0.3.3 • Minimal Core • Theory Aligned**

---

## 1. Status v0.3.3

**Focus:** Stable baseline

- ~700 LOC core
- Zero external dependencies
- Kernel + CAEL stable
- API Reference and Theory Mapping consistent
- Test suite passing (26/26)
- Public API frozen for 0.3.x line

---

## 2. Short-Term (0.3.x)

**Goal:** Stability, clean surface, no feature creep.

### v0.3.4

- Small examples in repo
- Clearer error messages
- Documentation polish

### v0.3.5

- Bug fixes
- Minor optimizations, no new concepts

---

## 3. Mid-Term (0.4.x)

**Goal:** Minimal extensions for governance without violating theory.

### Enhanced PolicyEngine

- Optional: Access to `ExecutionContext`
- Optional: Access to history (for future G(V))
- No breaking changes to interface

### Trace Sequence Helpers

- Small utilities for working with trace lists
- **Not an orchestrator**, just helpers
- Support for explicit V construction

### Standardized Export

- JSONL trace export format
- No new core structures

---

## 4. Long-Term (0.5.x+)

**Goal:** Optional extensions, keep core minimal.

### Possible Additions

- Async/await support (optional `AsyncKernel`)
- Input/output validation helpers (optional)
- Trace persistence utilities (optional)

**All as optional packages or utilities, never in core.**

---

## Non-Goals

**KL will NOT:**

- ❌ Become a workflow engine (composition is external)
- ❌ Implement distributed execution (violates determinism)
- ❌ Add runtime monitoring to core (observability is external)
- ❌ Provide built-in task libraries (users implement tasks)
- ❌ Add heavy dependencies (core stays zero-dependency)

---

## Versioning

- **0.3.x** – Stability series (API frozen)
- **0.4.x** – Governance extensions (backward-compatible)
- **0.5.x** – Optional utilities (separate packages)
- **1.0.0** – When API proven stable in production use

---

## Decision Log

### Why no built-in workflows?

**Rationale:** Workflow = composition of Δ into V. That's orchestrator territory, not execution substrate. KL provides Δ, orchestrators build V.

### Why no distributed execution?

**Rationale:** Distribution introduces timing non-determinism, violates Δ atomicity axiom. KL executes locally, orchestrators handle distribution.

### Why separate optional packages?

**Rationale:** Most users don't need all features. Core stays minimal and portable. Extensions can have dependencies.

---

**Last Updated:** 2025-11-30  
**Next Review:** Q1 2026
