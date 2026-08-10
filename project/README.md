# Local Hybrid AI Video Upscaler (Production-Grade)

A fully local AI-ready video upscaling system with CPU/GPU support, long-video-safe frame streaming, atomic output writes, and a clean PWA frontend.

## Features

- Fully local processing (no cloud calls)
- FastAPI backend + lightweight frontend PWA
- Streaming frame pipeline (safe for long videos)
- Background job processing with progress tracking
- Atomic output replacement to prevent corruption
- Optional GPU + NVENC detection
- Real-ESRGAN integration path (auto-enabled when weights/deps are present)

## Project Structure

```
project/
├── backend/
│   ├── main.py
│   ├── video_pipeline.py
│   ├── device.py
│   ├── job_manager.py
│   ├── config.py
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── app.js
│   ├── style.css
│   ├── manifest.json
│   └── service-worker.js
├── run.py
└── README.md
```

## Requirements

- Python 3.10+
- FFmpeg + FFprobe installed and available in `PATH`
- (Optional) NVIDIA GPU + CUDA runtime for GPU acceleration

## Setup

```bash
cd project
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

## Install FFmpeg

### Ubuntu/Debian

```bash
sudo apt update
sudo apt install -y ffmpeg
```

### macOS (Homebrew)

```bash
brew install ffmpeg
```

### Windows (Chocolatey)

```powershell
choco install ffmpeg
```

## Run

```bash
cd project
python run.py
```

- Backend API runs on `http://127.0.0.1:8000`
- Frontend opens automatically in your default browser

## API

- `POST /submit` with multipart fields:
  - `file`: video
  - `resolution`: one of `360,480,720,1080,1440,2048,4096,7680`
- `GET /status/{job_id}`
- `GET /download/{job_id}`

## Real-ESRGAN Upgrade

1. Install dependencies:

```bash
pip install realesrgan basicsr facexlib gfpgan
```

2. Download `RealESRGAN_x4plus.pth` and place it at:

```text
project/backend/weights/RealESRGAN_x4plus.pth
```

3. Restart the backend. If model + dependencies are found, Real-ESRGAN is used automatically; otherwise OpenCV upscaling is used.

## Stability and Safety Notes

- Frame-by-frame streaming avoids memory blowups for long videos.
- No image sequence dump to disk.
- Temp file output is atomically renamed on successful completion.
- Temp and input cleanup occurs on failures.
- CPU fallback path is retained when GPU/ESRGAN path is unavailable.
