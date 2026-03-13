---
base_model: mistralai/Mistral-7B-Instruct-v0.3
library_name: llama-cpp
pipeline_tag: text-generation
license: apache-2.0
language:
- pt
- en
tags:
- medical
- healthcare
- gguf
- quantized
- mistral
- fine-tuned
datasets:
- MedQuAD
model-index:
- name: medical-assistant-mistral-7b-ft-gguf
  results:
  - task:
      type: text-generation
      name: Medical Question Answering
    metrics:
    - type: bleu
      value: 0.298
      name: BLEU (vs MedQuAD ground truth)
    - type: rouge
      value: 0.421
      name: ROUGE-L (vs MedQuAD ground truth)
    - type: cosine_similarity
      value: 0.939
      name: Semantic Similarity (vs MedQuAD ground truth)
---

# Medical Assistant — Mistral 7B Fine-Tuned (GGUF) — Optimal Checkpoint

GGUF-quantized version of [`zagari/medical-assistant-mistral-7b-ft`](https://huggingface.co/zagari/medical-assistant-mistral-7b-ft) for **local inference without GPU**.

This is the **optimal checkpoint** (step 1500, ~1.3 effective epochs), selected after multi-checkpoint evaluation across 3 training sessions. Quantized to Q4_K_M (~4 GB) for portable execution on CPU and Apple Silicon.

This model runs on **CPU**, **Apple Silicon (Metal)**, and **Windows** via [llama.cpp](https://github.com/ggerganov/llama.cpp) or [llama-cpp-python](https://github.com/abetlen/llama-cpp-python).

Developed as part of the **Tech Challenge Phase 3** — Post-Graduate Program in AI for Developers at FIAP (São Paulo, Brazil).

> **WARNING:** This is an academic project. It must NOT be used for real clinical decisions. All responses must be validated by a qualified healthcare professional.

## Quick Start

### Install

```bash
# Mac (Apple Silicon — Metal acceleration)
CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python

# Linux/Windows (CPU only)
pip install llama-cpp-python
```

### Usage with llama-cpp-python

```python
from llama_cpp import Llama

model = Llama(
    model_path="medical-assistant-Q4_K_M.gguf",
    n_ctx=2048,
)

prompt = """Abaixo está uma instrução que descreve uma tarefa, junto com uma entrada que fornece contexto adicional. Escreva uma resposta que complete adequadamente a solicitação.

### Instrução:
Responda a seguinte pergunta médica de forma clara e detalhada.

### Entrada:
Quais são os sintomas do diabetes tipo 2?

### Resposta:
"""

output = model(prompt, max_tokens=512, temperature=0.7)
print(output["choices"][0]["text"])
```

### Usage with the Virtual Medical Assistant app

The app auto-detects your hardware and loads the GGUF model when no CUDA GPU is available:

```bash
# 1. Clone the repo
git clone https://github.com/zagari/virtual-medical-assistant.git
cd virtual-medical-assistant

# 2. Install dependencies
pip install -r requirements.txt
pip install llama-cpp-python  # or with Metal on Mac

# 3. Download this GGUF to models/
# (automatic on first run, or manual:)
huggingface-cli download zagari/medical-assistant-mistral-7b-ft-gguf \
    medical-assistant-Q4_K_M.gguf --local-dir models/

# 4. Run
python scripts/07_iniciar_app.py
```

## Model Details

| Property | Value |
|---|---|
| Base model | Mistral 7B Instruct v0.3 |
| Fine-tuning | QLoRA (LoRA r=64, alpha=128) |
| Training data | MedQuAD (~20.5k QA pairs: 80% PT + 20% EN + Brazilian supplement) |
| Checkpoint | Step 1500 (~1.3 effective epochs) — optimal from multi-checkpoint evaluation |
| Quantization | Q4_K_M (4-bit, medium quality) |
| File size | ~4 GB |
| Context length | 2,048 tokens |
| Prompt format | Alpaca (Instruction / Input / Output) |

## Evaluation Results (before quantization)

Evaluated on 50 medical questions against MedQuAD reference answers:

| Metric | Baseline (Mistral 7B) | Fine-tuned (this model) | Improvement |
|---|---|---|---|
| BLEU | 0.039 | 0.298 | +664% |
| ROUGE-L | 0.175 | 0.421 | +141% |
| Semantic Similarity | 0.904 | 0.939 | +3.9% |

## Quantization

This GGUF was created by:
1. Merging the LoRA adapters (optimal checkpoint-1500) with the base Mistral 7B model
2. Converting to GGUF format with Q4_K_M quantization via Unsloth

Q4_K_M offers a good balance between size and quality — it is the recommended quantization for most use cases.

### Performance comparison

| Format | Size | Requires | Speed (approx.) |
|---|---|---|---|
| LoRA + base (4-bit) | ~640MB + 4GB base | NVIDIA GPU (CUDA) | ~2-5s/response |
| **GGUF Q4_K_M** | **~4 GB** | **CPU or Apple Silicon** | **~5-15s/response** |
| Full float16 | ~14 GB | 14GB+ RAM | ~2-5min/response |

## Source Model

The LoRA adapters and full training details (including multi-checkpoint evaluation and learning rate analysis) are available at:
[`zagari/medical-assistant-mistral-7b-ft`](https://huggingface.co/zagari/medical-assistant-mistral-7b-ft)

- **Developed by:** Adriana Martins, Diego Oliveira, Eduardo Zagari, Renan Torres
- **License:** Apache 2.0
- **Repository:** [github.com/zagari/virtual-medical-assistant](https://github.com/zagari/virtual-medical-assistant)

## Citation

```bibtex
@misc{medical-assistant-fiap-2026,
  title={Virtual Medical Assistant with Fine-Tuning and LangGraph},
  author={Martins, Adriana and Oliveira, Diego and Zagari, Eduardo and Torres, Renan},
  year={2026},
  note={Tech Challenge Phase 3 — FIAP Post-Graduate Program in AI for Developers}
}
```
