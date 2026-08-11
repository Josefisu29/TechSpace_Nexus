# TechSpace AI cloud-first training pipeline

## 1. Local machine

Keep only source code and small test fixtures locally. Do not commit model weights, datasets, tokens, or checkpoints.

## 2. Cloud storage

Create a Google Cloud Storage bucket and set `GCS_BUCKET` in the runtime environment. Recommended prefixes:

```text
raw/
normalized/
cleaned/
quarantine/
balanced/
checkpoints/
evaluation/
archives/
```

## 3. Hugging Face

Use Hugging Face as the model/dataset registry. Create private model repositories for TechSpace adapters/releases if needed.

## 4. Ingestion

Install `training/requirements.txt`, authenticate with a Hugging Face token through Colab Secrets, then stream a bounded sample first:

```bash
python training/cloud_dataset_ingest.py --dataset fineweb2 --max-records 10000
```

Set `GCS_BUCKET` to upload each completed shard and delete its local copy.

## 5. Normalize and clean

Build the canonical multi-dataset stream, then run the safety gate:

```bash
python training/multi_dataset_builder.py --input data/raw --output data/normalized/multidataset.jsonl
python training/safe_cleaner.py \
  --input data/normalized/multidataset.jsonl \
  --output data/processed/cleaned.jsonl \
  --quarantine data/rejected/quarantine.jsonl
```

The cleaner uses exact SHA-256 deduplication and conservative PII/secret checks. It is not a complete safety system; add dedicated classifiers and human review before production training.

## 6. Colab QLoRA

Start with a small sample and verify the complete loop before spending GPU time:

```bash
python training/colab_qlora_train.py \
  --model Qwen/Qwen3-30B-A3B \
  --dataset data/processed/cleaned.jsonl \
  --output /content/techspace-adapter
```

For limited VRAM, reduce sequence length and use a smaller Qwen3 checkpoint first. Do not assume every Colab GPU can fit a 30B model even in 4-bit mode.

## 7. Evaluation gate

Run the fixed regression benchmark before promoting an adapter/model:

```bash
python training/evaluate_model.py --model /content/techspace-adapter
```

Compare results with the previous production version. A lower training loss alone is not a promotion criterion.

## 8. Release and rollback

Upload only evaluated artifacts to Hugging Face. Keep the previous release and an emergency smaller model available. Record dataset version, base-model revision, training arguments, evaluation results, and artifact hashes.

## 9. Production

Do not use Google Colab as the production inference server. Deploy the evaluated release to dedicated inference infrastructure and place a router in front of primary/backup models.

## Security

- Use Colab Secrets/environment variables for credentials.
- Never commit `.env`, service-account JSON, tokens, or private keys.
- Give cloud service accounts least-privilege permissions.
- Keep raw data immutable and preserve provenance/license metadata.
- Require evaluation and canary checks before automatic deployment.
