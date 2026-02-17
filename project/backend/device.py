from __future__ import annotations

import shutil
import subprocess
from functools import lru_cache

from .config import DEFAULT_VIDEO_CODEC, NVENC_VIDEO_CODEC

try:
    import torch
except Exception:  # torch optional dependency at runtime
    torch = None


def get_device() -> str:
    if torch is not None and torch.cuda.is_available():
        return "gpu"
    return "cpu"


def get_gpu_memory() -> int:
    if torch is not None and torch.cuda.is_available():
        props = torch.cuda.get_device_properties(0)
        return int(props.total_memory)
    return 0


def get_optimal_tile() -> int:
    vram = get_gpu_memory()
    if vram > 12 * 1024**3:
        return 512
    if vram > 8 * 1024**3:
        return 256
    if vram > 4 * 1024**3:
        return 128
    return 64


@lru_cache(maxsize=1)
def _available_encoders() -> str:
    if shutil.which("ffmpeg") is None:
        return ""
    result = subprocess.run(
        ["ffmpeg", "-hide_banner", "-encoders"],
        capture_output=True,
        text=True,
        check=False,
    )
    return f"{result.stdout}\n{result.stderr}"


def get_encoder() -> str:
    if get_device() == "gpu" and NVENC_VIDEO_CODEC in _available_encoders():
        return NVENC_VIDEO_CODEC
    return DEFAULT_VIDEO_CODEC
