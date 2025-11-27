# KL – Kernel Logic

KL is a lightweight architectural model for structured AI execution in technical systems.  
It focuses on the logical form of an AI operation and the controlled execution path that follows from it.

KL consists of two complementary layers:

- **Psi** – the Principle Layer (what an operation *is*)  
- **CAEL** – the Controlled AI Execution Layer (how an operation *is carried out*)

---

## 1. Psi – Principle Layer

Psi defines the essential characteristics of an AI operation.  
It describes the elements that must be known before execution can take place.

Psi covers:

- **Operation type**  
  read, write, transform, classify, validate, diagnose

- **Logical binding**  
  infrastructure domain, data domain, identity domain, application domain

- **Effect class**  
  state-changing or non-state-changing  
  single-step or multi-step  
  deterministic or nondeterministic effect patterns

- **Structural constraints**  
  scope, format, reversibility, temporal or spatial bounds

Psi does not enforce policy.  
Psi defines structure and essence.

---

## 2. CAEL – Controlled AI Execution Layer

CAEL performs the execution of an operation based on the structure defined by Psi.  
It acts as the technical surface that ensures consistency, context and traceability.

CAEL includes:

- Input gate  
- Context loader  
- Psi-based constraint mapping  
- Model orchestrator (LLMs, agents, tools, APIs)  
- Output validator  
- Telemetry and logging

CAEL executes.  
Psi defines what is being executed.

---

## 3. KL Architecture (text diagram)

```text
Clients / Systems / Apps
    |
    v
+------------------------+
|        KL Layer        |
|   (Kernel Logic Core)  |
+------------------------+
        |      |
        |      +------------------------------------------+
        |                                                 |
        v                                                 v
+------------------------+                    +---------------------------+
|          Psi           |                    |           CAEL            |
| Principle Layer        |                    | Controlled AI Execution   |
| (Operation Essence)    |                    | Layer                     |
+------------------------+                    +---------------------------+
| - Operation type       |                    | - Input Gate              |
| - Logical binding      |                    | - Context Loader          |
| - Effect class         |                    | - Psi Constraint Mapping  |
| - Structural limits    |                    | - Model Orchestrator      |
+------------------------+                    | - Output Validator        |
        |                                     | - Telemetry + Logging     |
        +-----------------[structural]--------+---------------------------+
                                                            |
                                                            v
                                                +--------------------------+
                                                |   AI Models / Tools      |
                                                |   (LLMs, Agents, APIs)   |
                                                +--------------------------+
                                                            |
                                                            v
                                                +--------------------------+
                                                | Target Systems and Data  |
                                                | (Infra, Apps, DBs)       |
                                                +--------------------------+
