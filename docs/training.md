# Training workflow

## 1. Colab setup

```bash
pip install -r requirements.txt
```

Inspect the runtime before selecting a model:

```bash
nvidia-smi
```

The configured model is intentionally small for the first smoke test. Move to a larger Qwen or GPT-OSS model only after the pipeline is proven on the available GPU.

## 2. Authenticate

Set `HF_TOKEN` through Colab Secrets or the runtime environment. Do not hard-code it in notebooks.

## 3. Train

```bash
python -m src.techspace_llm.train --config configs/training.yaml
```

Resume a saved checkpoint:

```bash
python -m src.techspace_llm.train --config configs/training.yaml --resume outputs/techspace-llm/checkpoint-250
```

## 4. Publish

```bash
python -m src.techspace_llm.publish \
  --folder outputs/techspace-llm \
  --repo YOUR_USERNAME/techspace-llm
```

## 5. Ollama

Export/merge to a compatible GGUF using the selected model's supported conversion workflow, place it at `ollama/techspace-llm.gguf`, then:

```bash
cd ollama
ollama create techspace-llm -f Modelfile
ollama run techspace-llm
```

## Training gates

Every release should record model ID, dataset revisions, commit SHA, training configuration, hardware, evaluation results, known limitations, and license/provenance information.
