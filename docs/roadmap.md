# KL Kernel Logic – Roadmap

**Version 0.3.4 • Minimal Core • Theory v1.0 Complete**

---

## 1. Status v0.3.4

**Focus:** v1.0-ready documentation and stable implementation

- ~700 LOC core
- Zero external dependencies
- Kernel + CAEL stable
- **KL Execution Theory v1.0 integrated** (definitive 5-element chain)
- API Reference and Theory Mapping complete
- Test suite passing (26/26)
- Public API frozen for 0.3.x line
- Documentation layer at version-ready quality

---

## 2. Short-Term (0.3.x)

**Goal:** Stability, clean surface, no feature creep.

### v0.3.4 (Current)

- **KL Execution Theory v1.0 integration** (5-element chain: Δ → V → t → G(V) → SS)
- New documentation: `docs/kl_execution_theory_v1.md` (definitive formal specification)
- Updated theory-to-code mapping in `docs/execution_theory_in_code.md`
- README updated with domain-agnostic validation summary
- Architecture documentation aligned with theory

### v0.3.5+

- Bug fixes
- Minor optimizations, no new concepts
- Community feedback integration

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

- **0.3.x** – Stability series (API frozen, theory v1.0 integrated)
- **0.4.x** – Governance extensions (backward-compatible)
- **0.5.x** – Optional utilities (separate packages)
- **1.0.0** – API proven stable in production use

**Path to 1.0.0:**

KL Kernel Logic is approaching 1.0.0 readiness. The theoretical foundation is complete (KL Execution Theory v1.0), the implementation is stable, and the documentation layer reflects version-ready quality. The transition to 1.0.0 will occur when the API has been validated in production environments and community feedback confirms stability.

---

## Decision Log

### Why no built-in workflows?

**Rationale:** Workflow = composition of Δ into V. That's orchestrator territory, not execution substrate. KL provides Δ, orchestrators build V.

### Why no distributed execution?

**Rationale:** Distribution introduces timing non-determinism, violates Δ atomicity axiom. KL executes locally, orchestrators handle distribution.

### Why separate optional packages?

**Rationale:** Most users don't need all features. Core stays minimal and portable. Extensions can have dependencies.

---

**Last Updated:** 2025-12-01  
**Next Review:** Q1 2026
