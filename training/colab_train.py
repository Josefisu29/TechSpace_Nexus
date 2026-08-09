from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "processed" / "clean_manifest.json"


def require_gate() -> dict:
    if not MANIFEST.exists():
        raise SystemExit("Training blocked: clean_manifest.json does not exist")
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    required = {"status": "approved", "pii_scan": "passed", "secret_scan": "passed"}
    for key, expected in required.items():
        if data.get(key) != expected:
            raise SystemExit(f"Training blocked: {key}={data.get(key)!r}, expected {expected!r}")
    return data


def main() -> None:
    manifest = require_gate()
    if os.getenv("RUN_TRAINING", "0") != "1":
        print("Gate passed. Set RUN_TRAINING=1 after configuring the GPU trainer.")
        return

    # Deliberately require an explicit trainer command. This prevents an unattended
    # workflow from silently choosing an incompatible base model or hyperparameters.
    trainer = os.getenv("TRAINER_COMMAND")
    if not trainer:
        raise SystemExit("TRAINER_COMMAND is required for an actual training run")
    import subprocess
    env = os.environ.copy()
    env["APPROVED_DATA_MANIFEST"] = str(MANIFEST)
    subprocess.run(trainer, shell=True, cwd=ROOT, env=env, check=True)
    print("Training command completed. Run independent evaluation before promotion.")


if __name__ == "__main__":
    main()
