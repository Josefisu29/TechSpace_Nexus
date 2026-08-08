# TechSpace LLM architecture

## Core flow

```text
Licensed/authorized sources
        ↓
Data ingestion + provenance
        ↓
Cleaning + deduplication + quality filters
        ↓
Versioned Hugging Face Dataset
        ↓
Google Colab / GPU training
        ↓
LoRA/QLoRA SFT
        ↓
Evaluation gate
        ↓
Hugging Face Model Hub
        ├── adapter/model artifacts
        └── model metadata + card
        ↓
GGUF export when supported
        ↓
Ollama local validation
        ↓
Production inference server (later: vLLM/SGLang)
```

## Dataset families

- general web/educational text: FineWeb/FineWeb-Edu samples and other compatible licensed corpora
- code: license-filtered and provenance-tracked sources
- computer science and mathematics: curated/authorized educational material
- instruction and reasoning: verified examples
- agent/tool use: structured function-calling and coding workflows
- Nigeria/Africa: authorized local-context datasets
- safety: adversarial and policy examples
- evaluation: held-out tests that are never used for training

## Continuous improvement

Do not train directly on raw user conversations. Candidate data must pass privacy filtering, provenance/license checks, deduplication, quality review, and evaluation before it can enter a future training release.

## Secrets

Never commit Hugging Face tokens, API keys, cookies, private datasets, or user data. Use environment variables or the Colab secret manager.
