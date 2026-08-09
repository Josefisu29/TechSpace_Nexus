from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("manifest", default="data/processed/clean_manifest.json")
    args = p.parse_args()
    path = Path(args.manifest)
    if not path.exists():
        raise SystemExit("manifest not found")
    data = json.loads(path.read_text(encoding="utf-8"))
    required = ["status", "pii_scan", "secret_scan", "deduplication", "artifact_sha256"]
    missing = [x for x in required if not data.get(x)]
    if missing:
        raise SystemExit(f"invalid manifest; missing: {', '.join(missing)}")
    if data["status"] != "approved" or data["pii_scan"] != "passed" or data["secret_scan"] != "passed":
        raise SystemExit("manifest failed safety gates")
    print("dataset manifest: VALID and APPROVED")


if __name__ == "__main__":
    main()
