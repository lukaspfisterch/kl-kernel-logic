"""
Example: simple text simplification under KL.

This module can be run directly:
    python -m kl_kernel_logic.examples.text_simplify
"""

from typing import Any, Dict

from kl_kernel_logic import (
    PsiDefinition,
    PsiConstraints,
    ExecutionPolicy,
    ExecutionContext,
    CAEL,
    CAELConfig,
)


def simplify_text(text: str) -> str:
    """
    Very small stand in for an AI operation.

    In a real system this could call an LLM or a specialised service.
    """
    return " ".join(text.strip().split()).lower()


def build_psi() -> PsiDefinition:
    return PsiDefinition(
        psi_type="application.text_simplify",
        domain="application",
        effect="pure",
        description="Input is plain text, output is simplified plain text.",
        constraints=PsiConstraints(
            scope="text",
            format="plain text",
        ),
    )


def build_context() -> ExecutionContext:
    policy = ExecutionPolicy(
        allow_network=False,
        allow_filesystem=False,
        max_tokens=None,
        timeout_seconds=5,
    )
    return ExecutionContext(
        user_id="demo-user",
        request_id="demo-request-001",
        policy=policy,
    )


def run_example() -> Dict[str, Any]:
    psi = build_psi()
    ctx = build_context()

    input_text = "  This Is   A DEMO Text   with   Irregular   spacing. "

    cael = CAEL(config=CAELConfig())
    trace = cael.execute(
        psi=psi,
        task=simplify_text,
        ctx=ctx,
        text=input_text,
    )
    return trace.describe()


if __name__ == "__main__":
    from pprint import pprint

    pprint(run_example())
