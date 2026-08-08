from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from datasets import Dataset, DatasetDict, load_dataset


@dataclass(frozen=True)
class DatasetConfig:
    dataset_id: str
    config: str | None = None
    split: str = "train"
    text_column: str = "text"
    max_samples: int | None = None


def load_text_dataset(cfg: DatasetConfig) -> Dataset:
    ds = load_dataset(cfg.dataset_id, cfg.config, split=cfg.split)
    if cfg.max_samples is not None:
        ds = ds.select(range(min(cfg.max_samples, len(ds))))
    if cfg.text_column not in ds.column_names:
        raise ValueError(f"Missing text column: {cfg.text_column}")
    return ds


def clean_text(text: str) -> str:
    return " ".join(text.replace("\x00", " ").split()).strip()


def clean_dataset(ds: Dataset, text_column: str = "text") -> Dataset:
    ds = ds.map(lambda row: {text_column: clean_text(row[text_column])})
    ds = ds.filter(lambda row: bool(row[text_column]))
    ds = ds.filter(lambda row: len(row[text_column]) >= 40)
    return ds


def split_dataset(ds: Dataset, test_size: float = 0.02, seed: int = 42) -> DatasetDict:
    return ds.train_test_split(test_size=test_size, seed=seed)
