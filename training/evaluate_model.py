"""Small regression evaluator for model promotion gates.

The benchmark file is deliberately checked into the repository so every model
version is compared against the same prompts. It is not a replacement for
broader safety or capability evaluation.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("--bench", default="training/benchmarks.jsonl")
    p.add_argument("--max-new-tokens", type=int, default=128)
    args = p.parse_args()

    tok = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype="auto", device_map="auto", trust_remote_code=True)
    rows = []
    with Path(args.bench).open(encoding="utf-8") as f:
        for line in f:
            if line.strip(): rows.append(json.loads(line))
    results = []
    for row in rows:
        prompt = row["prompt"]
        inputs = tok(prompt, return_tensors="pt").to(model.device)
        start = time.perf_counter()
        with torch.inference_mode():
            out = model.generate(**inputs, max_new_tokens=args.max_new_tokens, do_sample=False)
        elapsed = time.perf_counter() - start
        answer = tok.decode(out[0][inputs["input_ids"].shape[-1]:], skip_special_tokens=True)
        results.append({"id": row["id"], "category": row.get("category"), "prompt": prompt, "answer": answer, "seconds": round(elapsed, 3)})
    print(json.dumps({"model": args.model, "count": len(results), "results": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
