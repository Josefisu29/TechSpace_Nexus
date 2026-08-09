"""Production-facing contracts for Phases 31-40.

These boundaries keep provider credentials and infrastructure-specific implementations
out of the core domain. Provider adapters can be registered behind these interfaces.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

@dataclass(frozen=True)
class MediaJob:
    id: str
    kind: str
    status: str
    provider: str | None = None

class VoiceProvider(Protocol):
    async def transcribe(self, audio: bytes, mime_type: str) -> str: ...
    async def synthesize(self, text: str, voice: str | None = None) -> bytes: ...

class CreativeProvider(Protocol):
    async def generate_image(self, prompt: str) -> MediaJob: ...
    async def generate_video(self, prompt: str) -> MediaJob: ...

class EmbeddingProvider(Protocol):
    async def embed(self, texts: list[str]) -> list[list[float]]: ...

class SearchProvider(Protocol):
    async def search(self, query: str, limit: int = 10) -> list[dict]: ...

class BillingProvider(Protocol):
    async def create_checkout(self, user_id: str, plan: str) -> str: ...
    async def cancel_subscription(self, user_id: str) -> bool: ...
