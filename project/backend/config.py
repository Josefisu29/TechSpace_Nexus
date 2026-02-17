from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = BASE_DIR / "backend"
FRONTEND_DIR = BASE_DIR / "frontend"

DATA_DIR = BASE_DIR / "data"
INPUT_DIR = DATA_DIR / "inputs"
OUTPUT_DIR = DATA_DIR / "outputs"
TEMP_DIR = DATA_DIR / "temp"

SUPPORTED_RESOLUTIONS = [360, 480, 720, 1080, 1440, 2048, 4096, 7680]

DEFAULT_VIDEO_CODEC = "libx264"
NVENC_VIDEO_CODEC = "h264_nvenc"
AUDIO_CODEC = "copy"
PIX_FMT = "yuv420p"

for path in (INPUT_DIR, OUTPUT_DIR, TEMP_DIR):
    path.mkdir(parents=True, exist_ok=True)
