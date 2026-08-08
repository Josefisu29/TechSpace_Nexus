# TechSpace AI Studio UI

Premium desktop-first AI training and model operations interface. The UI is intentionally a separate frontend surface so the Python training pipeline remains independently testable.

## UX principles

- Clear hierarchy: workspace → run → model/data/evaluation.
- Dark-first operator experience with optional light theme.
- Dense enough for ML workflows without feeling like a terminal dashboard.
- Every destructive or expensive operation requires an explicit review state.
- Training progress, GPU utilization, dataset quality, checkpoints, and evaluation results are visible without hunting through logs.
- Responsive layouts for laptop/tablet and usable mobile monitoring.

## Screens

1. Overview — current run, GPU, dataset, model health, recent checkpoints.
2. Datasets — sources, licenses, provenance, quality, deduplication, versions.
3. Training — live loss, learning rate, throughput, VRAM, ETA, checkpoint timeline.
4. Models — model registry, adapters, versions, deployment targets.
5. Evaluations — benchmark matrix, regression alerts, side-by-side versions.
6. Playground — chat, code blocks, tool traces, model selection, latency/tokens.
7. Deployments — Ollama/local, hosted inference, endpoint health, versions.
8. Data Lab — inspect examples, filters, quality flags, duplicate clusters.
9. Settings — credentials, storage, compute profiles, notifications, safety controls.

## Visual language

Deep neutral canvas, subtle blue-violet accents, 16–24px radii, restrained glass surfaces, high-contrast typography, compact metric cards, readable charts, keyboard-friendly controls, reduced-motion support, and strong empty/error/loading states.
