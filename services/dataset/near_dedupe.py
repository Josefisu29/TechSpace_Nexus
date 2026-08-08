from __future__ import annotations

import hashlib
from dataclasses import dataclass


@dataclass(frozen=True)
class SignatureConfig:
    shingle_size: int = 5
    bands: int = 16
    rows: int = 4


def shingles(text: str, size: int = 5) -> set[str]:
    tokens = text.casefold().split()
    return {" ".join(tokens[i:i + size]) for i in range(max(0, len(tokens) - size + 1))}


def fingerprint(text: str, size: int = 5) -> int:
    parts = sorted(shingles(text, size))
    return int(hashlib.sha256("\n".join(parts).encode()).hexdigest()[:16], 16)


def jaccard(a: str, b: str, size: int = 5) -> float:
    sa, sb = shingles(a, size), shingles(b, size)
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def near_duplicate(a: str, b: str, threshold: float = 0.85) -> bool:
    return jaccard(a, b) >= threshold
