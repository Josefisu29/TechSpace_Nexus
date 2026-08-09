# TechSpace AI Model Redundancy

## Policy
Every production model must have an immutable revision, an approved license, a capability profile, health state, and an explicit fallback chain. The router never falls back to an unapproved model.

## Failover signals
- connection failure
- timeout
- provider/GPU failure
- out-of-memory
- unsupported capability
- context overflow
- rate limiting
- malformed tool/output response

## Artifact protection
Model artifacts are registered with SHA-256 checksums and storage tiers. Production deployments should keep at least one warm copy and one independent cold/off-site copy. Restore must verify the checksum before activation.

## Model lifecycle
`pending -> approved -> healthy -> degraded -> offline -> retired`

A degraded model is excluded from normal routing. Recovery health checks may promote it again. Retirement is explicit and irreversible at the registry layer.

## Production requirements
Before approval, run license verification, capability tests, safety evaluation, regression benchmarks, tool-call tests and compatibility checks. Exact Hugging Face/Ollama revisions must be pinned in deployment configuration; never use `latest` in production.

## Portfolio principle
Do not merge unrelated model weights merely to create a larger checkpoint. Use a model portfolio and router. Fine-tuning/merging is reserved for compatible architectures and validated training objectives.
