from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

class MediaType(str, Enum):
    IMAGE="image"
    VIDEO="video"
    AUDIO="audio"

@dataclass(frozen=True)
class MediaJob:
    id: str
    media_type: MediaType
    prompt: str
    status: str = "queued"

def create_job(job_id: str, media_type: MediaType, prompt: str) -> MediaJob:
    if not prompt.strip(): raise ValueError("prompt is required")
    return MediaJob(job_id, media_type, prompt.strip())
