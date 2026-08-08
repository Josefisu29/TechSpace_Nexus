# TechSpace AI — Completion Roadmap

## Product goal

TechSpace AI is a private-first AI platform for building, training, evaluating, versioning, deploying, and continuously improving TechSpace language models. It supports Hugging Face model/data workflows, Google Colab GPU training, local Ollama inference, and eventual hosted inference.

## Phase 0 — Foundation

- [x] Repository structure
- [x] Dataset manifest
- [x] Training configuration
- [x] Dataset cleaning pipeline
- [x] Provenance/license gates
- [x] Initial AI Studio UI
- [x] FastAPI control plane
- [x] Docker development stack
- [x] Ollama adapter

## Phase 1 — Reproducible data platform

- [x] Source/category manifest
- [x] Text normalization
- [x] Quality filtering
- [x] Exact deduplication
- [x] Near-deduplication primitives
- [ ] Scalable MinHash/LSH index
- [ ] Dataset content hashes
- [ ] Immutable dataset manifests
- [ ] Dataset lineage graph
- [ ] PII/secrets detection and quarantine
- [ ] License metadata validator
- [ ] Streaming ingestion for multi-billion-token corpora
- [ ] Parquet/WebDataset sharding
- [ ] Dataset train/validation/test splitter

## Phase 2 — Training engine

- [ ] Colab bootstrap notebook
- [ ] Transformers + TRL training runner
- [ ] PEFT/QLoRA adapter training
- [ ] Resume-from-checkpoint
- [ ] Gradient accumulation and checkpoint rotation
- [ ] Automatic mixed precision selection
- [ ] GPU capability detection
- [ ] Token/step throughput metrics
- [ ] TensorBoard/W&B optional integrations
- [ ] Training artifact manifest
- [ ] Reproducible seeds and environment lockfile
- [ ] Failed-run recovery

## Phase 3 — Evaluation and quality

- [ ] Held-out evaluation datasets
- [ ] General capability suite
- [ ] Coding suite
- [ ] Mathematics suite
- [ ] Instruction-following suite
- [ ] Tool/function-calling suite
- [ ] Nigerian/African knowledge suite
- [ ] Safety suite
- [ ] Hallucination/error analysis
- [ ] Regression gates
- [ ] Model-vs-model comparison
- [ ] Evaluation reports stored with model lineage

## Phase 4 — Model registry

- [ ] Model/version database
- [ ] Base-model lineage
- [ ] Dataset lineage
- [ ] Training configuration lineage
- [ ] Adapter/artifact registry
- [ ] Model promotion states: experimental → candidate → production → retired
- [ ] SHA256 artifact verification
- [ ] Hugging Face Hub publishing
- [ ] Private/public visibility controls
- [ ] Model cards and dataset cards

## Phase 5 — Inference platform

- [x] Ollama client adapter
- [x] Ollama packaging template
- [ ] Streaming chat API
- [ ] Tool/function calling gateway
- [ ] Conversation sessions
- [ ] Request cancellation
- [ ] Rate limits
- [ ] Context/token accounting
- [ ] Model fallback routing
- [ ] Hosted inference adapter
- [ ] Health and readiness checks

## Phase 6 — AI Studio UX

- [x] Dashboard shell
- [x] Training overview
- [x] Dataset health surface
- [x] Model surface
- [x] Evaluation surface
- [ ] Dataset browser
- [ ] Training run wizard
- [ ] Live log viewer
- [ ] Checkpoint browser
- [ ] Evaluation comparison workspace
- [ ] Model registry UI
- [ ] Playground with streaming responses
- [ ] Deployment wizard
- [ ] API-key/settings UI
- [ ] Audit/activity feed
- [ ] Command palette
- [ ] Accessibility audit

## Phase 7 — Security and identity

- [ ] Authentication
- [ ] RBAC
- [ ] Owner/admin/operator/viewer roles
- [ ] API key management
- [ ] Secret manager integration
- [ ] Encryption at rest
- [ ] TLS in deployment
- [ ] Audit logs
- [ ] Dataset access controls
- [ ] Model artifact access controls
- [ ] Request abuse protection
- [ ] Security headers
- [ ] Dependency/SBOM scanning

## Phase 8 — Production infrastructure

- [ ] PostgreSQL metadata store
- [ ] Object storage for datasets/checkpoints
- [ ] Redis/queue where required
- [ ] Worker service
- [ ] Job scheduler
- [ ] WebSocket/SSE training events
- [ ] Horizontal inference workers
- [ ] GPU worker profiles
- [ ] Observability: logs/metrics/traces
- [ ] Backups and restore tests
- [ ] Disaster recovery procedure
- [ ] CI/CD
- [ ] Staging environment
- [ ] Production environment

## Phase 9 — Continuous learning

- [ ] Explicit user feedback collection
- [ ] Feedback privacy filtering
- [ ] Human review queue
- [ ] High-quality example curation
- [ ] Synthetic-data generation pipeline
- [ ] Data-mixture versioning
- [ ] Scheduled retraining
- [ ] Evaluation gate before promotion
- [ ] Canary deployment
- [ ] Automatic rollback
- [ ] Model drift monitoring

## Phase 10 — Advanced agent platform

- [ ] LangGraph orchestration
- [ ] Supervisor/worker architecture
- [ ] Tool registry
- [ ] Sandboxed code execution
- [ ] Browser/search connectors
- [ ] RAG pipeline
- [ ] Vector index
- [ ] Document ingestion
- [ ] Long-term memory with explicit privacy controls
- [ ] Agent evaluation suite
- [ ] Cost/latency-aware model routing

## Definition of done

The platform is considered production-ready only when a clean environment can:

1. Create an approved dataset version from documented sources.
2. Reproduce a training run from its manifest.
3. Train or adapt a model on Colab/GPU infrastructure.
4. Save and verify checkpoints.
5. Evaluate the model against held-out suites.
6. Register the model with complete lineage.
7. Publish an approved artifact to Hugging Face when desired.
8. Package an inference artifact for Ollama/local use.
9. Serve streaming inference through the API.
10. Monitor the deployment and roll back a bad model.
11. Record audit/security events.
12. Retrain only from explicitly approved and traceable data.

## Non-negotiable principles

- Never train on private user data by default.
- Never bypass licensing/provenance checks.
- Never mix evaluation data into training automatically.
- Never promote a model based on a single benchmark.
- Never expose secrets to the model or frontend.
- Never claim continuous learning without a reviewed retraining pipeline.
- Every production model must be traceable to its base model, dataset versions, code revision, configuration, evaluation results, and artifact hash.
