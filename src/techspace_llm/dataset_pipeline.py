from __future__ import annotations

import argparse
import re
import unicodedata
from collections import Counter
from pathlib import Path

import yaml
from datasets import Dataset, concatenate_datasets, load_dataset


def load_manifest(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def normalize_text(value: str, cfg: dict) -> str:
    text = unicodedata.normalize("NFKC", value) if cfg.get("normalize_unicode", True) else value
    text = text.replace("\x00", " ") if cfg.get("strip_nulls", True) else text
    if cfg.get("strip_control_chars", True):
        text = "".join(ch if ch in "\n\t" or not unicodedata.category(ch).startswith("C") else " " for ch in text)
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    return "\n".join(lines).strip()


def quality_ok(text: str, cfg: dict) -> bool:
    if len(text) < cfg.get("min_chars", 40) or len(text) > cfg.get("max_chars", 200000):
        return False
    if len(text.split()) < cfg.get("min_words", 8):
        return False
    lines = text.splitlines()
    if lines:
        repeated = sum(count - 1 for count in Counter(lines).values() if count > 1)
        if repeated / len(lines) > cfg.get("max_repeated_line_ratio", 0.2):
            return False
    return True


def load_source(source: dict) -> Dataset:
    if not source.get("enabled"):
        raise ValueError(f"Disabled source cannot be loaded: {source['id']}")
    if not source.get("hf_id"):
        raise ValueError(f"Source {source['id']} has no dataset ID; add a reviewed source first.")
    return load_dataset(source["hf_id"], source.get("config"), split=source.get("split", "train"), streaming=False)


def process_source(source: dict, processing: dict) -> Dataset:
    ds = load_source(source)
    text_column = source.get("text_column", "text")
    if text_column not in ds.column_names:
        raise ValueError(f"{source['id']}: missing text column {text_column!r}")

    def transform(row: dict) -> dict:
        return {"text": normalize_text(str(row[text_column]), processing), "source_id": source["id"], "category": source["category"]}

    ds = ds.map(transform, remove_columns=ds.column_names)
    ds = ds.filter(lambda row: quality_ok(row["text"], processing))
    return ds


def deduplicate(ds: Dataset) -> Dataset:
    seen: set[str] = set()
    keep: list[int] = []
    for idx, text in enumerate(ds["text"]):
        key = text.casefold()
        if key not in seen:
            seen.add(key)
            keep.append(idx)
    return ds.select(keep)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a reviewed TechSpace training dataset")
    parser.add_argument("--manifest", default="configs/datasets.yaml")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    manifest = load_manifest(args.manifest)
    processing = manifest["processing"]
    datasets = []
    for source in manifest["sources"]:
        if not source.get("enabled"):
            continue
        if source.get("license_review") == "required":
            raise RuntimeError(f"Source {source['id']} is enabled but still requires license review.")
        datasets.append(process_source(source, processing))

    if not datasets:
        raise RuntimeError("No approved dataset sources are enabled.")

    combined = concatenate_datasets(datasets)
    if processing.get("deduplicate", True):
        combined = deduplicate(combined)

    output = Path(args.output or processing.get("output_dir", manifest["output"]["directory"]))
    output.mkdir(parents=True, exist_ok=True)
    combined.to_parquet(output / f"{manifest['output']['dataset_name']}-{manifest['output']['version']}.parquet")
    print(f"Wrote {len(combined):,} examples to {output}")


if __name__ == "__main__":
    main()
