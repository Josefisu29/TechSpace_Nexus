from __future__ import annotations

import argparse
import json
from pathlib import Path

from transformers import AutoModelForCausalLM, AutoTokenizer


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--output", default="artifacts/eval-smoke.json")
    args = parser.parse_args()

    tokenizer = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model, device_map="auto")

    prompts = [
        "Explain what an API is to a beginner.",
        "Write a Python function that returns the factorial of n.",
        "What is the difference between a process and a thread?",
    ]
    results = []
    for prompt in prompts:
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        output = model.generate(**inputs, max_new_tokens=128, do_sample=False)
        text = tokenizer.decode(output[0], skip_special_tokens=True)
        results.append({"prompt": prompt, "output": text})

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
