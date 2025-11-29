from kl_kernel_logic.psi import (
    PsiConstraints,
    ALLOWED_SCOPE_VALUES,
    ALLOWED_FORMAT_VALUES,
    ALLOWED_TEMPORAL_VALUES,
    ALLOWED_REVERSIBILITY_VALUES,
)


def test_constraints_accept_valid_values():
    constraints = PsiConstraints(
        scope=next(iter(ALLOWED_SCOPE_VALUES)),
        format=next(iter(ALLOWED_FORMAT_VALUES)),
        temporal=next(iter(ALLOWED_TEMPORAL_VALUES)),
        reversibility=next(iter(ALLOWED_REVERSIBILITY_VALUES)),
    )

    # should not raise
    constraints.validate()
    assert not constraints.is_empty()


def test_constraints_reject_invalid_scope():
    constraints = PsiConstraints(scope="invalid-scope")
    try:
        constraints.validate()
        assert False, "expected ValueError for invalid scope"
    except ValueError as exc:
        assert "Invalid constraint scope" in str(exc)


def test_constraints_reject_invalid_format():
    constraints = PsiConstraints(format="invalid-format")
    try:
        constraints.validate()
        assert False, "expected ValueError for invalid format"
    except ValueError as exc:
        assert "Invalid constraint format" in str(exc)
