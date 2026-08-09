from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Capability = Literal["general", "reasoning", "coding", "vision", "research", "audio", "image", "video"]

@dataclass(frozen=True)
class ModelProfile:
    id: str
    capabilities: frozenset[str]
    context: int
    priority: int = 0

MODELS = [
    ModelProfile("techspace", frozenset({"general", "reasoning", "research"}), 128000, 10),
    ModelProfile("techspace-code", frozenset({"general", "coding"}), 128000, 9),
    ModelProfile("techspace-vision", frozenset({"general", "vision"}), 128000, 8),
]

def route(capability: Capability, requested: str | None = None) -> ModelProfile:
    if requested:
        for model in MODELS:
            if model.id == requested and capability in model.capabilities:
                return model
    candidates = [m for m in MODELS if capability in m.capabilities]
    if not candidates:
        candidates = [m for m in MODELS if "general" in m.capabilities]
    return max(candidates, key=lambda m: (m.priority, m.context))
