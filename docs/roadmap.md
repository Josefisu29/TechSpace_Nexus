# TechSpace AI Full Roadmap

## Phase 0 — Foundation
- Repository structure
- Dataset policy
- Configuration
- UI shell
- API skeleton
- Local Docker environment

## Phase 1 — Working training loop
- Colab QLoRA/SFT notebook
- Dataset preparation
- Checkpoint/resume
- Evaluation harness
- Hugging Face publishing
- GGUF export verification
- Ollama smoke test

## Phase 2 — Real Studio
- API persistence
- Auth/RBAC
- Dataset browser
- Run creation wizard
- Live run events
- Log streaming
- Model registry
- Evaluation dashboards
- Playground connected to inference

## Phase 3 — Data platform
- Streaming ingestion
- Parquet/Arrow artifacts
- MinHash/LSH near-deduplication at scale
- PII detection/redaction
- Language identification
- Toxicity/safety filtering
- License/provenance reports
- Dataset lineage
- Human review queues

## Phase 4 — Training platform
- Worker queue
- Colab job handoff
- GPU provider abstraction
- Distributed training support
- Automatic checkpoint management
- Experiment comparison
- Hyperparameter sweeps

## Phase 5 — Model platform
- Adapter registry
- Merge/export pipeline
- Quantization profiles
- GGUF validation
- Ollama packaging
- Hosted inference provider
- Model rollout/rollback

## Phase 6 — Production
- PostgreSQL
- Object storage
- Redis/queue
- Secrets manager
- Observability
- Rate limiting
- Audit logs
- Backups
- Security review
- Load testing

## Phase 7 — Continuous improvement
- Explicitly consented feedback collection
- Privacy filtering
- Human preference datasets
- Regression suite
- Scheduled retraining
- Canary evaluation
- Versioned releases

A model is only promoted when it passes quality, safety, regression and operational gates.
