"""
Kernel Logic

Connects Psi (principle layer) and CAEL (execution layer)
into a unified execution flow.
"""

from typing import Any, Dict, Callable
from .psi import PsiDefinition
from .cael import CAELExecutor, ExecutionContext


class Kernel:
    """
    Kernel for KL that binds Psi descriptions and CAEL executions.

    Input: PsiDefinition and ExecutionContext
    Output: combined description and execution record
    """

    def __init__(self) -> None:
        self.executor = CAELExecutor()

    def execute(
        self,
        psi: PsiDefinition,
        ctx: ExecutionContext,
        task: Callable[..., Any],
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Execute a task under KL.

        The result bundles the Psi description with the CAEL execution record.
        """
        psi_info = psi.describe()
        execution_result = self.executor.run(task, ctx, **kwargs)

        return {
            "psi": psi_info,
            "execution": execution_result,
        }
