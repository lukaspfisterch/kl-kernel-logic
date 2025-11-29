## Composition and Workflows

KL intentionally does not prescribe a workflow model.
Workflows and envelope chaining should be implemented in higher layers
(DBL, execution gateways) by using:

- Psi metadata
- Envelope metadata
- External workflow engines

If needed, a future version may add an optional `parent_envelope_id`
field to `PsiEnvelope`, but the current 0.3 series keeps the core
contract minimal.

## Enterprise Extensions (not part of 0.3 core)

- JSON schema based input and output validation for Psi constraints
- Envelope digests and cryptographic signatures based on `PsiEnvelope.compute_digest`
- Dedicated trace stores (JSONL, SQLite, remote HTTP)
- Multi tenant separation and policy profiles per tenant
