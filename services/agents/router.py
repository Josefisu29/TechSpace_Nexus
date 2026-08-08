from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class Route:
    name: str
    model: str
    reason: str

RULES = (
    ("code", ("code", "debug", "python", "javascript", "typescript", "react", "sql"), "coding"),
    ("research", ("research", "sources", "latest", "compare", "study"), "research"),
    ("vision", ("image", "screenshot", "diagram", "photo"), "vision"),
    ("reasoning", ("prove", "derive", "why", "analyze", "reason"), "reasoning"),
)

def route(prompt: str) -> Route:
    text = prompt.casefold()
    for model, keywords, name in RULES:
        if any(k in text for k in keywords):
            return Route(name, model, f"Matched {name} task signals")
    return Route("general", "techspace", "Default general assistant route")
