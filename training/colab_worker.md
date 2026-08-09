# Colab/GPU worker contract

Run from a GPU runtime after cloning the repository.

1. Install `training/requirements.txt`.
2. Set `HF_TOKEN` as a Colab secret when gated/private assets require it.
3. Run `python training/safe_learning_pipeline.py` to acquire registered assets.
4. Execute the safe-cleaning worker and write `data/processed/clean_manifest.json`.
5. The manifest must contain `status=approved`, `pii_scan=passed`, and `secret_scan=passed` before training is allowed.
6. Train only from the approved versioned dataset and save immutable checkpoints.
7. Run independent evaluation/regression/safety suites.
8. Upload approved artifacts to Hugging Face/object storage; never commit model weights or datasets to Git.

The controller intentionally blocks training when the cleaning manifest is missing or fails privacy/security gates. Production promotion remains a separate registry/canary operation.
