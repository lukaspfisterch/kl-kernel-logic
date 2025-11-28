import kl_kernel_logic as kl


def test_basic_execution_roundtrip():
    psi = kl.PsiDefinition(
        operation_type=kl.OperationType.TRANSFORM,
        logical_binding="test.domain",
        effect_class=kl.EffectClass.NON_STATE_CHANGING,
    )

    policy = kl.ExecutionPolicy()
    ctx = kl.ExecutionContext(
        user_id="test-user",
        request_id="req-1",
        policy=policy,
    )

    def echo(value: str) -> str:
        return value

    kernel = kl.Kernel()
    result = kernel.execute(psi, ctx, task=echo, value="x")

    assert result["psi"]["logical_binding"] == "test.domain"
    assert result["execution"]["result"] == "x"
    assert result["execution"]["trace"][0]["stage"] == "start"
    assert result["execution"]["trace"][-1]["stage"] == "end"
