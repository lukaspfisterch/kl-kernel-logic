import pytest

from kl_kernel_logic import (
    PsiDefinition,
)
from kl_kernel_logic.cael import CAEL, CAELConfig, PolicyViolationError
from kl_kernel_logic.policy import DefaultSafePolicyEngine, PolicyEngine, PolicyDecision


def dummy_task() -> str:
    return "ok"


def test_default_safe_policy_allows_pure_operations():
    """DefaultSafePolicyEngine should allow effect='pure' operations."""
    psi = PsiDefinition(
        psi_type="math.calculation",
        domain="math",
        effect="pure",
    )

    cael = CAEL(config=CAELConfig(policy_engine=DefaultSafePolicyEngine()))
    
    # Should execute without raising
    trace = cael.execute(psi=psi, task=dummy_task)
    assert trace.success is True


def test_default_safe_policy_allows_read_operations():
    """DefaultSafePolicyEngine should allow effect='read' operations."""
    psi = PsiDefinition(
        psi_type="config.read",
        domain="config",
        effect="read",
    )

    cael = CAEL(config=CAELConfig(policy_engine=DefaultSafePolicyEngine()))
    
    # Should execute without raising
    trace = cael.execute(psi=psi, task=dummy_task)
    assert trace.success is True


def test_default_safe_policy_blocks_io_operations():
    """DefaultSafePolicyEngine should block effect='io' operations."""
    psi = PsiDefinition(
        psi_type="filesystem.write",
        domain="io",
        effect="io",
    )

    cael = CAEL(config=CAELConfig(policy_engine=DefaultSafePolicyEngine()))

    with pytest.raises(PolicyViolationError) as exc_info:
        cael.execute(psi=psi, task=dummy_task)
    
    assert "default_safe" in exc_info.value.policy_name
    assert "io" in exc_info.value.reason.lower()


def test_default_safe_policy_blocks_external_operations():
    """DefaultSafePolicyEngine should block effect='external' operations."""
    psi = PsiDefinition(
        psi_type="api.call",
        domain="external",
        effect="external",
    )

    cael = CAEL(config=CAELConfig(policy_engine=DefaultSafePolicyEngine()))

    with pytest.raises(PolicyViolationError) as exc_info:
        cael.execute(psi=psi, task=dummy_task)
    
    assert "default_safe" in exc_info.value.policy_name
    assert "external" in exc_info.value.reason.lower()


def test_default_safe_policy_allows_ai_operations():
    """DefaultSafePolicyEngine should allow effect='ai' operations (marked as nondeterministic)."""
    psi = PsiDefinition(
        psi_type="llm.generate",
        domain="ai",
        effect="ai",
    )

    cael = CAEL(config=CAELConfig(policy_engine=DefaultSafePolicyEngine()))
    
    # Should execute without raising
    trace = cael.execute(psi=psi, task=dummy_task)
    assert trace.success is True


def test_custom_policy_engine():
    """Test that custom PolicyEngine implementations work correctly."""
    
    class StrictPolicyEngine(PolicyEngine):
        """Custom policy that blocks everything except 'pure'."""
        
        def evaluate(self, psi) -> PolicyDecision:
            if psi.effect == "pure":
                return PolicyDecision(
                    policy_name="strict",
                    allowed=True,
                    reason="pure operation allowed"
                )
            return PolicyDecision(
                policy_name="strict",
                allowed=False,
                reason=f"effect '{psi.effect}' is not allowed under strict policy"
            )
    
    # Pure should work
    psi_pure = PsiDefinition(psi_type="calc", domain="math", effect="pure")
    cael = CAEL(config=CAELConfig(policy_engine=StrictPolicyEngine()))
    trace = cael.execute(psi=psi_pure, task=dummy_task)
    assert trace.success is True
    
    # Read should be blocked
    psi_read = PsiDefinition(psi_type="config.read", domain="config", effect="read")
    with pytest.raises(PolicyViolationError) as exc_info:
        cael.execute(psi=psi_read, task=dummy_task)
    
    assert "strict" in exc_info.value.policy_name
    assert "read" in exc_info.value.reason.lower()
