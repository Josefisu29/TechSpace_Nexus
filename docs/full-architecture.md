# TechSpace AI — Full Project Architecture

## Product

TechSpace AI is a model-development and inference platform for building, evaluating, versioning and deploying an in-house LLM. It is designed to start cheaply with Google Colab and Hugging Face, then graduate to dedicated GPU infrastructure without rewriting the product.

## Planes

### 1. Studio UI
Static/mobile-responsive operator interface in `ui/`. It visualizes runs, datasets, models, evaluations and deployments.

### 2. Control plane
FastAPI service in `apps/api/`. It owns authenticated project operations, run metadata, orchestration requests and health endpoints. The current scaffold intentionally uses in-memory state; production persistence should be PostgreSQL/managed database plus object storage.

### 3. Data plane
`services/dataset/` handles source manifests, normalization, quality gates, deduplication and dataset artifacts. Large datasets should be processed in streaming/batched jobs rather than loaded into RAM.

### 4. Training plane
Google Colab is the first compute worker. Training jobs consume immutable dataset versions and write resumable checkpoints. The same job contract can later target RunPod, Lambda, cloud GPUs, or dedicated hardware.

### 5. Model registry
Hugging Face Hub is the initial artifact registry. Store base-model ID/revision, adapter revision, dataset version, tokenizer version, training configuration, evaluation report and license metadata with each release.

### 6. Inference plane
Ollama is the local inference target. Hosted inference can later be added behind the same model-provider interface.

## Lifecycle

`source → review → ingest → clean → deduplicate → validate → version → train → checkpoint → evaluate → register → export → Ollama/hosted inference → monitor → feedback → next dataset version`

## Production requirements before public launch

- Authentication and authorization
- Persistent database
- Object storage for datasets/checkpoints
- Secret manager
- Job queue/worker system
- Signed artifact/version metadata
- Dataset and model lineage
- Rate limiting
- Audit logs
- Automated tests and CI
- Evaluation gates before deployment
- PII/privacy filtering and retention policy
- Abuse/safety controls
- Backups and disaster recovery

## Design rule

Never continuously train directly on raw production conversations. Feedback must go through consent, privacy filtering, quality review, dataset versioning, and held-out evaluation before it becomes training material.
