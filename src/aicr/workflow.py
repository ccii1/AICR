from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List


@dataclass
class WorkflowContext:
    user_query: str
    state: Dict[str, str] = field(default_factory=dict)


class WorkflowEngine:
    def __init__(self) -> None:
        self._steps: List[tuple[str, Callable[[WorkflowContext], None]]] = []

    def add_step(self, name: str, handler: Callable[[WorkflowContext], None]) -> None:
        self._steps.append((name, handler))

    def run(self, context: WorkflowContext) -> WorkflowContext:
        for step_name, handler in self._steps:
            handler(context)
            context.state["last_step"] = step_name
        return context
