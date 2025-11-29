"""
Tests for PsiDefinition validation.
"""

import pytest

import kl_kernel_logic as kl


def test_psi_with_all_required_fields_is_valid():
    """PsiDefinition with all required fields should pass validation."""
    psi = kl.PsiDefinition(
        psi_type="test.operation",
        domain="test",
        effect="pure",
    )
    
    # Should not raise
    psi.assert_minimal_valid()


def test_psi_with_empty_psi_type_raises():
    """PsiDefinition with empty psi_type should raise ValueError."""
    psi = kl.PsiDefinition(
        psi_type="",
        domain="test",
        effect="pure",
    )
    
    with pytest.raises(ValueError, match="psi_type must not be empty"):
        psi.assert_minimal_valid()


def test_psi_with_empty_domain_raises():
    """PsiDefinition with empty domain should raise ValueError."""
    psi = kl.PsiDefinition(
        psi_type="test.operation",
        domain="",
        effect="pure",
    )
    
    with pytest.raises(ValueError, match="domain must not be empty"):
        psi.assert_minimal_valid()


def test_psi_with_empty_effect_raises():
    """PsiDefinition with empty effect should raise ValueError."""
    psi = kl.PsiDefinition(
        psi_type="test.operation",
        domain="test",
        effect="",
    )
    
    with pytest.raises(ValueError, match="effect must not be empty"):
        psi.assert_minimal_valid()


def test_psi_key_generation():
    """psi_key() should combine psi_type and version."""
    psi = kl.PsiDefinition(
        psi_type="test.operation",
        domain="test",
        effect="pure",
        version="0.3.0",
    )
    
    key = psi.psi_key()
    assert key == "test.operation@0.3.0"


def test_psi_describe_includes_all_fields():
    """describe() should include all PsiDefinition fields."""
    psi = kl.PsiDefinition(
        psi_type="test.operation",
        domain="test",
        effect="pure",
        version="0.3.0",
        description="Test operation",
        tags=["test", "demo"],
        metadata={"key": "value"},
    )
    
    data = psi.describe()
    
    assert data["psi_type"] == "test.operation"
    assert data["domain"] == "test"
    assert data["effect"] == "pure"
    assert data["version"] == "0.3.0"
    assert data["description"] == "Test operation"
    assert data["tags"] == ["test", "demo"]
    assert data["metadata"]["key"] == "value"
    assert "constraints" in data

