# Release Procedure

This checklist defines the minimal, repeatable release steps for GitHub.

## MUST
- `pytest -q` clean
- Version bump in `src/kl_kernel_logic/__init__.py`
- `CHANGELOG.md` updated
- Tag `vX.Y.Z` created and pushed
- Build check if publishing to PyPI

## SHOULD
- GitHub release created with changelog excerpt
