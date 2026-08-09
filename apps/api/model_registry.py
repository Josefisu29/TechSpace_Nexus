from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum

class ModelStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    healthy = "healthy"
    degraded = "degraded"
    offline = "offline"
    retired = "retired"

@dataclass(frozen=True)
class ModelRecord:
    id: str
    provider: str
    revision: str
    license: str
    capabilities: tuple[str, ...]
    context_length: int
    enabled: bool = True
    status: ModelStatus = ModelStatus.pending
    approved: bool = False
    priority: int = 0
    fallbacks: tuple[str, ...] = ()
    metadata: dict = field(default_factory=dict)

REGISTRY: dict[str, ModelRecord] = {}

def register(model: ModelRecord) -> ModelRecord:
    if not model.id or not model.provider or not model.revision:
        raise ValueError("model id, provider and immutable revision are required")
    if model.revision.upper() in {"LATEST", "PIN_REQUIRED"}:
        raise ValueError("production registration requires an immutable pinned revision")
    REGISTRY[model.id] = model
    return model

def approve(model_id: str) -> ModelRecord:
    model = REGISTRY[model_id]
    updated = ModelRecord(**{**asdict(model), "approved": True, "status": ModelStatus.approved})
    REGISTRY[model_id] = updated
    return updated

def set_status(model_id: str, status: ModelStatus) -> ModelRecord:
    model = REGISTRY[model_id]
    updated = ModelRecord(**{**asdict(model), "status": status})
    REGISTRY[model_id] = updated
    return updated

def list_models() -> list[dict]:
    return [asdict(x) for x in REGISTRY.values()]

def get_model(model_id: str) -> ModelRecord | None:
    return REGISTRY.get(model_id)

def candidates(capability: str) -> list[ModelRecord]:
    healthy = {ModelStatus.approved, ModelStatus.healthy}
    return sorted((m for m in REGISTRY.values() if capability in m.capabilities and m.enabled and m.approved and m.status in healthy), key=lambda m: m.priority, reverse=True)
