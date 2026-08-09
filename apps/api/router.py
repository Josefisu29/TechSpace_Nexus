from __future__ import annotations

from dataclasses import dataclass
from model_registry import get_model

@dataclass(frozen=True)
class RouteDecision:
    capability: str
    model: str
    reason: str

ALIASES = {"chat": "general", "code": "coding", "deep_research": "research", "image_understanding": "vision"}

KEYWORDS = {
    "coding": ("debug", "python", "javascript", "typescript", "code", "function", "api", "sql"),
    "research": ("research", "latest", "sources", "cite", "compare studies"),
    "vision": ("image", "screenshot", "photo", "diagram"),
    "reasoning": ("prove", "derive", "deeply analyze", "reason", "math"),
}

CAPABILITY_MODELS = {
    "general": "qwen3",
    "reasoning": "deepseek-r1",
    "coding": "qwen3",
    "vision": "qwen3",
    "research": "qwen3",
}

def route(prompt: str, requested: str = "auto") -> RouteDecision:
    capability = ALIASES.get(requested, requested)
    if capability in CAPABILITY_MODELS and requested != "auto":
        model = get_model(CAPABILITY_MODELS[capability])
        if model and model.enabled and capability in model.capabilities:
            return RouteDecision(capability, model.id, "explicit capability")
    p = prompt.casefold()
    detected = next((c for c, words in KEYWORDS.items() if any(w in p for w in words)), "general")
    model_id = CAPABILITY_MODELS[detected]
    model = get_model(model_id)
    if not model or not model.enabled:
        fallback = get_model("qwen3")
        if not fallback or not fallback.enabled:
            raise RuntimeError("no enabled general model")
        return RouteDecision("general", fallback.id, "fallback model")
    return RouteDecision(detected, model.id, f"{detected} intent")
