from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

@dataclass(frozen=True)
class Chunk:
    id: str
    text: str
    source: str
    index: int

def chunk_text(text: str, source: str, size: int = 900, overlap: int = 120) -> list[Chunk]:
    clean = re.sub(r"\s+", " ", text).strip()
    if not clean: return []
    step = max(1, size - overlap)
    chunks=[]
    for i, start in enumerate(range(0, len(clean), step)):
        body=clean[start:start+size]
        if not body: break
        cid=hashlib.sha256(f"{source}:{i}:{body}".encode()).hexdigest()[:20]
        chunks.append(Chunk(cid, body, source, i))
        if start+size >= len(clean): break
    return chunks

def lexical_score(query: str, text: str) -> float:
    q=set(re.findall(r"\w+", query.casefold()))
    t=set(re.findall(r"\w+", text.casefold()))
    return len(q&t)/max(1,len(q))

def retrieve(query: str, chunks: list[Chunk], top_k: int = 5) -> list[tuple[Chunk,float]]:
    return sorted(((c, lexical_score(query,c.text)) for c in chunks), key=lambda x:x[1], reverse=True)[:top_k]
