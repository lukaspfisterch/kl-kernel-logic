import kl_kernel_logic as kl


def test_basic_execution_roundtrip():
    psi = kl.PsiDefinition(
        psi_type="test.echo_transform",
        domain="test",
        effect="pure",
    )

    def echo(value: str) -> str:
        return value

    kernel = kl.Kernel()
    trace = kernel.execute(psi=psi, task=echo, value="x")
    data = trace.describe()

    assert data["psi"]["domain"] == "test"
    assert data["success"] is True
    assert data["output"] == "x"
    assert data["error"] is None
    assert data["runtime_ms"] is not None
    assert data["runtime_ms"] >= 0.0
