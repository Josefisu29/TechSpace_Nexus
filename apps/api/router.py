from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class RouteDecision:
    capability: str
    model: str
    reason: str

DEFAULTS = {
    "general": "techspace",
    "reasoning": "techspace-reason",
    "code": "techspace-code",
    "vision": "techspace-vision",
    "research": "techspace-research",
}

def route(prompt: str, requested: str = "auto") -> RouteDecision:
    p = prompt.casefold()
    if requested in DEFAULTS: return RouteDecision(requested, DEFAULTS[requested], "explicit capability")
    if any(x in p for x in ("debug", "python", "javascript", "typescript", "code", "function", "api")):
        return RouteDecision("code", DEFAULTS["code"], "coding intent")
    if any(x in p for x in ("research", "latest", "sources", "cite", "compare studies")):
        return RouteDecision("research", DEFAULTS["research"], "research intent")
    if any(x in p for x in ("image", "screenshot", "photo", "diagram")):
        return RouteDecision("vision", DEFAULTS["vision"], "visual intent")
    if any(x in p for x in ("prove", "derive", "deeply analyze", "reason")):
        return RouteDecision("reasoning", DEFAULTS["reasoning"], "reasoning intent")
    return RouteDecision("general", DEFAULTS["general"], "general intent")
