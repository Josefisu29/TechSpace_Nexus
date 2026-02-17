from __future__ import annotations

import json
import math
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Callable

import cv2
import numpy as np

from .config import AUDIO_CODEC, OUTPUT_DIR, PIX_FMT, TEMP_DIR
from .device import get_device, get_encoder

try:
    import torch
except Exception:
    torch = None

try:
    from basicsr.archs.rrdbnet_arch import RRDBNet
    from realesrgan import RealESRGANer
except Exception:
    RRDBNet = None
    RealESRGANer = None


class UpscaleEngine:
    def upscale_frame(self, frame: np.ndarray, target_height: int) -> np.ndarray:
        raise NotImplementedError


class OpenCVUpscaleEngine(UpscaleEngine):
    def upscale_frame(self, frame: np.ndarray, target_height: int) -> np.ndarray:
        h, w = frame.shape[:2]
        if h <= 0 or w <= 0:
            raise ValueError("Invalid frame dimensions")
        scale = target_height / h
        new_w = max(2, int(round(w * scale)))
        return cv2.resize(frame, (new_w, target_height), interpolation=cv2.INTER_CUBIC)


class RealESRGANUpscaleEngine(UpscaleEngine):
    def __init__(self, model_path: Path, tile: int):
        if RRDBNet is None or RealESRGANer is None:
            raise RuntimeError("Real-ESRGAN dependencies are not installed")

        self.device = "cuda" if get_device() == "gpu" else "cpu"
        model = RRDBNet(
            num_in_ch=3,
            num_out_ch=3,
            num_feat=64,
            num_block=23,
            num_grow_ch=32,
            scale=4,
        )
        self.upsampler = RealESRGANer(
            scale=4,
            model_path=str(model_path),
            model=model,
            tile=tile,
            tile_pad=10,
            pre_pad=0,
            half=self.device == "cuda",
            device=self.device,
        )

    def upscale_frame(self, frame: np.ndarray, target_height: int) -> np.ndarray:
        try:
            output, _ = self.upsampler.enhance(frame, outscale=4)
        except RuntimeError:
            if torch is None:
                raise
            torch.cuda.empty_cache()
            self.upsampler.device = "cpu"
            output, _ = self.upsampler.enhance(frame, outscale=4)

        scale = target_height / output.shape[0]
        new_w = max(2, int(round(output.shape[1] * scale)))
        return cv2.resize(output, (new_w, target_height), interpolation=cv2.INTER_CUBIC)


def _ffprobe_metadata(input_path: Path) -> dict:
    probe_cmd = [
        "ffprobe",
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(input_path),
    ]
    result = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
    metadata = json.loads(result.stdout)

    streams = metadata.get("streams", [])
    video_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
    if not video_stream:
        raise RuntimeError("No video stream found")

    width = int(video_stream["width"])
    height = int(video_stream["height"])
    frame_count = int(video_stream.get("nb_frames") or 0)
    rate = video_stream.get("avg_frame_rate") or video_stream.get("r_frame_rate") or "30/1"
    try:
        num, den = rate.split("/")
        fps = float(num) / float(den)
    except Exception:
        fps = 30.0

    if frame_count <= 0:
        duration = float(metadata.get("format", {}).get("duration") or 0)
        if duration > 0 and fps > 0:
            frame_count = int(math.ceil(duration * fps))

    return {
        "width": width,
        "height": height,
        "fps": fps,
        "frame_count": max(1, frame_count),
    }


def process_video(
    input_path: Path,
    output_path: Path,
    target_height: int,
    update_progress: Callable[[int], None],
    engine: UpscaleEngine,
) -> None:
    metadata = _ffprobe_metadata(input_path)
    cap = cv2.VideoCapture(str(input_path))
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open input video: {input_path}")

    fps = metadata["fps"]
    total_frames = metadata["frame_count"]

    ok, frame = cap.read()
    if not ok or frame is None:
        cap.release()
        raise RuntimeError("No frames available in source video")

    upscaled = engine.upscale_frame(frame, target_height)
    out_h, out_w = upscaled.shape[:2]

    fd, tmp_file = tempfile.mkstemp(prefix="upscaled_", suffix=".mp4", dir=str(TEMP_DIR))
    os.close(fd)
    tmp_path = Path(tmp_file)

    encoder = get_encoder()
    ffmpeg_cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "rawvideo",
        "-vcodec",
        "rawvideo",
        "-pix_fmt",
        "bgr24",
        "-s",
        f"{out_w}x{out_h}",
        "-r",
        str(fps),
        "-i",
        "-",
        "-i",
        str(input_path),
        "-map",
        "0:v:0",
        "-map",
        "1:a?",
        "-c:v",
        encoder,
        "-pix_fmt",
        PIX_FMT,
        "-c:a",
        AUDIO_CODEC,
        "-shortest",
        str(tmp_path),
    ]

    ffmpeg_process = subprocess.Popen(
        ffmpeg_cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )

    processed_frames = 0

    try:
        ffmpeg_process.stdin.write(upscaled.tobytes())
        processed_frames += 1
        update_progress(int((processed_frames / total_frames) * 100))

        while True:
            ok, frame = cap.read()
            if not ok or frame is None:
                break

            upscaled = engine.upscale_frame(frame, target_height)
            ffmpeg_process.stdin.write(upscaled.tobytes())
            processed_frames += 1
            if processed_frames % 5 == 0 or processed_frames >= total_frames:
                update_progress(min(99, int((processed_frames / total_frames) * 100)))

    finally:
        cap.release()
        if ffmpeg_process.stdin:
            ffmpeg_process.stdin.close()

    stderr = ffmpeg_process.stderr.read().decode("utf-8", errors="ignore") if ffmpeg_process.stderr else ""
    return_code = ffmpeg_process.wait()

    if return_code != 0:
        tmp_path.unlink(missing_ok=True)
        raise RuntimeError(f"FFmpeg failed ({return_code}): {stderr[-1000:]}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    os.replace(tmp_path, output_path)
    update_progress(100)
