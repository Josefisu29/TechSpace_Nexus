from __future__ import annotations

from dataclasses import dataclass
from time import monotonic

from model_registry import ModelRecord, ModelStatus, candidates, get_model, set_status

@dataclass(frozen=True)
class Attempt:
    model_id: str
    ok: bool
    latency_ms: int
    error: str | None = None

class ModelUnavailable(RuntimeError):
    pass

class FailoverRouter:
    def __init__(self, *, max_attempts: int = 3, timeout_ms: int = 120_000):
        self.max_attempts = max_attempts
        self.timeout_ms = timeout_ms

    def plan(self, capability: str, requested: str | None = None) -> list[ModelRecord]:
        ordered: list[ModelRecord] = []
        if requested:
            requested_model = get_model(requested)
            if requested_model and requested_model.approved and requested_model.enabled and requested_model.status in {ModelStatus.approved, ModelStatus.healthy}:
                ordered.append(requested_model)
        for model in candidates(capability):
            if model.id not in {x.id for x in ordered}:
                ordered.append(model)
        expanded: list[ModelRecord] = []
        for model in ordered:
            expanded.append(model)
            for fallback_id in model.fallbacks:
                fallback = get_model(fallback_id)
                if fallback and fallback.approved and fallback.enabled and fallback.status in {ModelStatus.approved, ModelStatus.healthy} and fallback.id not in {x.id for x in expanded}:
                    expanded.append(fallback)
        return expanded[: self.max_attempts]

    async def execute(self, capability: str, call, requested: str | None = None):
        attempts: list[Attempt] = []
        for model in self.plan(capability, requested):
            started = monotonic()
            try:
                result = await call(model)
                latency = int((monotonic() - started) * 1000)
                if latency > self.timeout_ms:
                    raise TimeoutError(f"model exceeded {self.timeout_ms}ms")
                set_status(model.id, ModelStatus.healthy)
                attempts.append(Attempt(model.id, True, latency))
                return result, attempts
            except Exception as exc:
                latency = int((monotonic() - started) * 1000)
                set_status(model.id, ModelStatus.degraded)
                attempts.append(Attempt(model.id, False, latency, str(exc)))
        raise ModelUnavailable({"capability": capability, "attempts": [a.__dict__ for a in attempts]})
