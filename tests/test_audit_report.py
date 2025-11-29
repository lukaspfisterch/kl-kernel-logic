from kl_kernel_logic import (
    PsiDefinition,
    PsiEnvelope,
)
from kl_kernel_logic.kernel import Kernel
from kl_kernel_logic.audit import build_audit_report


def test_audit_report_contains_psi_and_envelope():
    psi = PsiDefinition(
        psi_type="config.read",
        domain="config",
        effect="read",
    )

    envelope = PsiEnvelope(psi=psi, version="1.0")
    kernel = Kernel()

    trace = kernel.execute(psi=psi, task=lambda: "ok", envelope=envelope)
    report = build_audit_report(trace)

    data = report.describe()
    assert "generated_at" in data
    assert data["trace"]["psi"]["domain"] == "config"
    assert data["trace"]["envelope"]["envelope_id"] == envelope.envelope_id
