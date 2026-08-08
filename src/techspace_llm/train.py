from __future__ import annotations

import argparse
import os
from pathlib import Path

import yaml
from datasets import Dataset
from peft import LoraConfig
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TrainingArguments
from trl import SFTTrainer

from .data import DatasetConfig, clean_dataset, load_text_dataset


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_trainer(cfg: dict, dataset: Dataset) -> SFTTrainer:
    model_id = cfg["model"]["id"]
    tokenizer = AutoTokenizer.from_pretrained(model_id, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    bnb = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype="bfloat16",
        bnb_4bit_use_double_quant=True,
    )
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        quantization_config=bnb,
        device_map="auto",
    )

    lora_cfg = cfg["lora"]
    peft = LoraConfig(
        r=lora_cfg["r"],
        lora_alpha=lora_cfg["alpha"],
        lora_dropout=lora_cfg["dropout"],
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=None if lora_cfg["target_modules"] == "auto" else lora_cfg["target_modules"],
    )

    t = cfg["training"]
    args = TrainingArguments(
        output_dir=t["output_dir"],
        num_train_epochs=t["num_train_epochs"],
        per_device_train_batch_size=t["per_device_train_batch_size"],
        gradient_accumulation_steps=t["gradient_accumulation_steps"],
        learning_rate=t["learning_rate"],
        warmup_ratio=t["warmup_ratio"],
        logging_steps=t["logging_steps"],
        save_steps=t["save_steps"],
        eval_steps=t["eval_steps"],
        save_total_limit=t["save_total_limit"],
        gradient_checkpointing=t["gradient_checkpointing"],
        bf16=t["bf16"],
        fp16=t["fp16"],
        report_to=t["report_to"],
        evaluation_strategy="steps",
    )

    return SFTTrainer(
        model=model,
        processing_class=tokenizer,
        train_dataset=dataset,
        peft_config=peft,
        args=args,
        dataset_text_field=cfg["data"]["text_column"],
        max_seq_length=cfg["data"]["max_seq_length"],
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/training.yaml")
    parser.add_argument("--resume", default=None)
    args = parser.parse_args()

    cfg = load_config(args.config)
    data_cfg = DatasetConfig(**cfg["data"])
    dataset = clean_dataset(load_text_dataset(data_cfg), data_cfg.text_column)
    split = dataset.train_test_split(test_size=0.02, seed=42)
    trainer = build_trainer(cfg, split["train"])

    trainer.train(resume_from_checkpoint=args.resume)
    output_dir = Path(cfg["training"]["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    trainer.save_model(output_dir)
    trainer.processing_class.save_pretrained(output_dir)


if __name__ == "__main__":
    main()
