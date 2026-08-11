"""QLoRA SFT entrypoint for Colab/cloud GPUs.

Use a Hugging Face token from Colab Secrets or the environment. The base model
is never modified; adapters are saved as a separate artifact for easy rollback.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

import torch
from datasets import load_dataset
from peft import LoraConfig
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TrainingArguments
from trl import SFTTrainer


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="Qwen/Qwen3-30B-A3B")
    p.add_argument("--dataset", required=True)
    p.add_argument("--output", default="/content/techspace-adapter")
    p.add_argument("--max-seq-length", type=int, default=1024)
    p.add_argument("--epochs", type=float, default=1.0)
    p.add_argument("--batch-size", type=int, default=1)
    p.add_argument("--grad-accumulation", type=int, default=16)
    p.add_argument("--resume", default=None)
    args = p.parse_args()

    token = os.getenv("HF_TOKEN")
    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_use_double_quant=True)
    tokenizer = AutoTokenizer.from_pretrained(args.model, token=token, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(args.model, quantization_config=bnb, device_map="auto", torch_dtype=torch.bfloat16, token=token)
    model.config.use_cache = False

    ds = load_dataset("json", data_files=args.dataset, split="train")
    ds = ds.filter(lambda x: isinstance(x.get("text"), str) and len(x["text"].strip()) >= 20)
    lora = LoraConfig(r=32, lora_alpha=64, lora_dropout=0.05, target_modules="all-linear", task_type="CAUSAL_LM")
    training = TrainingArguments(
        output_dir=args.output,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accumulation,
        learning_rate=2e-4,
        logging_steps=10,
        save_steps=250,
        save_total_limit=3,
        bf16=torch.cuda.is_available() and torch.cuda.is_bf16_supported(),
        fp16=torch.cuda.is_available() and not torch.cuda.is_bf16_supported(),
        gradient_checkpointing=True,
        optim="paged_adamw_8bit",
        report_to="none",
    )
    trainer = SFTTrainer(model=model, tokenizer=tokenizer, train_dataset=ds, dataset_text_field="text", max_seq_length=args.max_seq_length, peft_config=lora, args=training)
    trainer.train(resume_from_checkpoint=args.resume)
    Path(args.output).mkdir(parents=True, exist_ok=True)
    trainer.save_model(args.output)
    tokenizer.save_pretrained(args.output)
    print(f"Saved adapter to {args.output}")


if __name__ == "__main__":
    main()
