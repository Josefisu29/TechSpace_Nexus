"""Orchestrate acquisition -> safety cleaning -> versioned dataset -> training/evaluation gates.

Heavy work is delegated to the Colab/GPU worker. This controller never promotes a
model directly: promotion requires passing independent evaluation gates.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
STATE = DATA / "pipeline_state.json"


def run(cmd: list[str]) -> None:
    print("$", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=ROOT, check=True)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def save_state(stage: str, **extra: object) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    state = {"updated_at": datetime.now(timezone.utc).isoformat(), "stage": stage, **extra}
    STATE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def main() -> None:
    kind = os.getenv("ASSET_KIND", "all")
    save_state("acquiring", kind=kind)
    if kind in {"all", "models"}:
        run([sys.executable, "training/download_assets.py", "models"])
    if kind in {"all", "datasets"}:
        run([sys.executable, "training/download_assets.py", "datasets"])

    # Cleaning is intentionally delegated to the safe cleaner worker. The controller
    # only advances when the worker writes an explicit, validated manifest.
    save_state("awaiting_clean_manifest")
    manifest = DATA / "processed" / "clean_manifest.json"
    if not manifest.exists():
        raise SystemExit("clean_manifest.json missing: run the safe cleaning worker before training")

    payload = json.loads(manifest.read_text(encoding="utf-8"))
    if payload.get("status") != "approved":
        raise SystemExit("cleaning manifest is not approved; training is blocked")
    if payload.get("pii_scan") != "passed" or payload.get("secret_scan") != "passed":
        raise SystemExit("privacy/security gates failed; training is blocked")

    save_state("training_ready", dataset_manifest_hash=sha256_file(manifest))
    print("Training gate passed. Launch the Colab/GPU trainer with the approved manifest.")


if __name__ == "__main__":
    main()
