# TechSpace Dataset Policy

## Dataset layers

The project keeps training data separated by purpose:

- general educational/web text
- code
- computer science
- mathematics
- instruction
- reasoning
- agent/tool use
- Africa/Nigeria
- safety
- held-out evaluation

## Source policy

A source entry is a manifest declaration, not permission to train on it. Before enabling a source, record:

1. Dataset/source name and exact revision.
2. Source URL or Hugging Face dataset ID.
3. License and whether it permits the intended use.
4. Provenance and collection date where available.
5. Known restrictions or attribution requirements.
6. Processing and filtering applied.

Sources marked `license_review: required` are blocked by the pipeline until explicitly reviewed and changed to an approved state.

## Quality controls

The preparation pipeline normalizes Unicode, removes null/control characters, filters very short/large examples, detects excessive repeated lines, preserves source/category metadata, and exact-deduplicates examples.

Near-deduplication is a planned next layer and must be implemented with a documented similarity method before being enabled for large corpora.

## Privacy

Private user conversations, credentials, personal files, or other private data must never be automatically added to training. Any future feedback-learning system must use explicit consent, privacy filtering, provenance, review, and a separate held-out evaluation set.

## Evaluation isolation

Evaluation sources are never automatically included in training. Keep evaluation data in a separate repository/version and use it only for model comparison.
