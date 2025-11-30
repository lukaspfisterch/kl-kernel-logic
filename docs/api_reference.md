# KL Kernel Logic – API Reference

**Version:** 0.3.4  
**Package:** `kl_kernel_logic`

---

## Overview

KL Kernel Logic provides a compact, deterministic execution substrate. It separates:

- **PsiDefinition** (operation specification)
- **ExecutionContext** (constraints and policy)
- **Kernel** (execution harness)
- **ExecutionTrace** (audit output)

This document defines the **stable public API** for the 0.3.x line.

**Everything not listed here is considered internal.**

---

## Table of Contents

1. [Import Surface](#1-import-surface)
2. [Execution Modes](#2-execution-modes)
3. [PsiDefinition](#3-psidefinition)
4. [PsiConstraints](#4-psiconstraints)
5. [PsiEnvelope](#5-psienvelope)
6. [ExecutionPolicy](#6-executionpolicy)
7. [ExecutionContext](#7-executioncontext)
8. [Kernel](#8-kernel-low-level-execution)
9. [CAEL](#9-cael-controlled-execution)
10. [ExecutionTrace](#10-executiontrace)
11. [PolicyEngine](#11-policyengine)
12. [AuditReport](#12-auditreport)
13. [Complete Examples](#13-complete-examples)
14. [Stability Guarantees](#14-stability-guarantees)
15. [Theory Correspondence](#15-appendix-theory-correspondence)

---

## 1. Import Surface

```python
from kl_kernel_logic import (
    # Core definitions
    PsiDefinition,
    PsiConstraints,
    PsiEnvelope,
    
    # Execution
    Kernel,
    ExecutionTrace,
    CAEL,
    CAELConfig,
    
    # Policy
    PolicyEngine,
    PolicyDecision,
    DefaultSafePolicyEngine,
    PolicyViolationError,
    
    # Context
    ExecutionContext,
    ExecutionPolicy,
    
    # Audit
    AuditReport,
    build_audit_report,
)
```

---

## 2. Execution Modes

KL provides **two execution modes**:

### Mode 1: Direct Kernel (Low-Level)

**Use when:** Full control, no policy layer needed, testing

```python
kernel = Kernel()
trace = kernel.execute(psi=psi, task=task, **kwargs)
```

### Mode 2: CAEL (Recommended)

**Use when:** Policy evaluation, context handling, production use

```python
cael = CAEL(config=CAELConfig())
trace = cael.execute(psi=psi, task=task, ctx=ctx, **kwargs)
```

**Recommendation:** Use **CAEL** for production. Use **Kernel** for testing or when building custom orchestrators.

---

## 3. PsiDefinition

### Purpose

**PsiDefinition is a metadata specification for an operation.**

It **describes:**
- What the operation is (psi_type, domain)
- What effects it may have (effect)
- Which constraints apply (constraints)

It **does not contain:**
- Implementation code
- Input data
- Execution logic

**A Psi is a contract, not code.**

### Type Signature

```python
@dataclass(frozen=True)
class PsiDefinition:
    psi_type: str
    domain: str
    effect: str
    schema_version: str = "1.0"
    constraints: PsiConstraints = field(default_factory=PsiConstraints)
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)
    correlation_id: Optional[str] = None
    criticality: Optional[str] = None
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `psi_type` | `str` | Logical type identifier (e.g., `"math.add"`, `"text.uppercase"`) |
| `domain` | `str` | Domain grouping (e.g., `"math"`, `"text"`, `"ai"`) |
| `effect` | `str` | Effect category (see below) |
| `schema_version` | `str` | Psi schema version (default: `"1.0"`) |
| `constraints` | `PsiConstraints` | Governance constraints |
| `description` | `Optional[str]` | Human-readable description |
| `tags` | `List[str]` | Optional categorization tags |
| `metadata` | `Dict[str, str]` | Additional metadata (JSON-compatible) |
| `correlation_id` | `Optional[str]` | Request correlation identifier for tracing |
| `criticality` | `Optional[str]` | Criticality level: `"low"`, `"medium"`, `"high"` |

### Effect Categories (Convention)

`effect` is a **free-form string**. Common conventions:

| Value | Meaning | DefaultSafePolicyEngine |
|-------|---------|------------------------|
| `"pure"` | Deterministic, no side effects | ✅ Allowed |
| `"read"` | Read-only operations | ✅ Allowed |
| `"ai"` | AI/LLM calls (may be nondeterministic) | ✅ Allowed |
| `"io"` | Filesystem operations | ❌ Denied |
| `"external"` | Network calls | ❌ Denied |

> **Note:** You can define custom effect values for domain-specific policies.

### Methods

```python
def assert_minimal_valid() -> None:
    """Validate required fields (psi_type, domain, effect must be non-empty)"""

def psi_key() -> str:
    """Return stable key: f"{psi_type}@{schema_version}" """

def describe() -> Dict[str, Any]:
    """Return JSON-serializable representation"""

def to_dict() -> Dict[str, Any]:
    """Lossless serialization"""

@classmethod
def from_dict(cls, data: Dict[str, Any]) -> "PsiDefinition":
    """Reconstruct from dict"""
```

### Example

```python
from kl_kernel_logic import PsiDefinition, PsiConstraints

psi = PsiDefinition(
    psi_type="text.uppercase",
    domain="text",
    effect="pure",
    description="Convert text to uppercase",
    constraints=PsiConstraints(
        scope="local",
        format="text",
        temporal="instant",
    ),
    tags=["text-processing", "deterministic"],
    correlation_id="req-abc-123",  # Optional: for tracing
)
```

---

## 4. PsiConstraints

### Purpose

Governance anchors for PsiDefinition. All fields optional, validated on demand.

### Type Signature

```python
@dataclass(frozen=True)
class PsiConstraints:
    scope: Optional[str] = None          # "local", "session", "system"
    format: Optional[str] = None         # "opaque", "text", "json"
    temporal: Optional[str] = None       # "instant", "bounded", "stream"
    reversibility: Optional[str] = None  # "reversible", "irreversible"
    extra: Dict[str, str] = field(default_factory=dict)
```

### Canonical Values

```python
ALLOWED_SCOPE_VALUES = ("local", "session", "system")
ALLOWED_FORMAT_VALUES = ("opaque", "text", "json")
ALLOWED_TEMPORAL_VALUES = ("instant", "bounded", "stream")
ALLOWED_REVERSIBILITY_VALUES = ("reversible", "irreversible")
```

### Methods

```python
def validate() -> None:
    """Validate against canonical sets (raises ValueError if invalid)"""

def is_empty() -> bool:
    """Return True if no constraint is set"""

def to_dict() -> Dict[str, Any]:
    """JSON-serializable representation"""

@classmethod
def from_dict(cls, data: Optional[Dict[str, Any]]) -> "PsiConstraints":
    """Construct from dict"""
```

---

## 5. PsiEnvelope

### Purpose

Versioned transport container for PsiDefinition.

### Type Signature

```python
@dataclass
class PsiEnvelope:
    psi: PsiDefinition
    version: str = "1.0"
    envelope_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    signature: Optional[str] = None
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `psi` | `PsiDefinition` | The wrapped Psi |
| `version` | `str` | Envelope schema version |
| `envelope_id` | `str` | Unique UUID |
| `timestamp` | `str` | ISO 8601 creation timestamp (UTC) |
| `metadata` | `Dict[str, Any]` | Envelope-level metadata |
| `signature` | `Optional[str]` | Optional cryptographic signature |

---

## 6. ExecutionPolicy

### Purpose

Per-request constraint flags.

### Type Signature

```python
@dataclass(frozen=True)
class ExecutionPolicy:
    allow_network: bool = False
    allow_filesystem: bool = False
    timeout_seconds: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `allow_network` | `bool` | Whether network access is permitted |
| `allow_filesystem` | `bool` | Whether filesystem access is permitted |
| `timeout_seconds` | `Optional[float]` | Timeout threshold for **post-execution classification** (not enforcement) |
| `metadata` | `Dict[str, Any]` | Policy-specific metadata |

> **Important:** `timeout_seconds` is used for **classification after execution**, not for interrupting running tasks.

### Methods

```python
def to_dict() -> Dict[str, Any]:
    """Serialize to dict"""

@staticmethod
def from_dict(data: Optional[Dict[str, Any]]) -> "ExecutionPolicy":
    """Reconstruct from dict"""
```

### Example

```python
from kl_kernel_logic import ExecutionPolicy

policy = ExecutionPolicy(
    allow_network=False,
    allow_filesystem=False,
    timeout_seconds=2.0,
)
```

---

## 7. ExecutionContext

### Purpose

Binds policy, identity, and correlation info together.

### Type Signature

```python
@dataclass
class ExecutionContext:
    user_id: str
    request_id: str
    policy: Optional[ExecutionPolicy] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `user_id` | `str` | Logical identity of the caller |
| `request_id` | `str` | Request correlation ID |
| `policy` | `Optional[ExecutionPolicy]` | Execution policy for this request |
| `metadata` | `Dict[str, Any]` | Context-specific metadata |

### Methods

```python
def policy_or_default() -> ExecutionPolicy:
    """Return attached policy or default instance"""

def to_dict() -> Dict[str, Any]:
    """Serialize to dict"""

@staticmethod
def from_dict(data: Dict[str, Any]) -> "ExecutionContext":
    """Reconstruct from dict"""
```

### Example

```python
from kl_kernel_logic import ExecutionContext, ExecutionPolicy

ctx = ExecutionContext(
    user_id="user_123",
    request_id="req_456",
    policy=ExecutionPolicy(
        allow_network=False,
        timeout_seconds=2.0,
    ),
)
```

---

## 8. Kernel (Low-Level Execution)

### Purpose

**Kernel is the minimal execution engine.** It executes a task once and returns a structured trace.

### Important

The Kernel:
- ❌ Does **not** enforce determinism (task implementation does)
- ❌ Does **not** evaluate policies
- ❌ Does **not** guarantee task purity
- ✅ **Does** provide deterministic measurement and tracing

### Type Signature

```python
class Kernel:
    def execute(
        self,
        *,
        psi: PsiDefinition,
        task: Callable[..., Any],
        envelope: Optional[PsiEnvelope] = None,
        parent_trace_id: Optional[str] = None,
        policy_decisions: Optional[Sequence[Mapping[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> ExecutionTrace:
        """
        Execute task and return structured trace.
        
        Exceptions are captured and never bubble up.
        """
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `psi` | `PsiDefinition` | Operation specification |
| `task` | `Callable[..., Any]` | Function to execute |
| `envelope` | `Optional[PsiEnvelope]` | Optional envelope (auto-created if None) |
| `parent_trace_id` | `Optional[str]` | Parent trace for nested execution |
| `policy_decisions` | `Optional[Sequence]` | Policy decisions to attach to trace |
| `metadata` | `Optional[Dict]` | Additional metadata for trace |
| `**kwargs` | `Any` | Arguments passed to `task` |

### Example

```python
from kl_kernel_logic import Kernel, PsiDefinition

def add(a: int, b: int) -> int:
    return a + b

kernel = Kernel()
psi = PsiDefinition(psi_type="math.add", domain="math", effect="pure")

trace = kernel.execute(psi=psi, task=add, a=1, b=2)

print(trace.success)      # True
print(trace.output)       # 3
print(trace.runtime_ms)   # 0.123 (example)
```

---

## 9. CAEL (Controlled Execution)

### Purpose

**CAEL** (Controlled AI Execution Layer) wraps Kernel with policy evaluation and context handling.

### Type Signature

```python
@dataclass
class CAELConfig:
    policy_engine: PolicyEngine = DefaultSafePolicyEngine()
    envelope_version: str = "1.0"

class CAEL:
    def __init__(
        self,
        config: Optional[CAELConfig] = None,
        kernel: Optional[Kernel] = None,
    ):
        ...
    
    def execute(
        self,
        psi: PsiDefinition,
        task: Callable[..., Any],
        ctx: Optional[ExecutionContext] = None,
        envelope: Optional[PsiEnvelope] = None,
        **kwargs: Any,
    ) -> ExecutionTrace:
        """Execute with policy evaluation and context handling."""
```

### Execution Flow

1. **Policy evaluation** - Calls `policy_engine.evaluate(psi)`
2. **Raises PolicyViolationError** if policy denies execution
3. **Envelope construction** - Creates or reuses envelope
4. **Delegates to Kernel** - Calls `kernel.execute()`
5. **Attaches policy decisions** to trace
6. **Timeout classification** based on `ctx.policy.timeout_seconds`

### Example

```python
from kl_kernel_logic import (
    CAEL, CAELConfig,
    PsiDefinition,
    ExecutionContext, ExecutionPolicy,
    PolicyViolationError,
)

def uppercase(text: str) -> str:
    return text.upper()

psi = PsiDefinition(psi_type="text.uppercase", domain="text", effect="pure")

ctx = ExecutionContext(
    user_id="user_123",
    request_id="req_456",
    policy=ExecutionPolicy(timeout_seconds=5.0),
)

cael = CAEL(config=CAELConfig())

try:
    trace = cael.execute(psi=psi, task=uppercase, ctx=ctx, text="hello")
    print(trace.output)  # "HELLO"
except PolicyViolationError as e:
    print(f"Blocked: {e.policy_name} - {e.reason}")
```

---

## 10. ExecutionTrace

### Purpose

Canonical output of Kernel/CAEL execution.

### Type Signature

```python
@dataclass
class ExecutionTrace:
    psi: PsiDefinition
    envelope: PsiEnvelope
    
    success: bool
    output: Any
    error: Optional[str]
    
    started_at: str
    finished_at: str
    runtime_ms: float
    
    trace_id: str = field(default_factory=lambda: str(uuid4()))
    parent_trace_id: Optional[str] = None
    
    policy_decisions: List[Mapping[str, Any]] = field(default_factory=list)
    policy_result: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `psi` | `PsiDefinition` | The executed Psi |
| `envelope` | `PsiEnvelope` | Envelope used for execution |
| `success` | `bool` | `True` if execution completed without error |
| `output` | `Any` | Result produced by task |
| `error` | `Optional[str]` | Error message if `success` is `False` |
| `started_at` | `str` | ISO 8601 start timestamp (UTC) |
| `finished_at` | `str` | ISO 8601 finish timestamp (UTC) |
| `runtime_ms` | `float` | Duration in milliseconds |
| `trace_id` | `str` | Unique UUID for this trace |
| `parent_trace_id` | `Optional[str]` | Parent trace UUID for nested execution |
| `policy_decisions` | `List[Mapping]` | Policy decisions applied |
| `policy_result` | `Optional[str]` | Policy summary: `"allow"`, `"block"`, `"timeout"` |
| `metadata` | `Dict[str, Any]` | Additional trace metadata |

### Methods

```python
def describe() -> Dict[str, Any]:
    """Return JSON-serializable representation"""
```

---

## 11. PolicyEngine

### Purpose

Abstract interface for policy evaluation.

### Type Signature

```python
@dataclass
class PolicyDecision:
    policy_name: str
    allowed: bool
    reason: Optional[str] = None

class PolicyEngine:
    def evaluate(self, psi: PsiDefinition) -> PolicyDecision:
        raise NotImplementedError

class DefaultSafePolicyEngine(PolicyEngine):
    def evaluate(self, psi: PsiDefinition) -> PolicyDecision:
        effect = psi.effect.strip().lower()
        
        if effect in {"pure", "read", "ai"}:
            return PolicyDecision(
                policy_name="default_safe_policy",
                allowed=True,
                reason=f"effect '{effect}' is allowed",
            )
        
        return PolicyDecision(
            policy_name="default_safe_policy",
            allowed=False,
            reason=f"effect '{effect}' is not allowed",
        )
```

### Policy Rules

**DefaultSafePolicyEngine:**
- ✅ **Allows:** `pure`, `read`, `ai`
- ❌ **Denies:** `io`, `external`, and all others

---

## 12. AuditReport

### Purpose

Wraps ExecutionTrace into serializable audit record.

### Type Signature

```python
@dataclass
class AuditReport:
    run_id: str
    trace: Dict[str, Any]
    created_at: str
    metadata: Dict[str, Any] = field(default_factory=dict)

def build_audit_report(
    trace: ExecutionTrace,
    metadata: Optional[Dict[str, Any]] = None,
) -> AuditReport:
    """Build audit report from ExecutionTrace"""
```

### Example

```python
from kl_kernel_logic import build_audit_report, Kernel, PsiDefinition

kernel = Kernel()
psi = PsiDefinition(psi_type="test.op", domain="test", effect="pure")

trace = kernel.execute(psi=psi, task=lambda: "result")
report = build_audit_report(trace, metadata={"tenant": "acme"})

print(report.run_id)       # trace.trace_id
print(report.created_at)   # trace.started_at
print(report.describe())   # JSON-serializable dict
```

---

## 13. Complete Examples

### Example 1: Direct Kernel Usage

```python
from kl_kernel_logic import Kernel, PsiDefinition, PsiConstraints

def add(a: int, b: int) -> int:
    return a + b

psi = PsiDefinition(
    psi_type="math.add",
    domain="math",
    effect="pure",
    constraints=PsiConstraints(scope="local", temporal="instant"),
)

kernel = Kernel()
trace = kernel.execute(psi=psi, task=add, a=10, b=20)

if trace.success:
    print(f"Result: {trace.output}")
    print(f"Runtime: {trace.runtime_ms}ms")
else:
    print(f"Error: {trace.error}")
```

### Example 2: CAEL with Policy and Context

```python
from kl_kernel_logic import (
    CAEL, CAELConfig,
    PsiDefinition,
    ExecutionContext, ExecutionPolicy,
    build_audit_report,
)

def uppercase(text: str) -> str:
    return text.upper()

psi = PsiDefinition(
    psi_type="text.uppercase",
    domain="text",
    effect="pure",
)

ctx = ExecutionContext(
    user_id="user_123",
    request_id="req_456",
    policy=ExecutionPolicy(
        allow_network=False,
        timeout_seconds=1.0,
    ),
)

cael = CAEL(config=CAELConfig())
trace = cael.execute(psi=psi, task=uppercase, ctx=ctx, text="hello")

# Audit
report = build_audit_report(trace)
print(report.describe())
```

---

## 14. Stability Guarantees

### ✅ Guaranteed Stable (0.3.x)

- `PsiDefinition`, `PsiConstraints`, `PsiEnvelope`
- `Kernel.execute()` signature
- `CAEL.execute()` signature
- `ExecutionTrace` fields
- `PolicyEngine` interface
- `ExecutionContext`, `ExecutionPolicy`
- `AuditReport`, `build_audit_report()`

### ❌ Not Guaranteed

- Internal modules (not in `__all__`)
- Helper utilities
- `examples_foundations/` implementations
- Specific `PolicyEngine` implementations beyond interface

---

## 15. Appendix: Theory Correspondence

| Theory | Code | Notes |
|--------|------|-------|
| **Δ** (atomic step) | `Kernel.execute()` | One execution = one Δ |
| **V** (behaviour) | `List[ExecutionTrace]` | Orchestrator builds V |
| **t** (logical time) | List index + `runtime_ms` | Structural time |
| **G** (governance) | `PolicyEngine` + orchestrator | Pre-check + G(V) layer |
| **L** (boundaries) | `ExecutionPolicy` + `PsiConstraints` | Declarative limits |

**For detailed theory mapping, see:** [docs/execution_theory_in_code.md](execution_theory_in_code.md)

---

**End of API Reference v0.3.4**
