# TechSpace AI model portfolio

## Recommended architecture

Do not merge unrelated model weights into one checkpoint. Use a portfolio + router: one primary chat/reasoning model, a code specialist, a vision model, an embedding model, and a reranker. Distillation/LoRA can later create a TechSpace-branded student model.

| Role | Recommended open model | Use |
|---|---|---|
| General/reasoning | Qwen3 family (select size by GPU budget) | primary assistant and orchestration |
| Reasoning specialist | DeepSeek-R1 / compatible distill | hard reasoning, math |
| Coding | Qwen3 coding-capable variant or DeepSeek distill | code generation/review |
| Vision | Gemma 3 multimodal or another license-approved VLM | images/screenshots/docs |
| Embeddings | Qwen3-Embedding 0.6B/4B/8B | multilingual RAG |
| Retrieval fallback | BGE-M3 | dense/sparse/multilingual retrieval |
| Reranking | BGE/Qwen-compatible reranker selected after benchmark | final context ranking |
| Local runtime | Ollama | local development and edge inference |
| Cloud runtime | vLLM/TGI-compatible deployment | production GPU serving |

## Why this portfolio

Qwen3 is a strong general foundation and is available through Ollama, including 30B and 235B variants. DeepSeek-R1 is MIT licensed at the model repository and is useful as a reasoning specialist. Qwen3 Embedding provides 0.6B/4B/8B choices and 100+ language support; BGE-M3 is a useful retrieval fallback with dense, multi-vector and sparse retrieval. Always verify the exact model-card license, terms, and any base-model/component restrictions before commercial redistribution.

## Training strategy

1. Start from one permissively licensed base model.
2. Build TechSpace instruction, tool-use, coding, research and Nigeria/Africa-relevant datasets.
3. SFT with LoRA/QLoRA.
4. Evaluate against the unmodified base.
5. Add preference optimization only after reliable SFT/eval.
6. Distill specialist behavior into a smaller TechSpace model.
7. Do not merge model weights merely because architectures are compatible; benchmark every merge and retain the best checkpoint.

## Deployment profiles

- `local-fast`: small Qwen3 + Qwen3-Embedding via Ollama.
- `local-quality`: larger Qwen3/DeepSeek specialist where hardware permits.
- `cloud-quality`: GPU-served primary model + specialist routing.
- `rag`: Qwen3-Embedding or BGE-M3 + reranker.

## License policy

The repository must store the exact model ID, revision/commit, license URL, tokenizer license, base-model lineage, dataset licenses and redistribution restrictions for every model used. No model is approved for commercial TechSpace distribution solely because it is called "open source".
