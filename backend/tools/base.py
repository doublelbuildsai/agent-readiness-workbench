from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters: dict[str, Any]
    handler: Callable[..., dict[str, Any]]


@dataclass
class ToolCall:
    tool: str
    agent_id: str
    inputs: dict[str, Any]
    outputs: dict[str, Any] = field(default_factory=dict)
    citation: str | None = None


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition) -> None:
        self._tools[tool.name] = tool

    def execute(self, name: str, agent_id: str, **inputs: Any) -> ToolCall:
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")
        definition = self._tools[name]
        outputs = definition.handler(**inputs)
        return ToolCall(tool=name, agent_id=agent_id, inputs=inputs, outputs=outputs)

    def schemas(self) -> list[dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                },
            }
            for tool in self._tools.values()
        ]