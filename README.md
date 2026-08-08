# TechSpace LLM

A clean, reproducible training and deployment scaffold for the TechSpace LLM project.

## Pipeline

`dataset sources → license/quality filtering → deduplication → versioned dataset → Colab QLoRA/SFT → evaluation → Hugging Face Hub → GGUF/Ollama → production inference`

## Scope

- Google Colab training notebook
- Hugging Face model and dataset configuration
- Dataset ingestion and quality filtering
- LoRA/QLoRA supervised fine-tuning
- Checkpointing and resume support
- Evaluation harness
- Hugging Face Hub publishing
- GGUF/Ollama packaging
- Configuration-driven experiments

## Initial model strategy

The repository is designed to prototype on a small Qwen-family instruct/coder model and graduate to larger models such as Qwen3-Coder or GPT-OSS when the pipeline is validated. Model IDs remain configuration values so experiments can be reproduced without rewriting code.

## Data policy

Only use datasets and source material whose licenses/terms permit the intended use. Keep source metadata, license information, provenance, and dataset versions with every build. Never place secrets or private user data in the training corpus.

## Quick start

1. Create a Python environment from `requirements.txt`.
2. Copy `.env.example` to `.env` and add a Hugging Face token with the minimum required permissions.
3. Run the data preparation pipeline.
4. Open `notebooks/01_colab_qlora_sft.ipynb` in Google Colab.
5. Train/evaluate and publish a versioned adapter/model to Hugging Face.
6. Export to GGUF when supported by the selected model and test locally with Ollama.

See `docs/architecture.md` and `docs/training.md` for the complete workflow.
