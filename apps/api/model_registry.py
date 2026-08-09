from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone

@dataclass(frozen=True)
class ModelRecord:
    id: str
    provider: str
    revision: str
    license: str
    capabilities: tuple[str, ...]
    context_length: int
    enabled: bool = True
    metadata: dict = field(default_factory=dict)

REGISTRY: dict[str, ModelRecord] = {}

def register(model: ModelRecord) -> ModelRecord:
    if not model.id or not model.provider or not model.revision:
        raise ValueError("model id, provider and revision are required")
    REGISTRY[model.id] = model
    return model

def list_models() -> list[dict]:
    return [asdict(x) for x in REGISTRY.values()]

def get_model(model_id: str) -> ModelRecord | None:
    return REGISTRY.get(model_id)

# Baseline records. Exact revisions should be pinned in deployment configuration.
register(ModelRecord("qwen3", "ollama/huggingface", "PIN_REQUIRED", "VERIFY_MODEL_CARD", ("general", "reasoning", "coding"), 128000))
register(ModelRecord("deepseek-r1", "huggingface", "PIN_REQUIRED", "MIT", ("reasoning", "math", "coding"), 128000))
register(ModelRecord("qwen3-embedding", "ollama/huggingface", "PIN_REQUIRED", "VERIFY_MODEL_CARD", ("embedding", "retrieval"), 32768))
register(ModelRecord("bge-m3", "ollama/huggingface", "PIN_REQUIRED", "VERIFY_MODEL_CARD", ("embedding", "retrieval", "multilingual"), 8192))
