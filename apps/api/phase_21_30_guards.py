from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Role = Literal["user", "operator", "admin", "owner"]

@dataclass(frozen=True)
class ExecutionBudget:
    max_seconds: int = 120
    max_tool_calls: int = 20
    max_tokens: int = 16000

@dataclass(frozen=True)
class ToolPermission:
    name: str
    requires_confirmation: bool = True
    allowed_roles: tuple[Role, ...] = ("user", "operator", "admin", "owner")

DEFAULT_TOOLS = (
    ToolPermission("web.search", False),
    ToolPermission("files.read", False),
    ToolPermission("code.execute", True),
    ToolPermission("shell.execute", True),
    ToolPermission("git.write", True),
)

def can_use_tool(role: Role, tool: ToolPermission) -> bool:
    return role in tool.allowed_roles
