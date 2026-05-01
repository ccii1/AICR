from __future__ import annotations

from typing import Callable, Dict


class MCPBridge:
    def __init__(self) -> None:
        self._tools: Dict[str, Callable[[str], str]] = {}

    def register_tool(self, name: str, handler: Callable[[str], str]) -> None:
        self._tools[name] = handler

    def call(self, tool_name: str, payload: str) -> str:
        if tool_name not in self._tools:
            return f"MCP tool not found: {tool_name}"
        return self._tools[tool_name](payload)
