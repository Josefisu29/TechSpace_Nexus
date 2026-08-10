from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from .config import OUTPUT_DIR, SUPPORTED_RESOLUTIONS
from .device import get_device, get_optimal_tile
from .video_pipeline import OpenCVUpscaleEngine, RealESRGANUpscaleEngine, process_video


@dataclass
class Job:
    job_id: str
    status: str = "queued"
    progress: int = 0
    input_path: Optional[Path] = None
    output_path: Optional[Path] = None
    resolution: int = 1080
    device: str = "cpu"
    error: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class JobManager:
    def __init__(self) -> None:
        self.jobs: Dict[str, Job] = {}
        self._lock = threading.Lock()

    def create_job(self, input_path: Path, resolution: int) -> Job:
        if resolution not in SUPPORTED_RESOLUTIONS:
            raise ValueError(f"Unsupported resolution: {resolution}")

        job_id = str(uuid.uuid4())
        output_path = OUTPUT_DIR / f"{job_id}.mp4"
        job = Job(
            job_id=job_id,
            input_path=input_path,
            output_path=output_path,
            resolution=resolution,
            device=get_device(),
        )

        with self._lock:
            self.jobs[job_id] = job

        worker = threading.Thread(target=self._run_job, args=(job_id,), daemon=True)
        worker.start()
        return job

    def _run_job(self, job_id: str) -> None:
        job = self.jobs[job_id]
        job.status = "processing"

        def _set_progress(value: int) -> None:
            with self._lock:
                if job_id in self.jobs:
                    self.jobs[job_id].progress = max(0, min(100, value))

        try:
            engine = self._build_engine()
            process_video(
                input_path=job.input_path,
                output_path=job.output_path,
                target_height=job.resolution,
                update_progress=_set_progress,
                engine=engine,
            )
            with self._lock:
                self.jobs[job_id].status = "completed"
                self.jobs[job_id].progress = 100
        except Exception as exc:
            with self._lock:
                self.jobs[job_id].status = "failed"
                self.jobs[job_id].error = str(exc)
            if job.output_path:
                job.output_path.unlink(missing_ok=True)
        finally:
            if job.input_path:
                job.input_path.unlink(missing_ok=True)

    def _build_engine(self):
        weights_path = Path(__file__).resolve().parent / "weights" / "RealESRGAN_x4plus.pth"
        if weights_path.exists():
            try:
                return RealESRGANUpscaleEngine(weights_path, tile=get_optimal_tile())
            except Exception:
                return OpenCVUpscaleEngine()
        return OpenCVUpscaleEngine()

    def get_job(self, job_id: str) -> Optional[Job]:
        with self._lock:
            return self.jobs.get(job_id)
