# Changelog

All notable changes to KL Kernel Logic will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2025-11-29

### Added

- **PsiDefinition v0.3.0** - Complete rewrite with flexible string-based architecture
  - New fields: `psi_type` (str), `domain` (str), `effect` (str)
  - Version field (default "0.3.0")
  - Optional `description`, `tags`, and `metadata`
  - `psi_key()` method for stable logical keys
  - `assert_minimal_valid()` for construction-time validation
  - `describe()` method for JSON serialization

- **PsiConstraints** - Structured constraint block for policy anchoring
  - Fields: `scope`, `format`, `temporal`, `reversibility`, `extra`
  - `validate()` method with allowed value sets
  - `is_empty()` helper method
  - `describe()` for serialization

- **PolicyEngine Interface** - Extensible strategy pattern for policy evaluation
  - Abstract base class with `evaluate()` method
  - Returns `PolicyDecision` objects
  - Supports custom implementations

- **DefaultSafePolicyEngine** - Built-in effect-based safety model
  - Allows: `pure` (deterministic), `read` (config/lookup), `ai` (nondeterministic placeholder)
  - Blocks: `io` (filesystem), `external` (network/APIs)
  - Rejects unknown effects by default

- **PolicyDecision** - Structured policy evaluation result
  - Fields: `policy_name`, `allowed`, `reason`, `metadata`
  - `describe()` method for audit trails

- **PolicyViolationError** - Rich exception type replacing old `PolicyViolation`
  - Includes: `policy_name`, `reason`, detailed message
  - Better error context for debugging

- **Test Coverage** - Comprehensive test suite (26/26 passing)
  - Policy engine tests (6 tests for all effect types)
  - Runtime measurement tests (4 tests for runtime_ms)
  - Psi validation tests (6 tests for PsiDefinition validation)
  - Constraint validation tests (4 tests)
  - Foundation flow tests (3 tests)
  - Kernel and timeout tests (2 tests)
  - Audit report test (1 test)

### Changed

- **policy.py** - Complete rewrite
  - Removed enum-based templates
  - Introduced `PolicyEngine` strategy pattern
  - Cleaner evaluation model with structured decisions

- **CAEL** - Migrated to v0.3.0 architecture
  - Now uses single `PolicyEngine` instance (not policy lists)
  - Default: `DefaultSafePolicyEngine()` automatically instantiated
  - Cleaner execution pipeline
  - Preserved timeout precedence logic
  - Preserved `ExecutionContext` compatibility

- **Kernel** - Updated trace serialization
  - Now depends on `PsiDefinition.describe()` and `PsiEnvelope.describe()`
  - Aligned error handling with v0.3.0 models

- **Package Structure** - Standardized exports
  - Updated `__init__.py` exports (removed old policy classes)
  - Added `__version__ = "0.3.0"`
  - Clean public API surface

- **Repository Metadata** - Professional GitHub setup
  - Updated `pyproject.toml` with proper metadata
  - Added license, URLs, classifiers, keywords
  - Added README badges (Python, License, Tests)
  - Added Contributing section
  - Enhanced documentation formatting

### Removed

- **Breaking Changes** (intentional for clean architecture):
  - ❌ `OperationType` enum
  - ❌ `EffectClass` enum
  - ❌ `PolicyTemplate` enum
  - ❌ `Policy` class
  - ❌ `PolicyViolation` exception
  - ❌ `evaluate_policies()` function

### Fixed

- Deterministic timestamp formatting (ISO 8601: `YYYY-MM-DDTHH:MM:SS.mmmZ`)
- `ExecutionTrace.runtime_ms` now properly calculated in Kernel.execute()
- Timestamp precision consistent across all modules (milliseconds)
- Multiprocessing error handling indentation bug in Kernel (line 157)
- Envelope metadata merge edge cases
- Test suite timing issues on Windows (multiprocessing spawn mode)
- Example path resolution in some environments
- README formatting (removed copy artifacts, fixed code blocks)

### Security

- **PolicyEngine Safety Layer**
  - Blocks IO and external operations by default
  - Explicit effect classification required
  - Unknown effects rejected
  
- **Audit Trail**
  - CAEL ensures all executions return full `ExecutionTrace`
  - Context metadata automatically captured
  - `AuditReport` provides deterministic output for governance/SIEM

### Migration Guide

If upgrading from v0.2.0:

1. **Update imports:**
   ```python
   # Old
   from kl_kernel_logic import OperationType, EffectClass, PolicyViolation
   
   # New
   from kl_kernel_logic import PsiDefinition, PsiConstraints, PolicyViolationError
   from kl_kernel_logic.policy import PolicyEngine, DefaultSafePolicyEngine
   ```

2. **Update PsiDefinition:**
   ```python
   # Old
   psi = PsiDefinition(
       operation_type=OperationType.TRANSFORM,
       logical_binding="domain.path",
       effect_class=EffectClass.NON_STATE_CHANGING,
   )
   
   # New
   psi = PsiDefinition(
       psi_type="domain.operation_name",
       domain="domain",
       effect="pure",
   )
   ```

3. **Update Policy Handling:**
   ```python
   # Old
   config = CAELConfig(policies=[Policy(...)])
   
   # New (DefaultSafePolicyEngine used automatically)
   cael = CAEL()  # That's it!
   
   # Or with custom engine
   cael = CAEL(config=CAELConfig(policy_engine=MyCustomEngine()))
   ```

4. **Update Exception Handling:**
   ```python
   # Old
   except PolicyViolation as e:
       print(e.violated_policies)
   
   # New
   except PolicyViolationError as e:
       print(f"{e.policy_name}: {e.reason}")
   ```

---

## [0.2.0] - 2025-11-28

### Added

- **PsiEnvelope** - Versioned metadata transport container
  - UUID envelope identifier
  - Creation timestamp
  - Optional metadata and signature
  
- **ExecutionContext & ExecutionPolicy** - Request-level policy controls
  - Per-request timeout enforcement
  - Network and filesystem flags
  - Token limits for AI operations

- **Policy Templates** - Initial policy system
  - `READ_ONLY` template (blocks write operations)
  - `NO_NETWORK` template (blocks network operations)
  - `evaluate_policies()` function

- **Timeout Support** - Multiprocessing-based execution limits
  - Per-call, context, and config-level timeout precedence
  - Windows and Linux compatibility (spawn context)
  - Graceful termination on timeout

- **AuditReport** - Deterministic audit trail generation
  - `build_audit_report()` helper
  - JSON-serializable output
  - Governance-ready structure

- **Foundation Examples** - Deterministic reference implementations
  - Poisson equation solver (1D)
  - Trajectory integration (1D)
  - Sliding-window smoothing

- **Test Suite** - Comprehensive test coverage
  - Kernel execution tests
  - Policy evaluation tests
  - Timeout enforcement tests
  - Foundation operation tests

### Changed

- Kernel moved to timezone-aware timestamps (ISO 8601)
- PsiDefinition constraints field accepts dict format

---

## [0.1.0] - 2025-11-15

### Added

- Initial prototype implementation
- Basic `PsiDefinition` with enums
- `Kernel` execution engine
- `CAEL` wrapper layer
- Deterministic foundation examples

---

[Unreleased]: https://github.com/lukaspfisterch/kl-kernel-logic/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/lukaspfisterch/kl-kernel-logic/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/lukaspfisterch/kl-kernel-logic/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/lukaspfisterch/kl-kernel-logic/releases/tag/v0.1.0
