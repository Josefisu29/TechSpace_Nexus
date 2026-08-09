# TechSpace AI — Phases 21–30 Implementation Contract

This document defines the production completion contract for the next ten phases. Code must not be marked complete merely because a route or UI placeholder exists.

## 21 — Production Database
- PostgreSQL is the production metadata store.
- SQLAlchemy async sessions are used by API services.
- Every tenant-owned record must carry an owner/organization boundary.
- Migrations, indexes, backup/restore and connection pooling are mandatory before production.

## 22 — Authentication & Identity
- JWT/session authentication with Argon2-compatible password hashing.
- OAuth/passkeys/MFA are provider integrations, not hard-coded secrets.
- RBAC: user, operator, admin, owner.
- Every protected resource must enforce ownership/tenant scope.

## 23 — Production Chat
- Persistent conversations/messages.
- Streaming via SSE.
- Abort/regenerate/edit.
- Token/context accounting.
- Rate limits and abuse controls.
- Chat search, archive, pin, export and feedback.

## 24 — Files & Multimodal
- Signed uploads to object storage.
- MIME/size validation and malware scanning.
- PDF/DOCX/PPTX/XLSX/CSV/text/image/audio/video extraction.
- OCR where needed.
- Provider/model abstraction for vision, speech, image and video.

## 25 — RAG / Knowledge
- Content-addressed chunks.
- Embeddings.
- Vector store + keyword/hybrid retrieval.
- Reranking.
- Metadata and tenant filtering.
- Citation provenance.

## 26 — Web Search
- Search provider abstraction.
- Fetch/extract/clean pages.
- Source ranking and deduplication.
- Prompt-injection isolation for untrusted web content.
- Citation URLs and timestamps.

## 27 — Deep Research
- Planner → search → extraction → synthesis pipeline.
- Parallel bounded research tasks.
- Source verification and contradiction reporting.
- Persistent research reports.

## 28 — Agent Runtime
- Typed tool registry.
- Explicit permissions.
- Time/token/tool budgets.
- Durable jobs and retries.
- Human approval for dangerous actions.
- Full execution audit trail.

## 29 — Coding Agent
- Repository workspace.
- Git integration.
- Patch-based file changes.
- Test/lint loop.
- Review and PR preparation.
- No direct production mutation by the model.

## 30 — Secure Code Sandbox
- Isolated ephemeral containers/VMs.
- CPU/RAM/disk/time limits.
- Default-deny network.
- Read-only base image.
- Non-root execution.
- Artifact/result transfer only through controlled channels.

## Acceptance gate

A phase is complete only when its integration tests pass, its security boundary is tested, its data lineage is observable, and failure/rollback behavior is documented. External credentials and infrastructure must be configured through environment/secret management and never committed.
