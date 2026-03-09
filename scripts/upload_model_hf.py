#!/usr/bin/env python3
"""
Upload do modelo ótimo (checkpoint-1500 / epoch_1_5) para o Hugging Face Hub.

Uso:
    python scripts/upload_model_hf.py

Requer HF_TOKEN no arquivo .env do projeto (com permissão Write).
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

PROJECT_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = PROJECT_DIR / "models" / "medical-assistant-epoch_1_5"
HF_HUB_REPO = "zagari/medical-assistant-mistral-7b-ft"

# ============================================================================
# CARREGAR .env
# ============================================================================

load_dotenv(PROJECT_DIR / ".env")

HF_TOKEN = os.getenv("HF_TOKEN", "")

# ============================================================================
# VALIDAÇÕES
# ============================================================================

if not HF_TOKEN:
    print("ERRO: HF_TOKEN não configurado.")
    print("  Configure no arquivo .env do projeto:")
    print("    HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxx")
    print("")
    print("  Crie seu token em: https://huggingface.co/settings/tokens (permissão Write)")
    sys.exit(1)

if not MODEL_DIR.exists():
    print(f"ERRO: Diretório do modelo não encontrado: {MODEL_DIR}")
    sys.exit(1)

# Verificar arquivos essenciais
required_files = ["adapter_config.json", "adapter_model.safetensors", "tokenizer.json"]
missing = [f for f in required_files if not (MODEL_DIR / f).exists()]
if missing:
    print(f"ERRO: Arquivos faltando no modelo: {', '.join(missing)}")
    sys.exit(1)

# ============================================================================
# LISTAR ARQUIVOS QUE SERÃO ENVIADOS
# ============================================================================

print("=" * 60)
print(f"  Upload do modelo para Hugging Face Hub")
print("=" * 60)
print("")
print(f"  Modelo local: {MODEL_DIR}")
print(f"  Destino: https://huggingface.co/{HF_HUB_REPO}")
print("")
print("  Arquivos:")
total_size = 0
for f in sorted(MODEL_DIR.iterdir()):
    if f.is_file():
        size_mb = f.stat().st_size / (1024 * 1024)
        total_size += size_mb
        print(f"    {f.name}: {size_mb:.2f} MB")
print(f"  Total: {total_size:.2f} MB")
print("")

# ============================================================================
# UPLOAD
# ============================================================================

from huggingface_hub import HfApi, login

login(token=HF_TOKEN)
print("Autenticado no Hugging Face Hub")

api = HfApi()
api.create_repo(repo_id=HF_HUB_REPO, exist_ok=True, private=False)

commit_msg = (
    "Upload adapters LoRA checkpoint-1500 (Sessão 3, max_steps=1500) "
    "— melhor modelo: eval_loss=0.6539, BLEU=0.298, ROUGE-L=0.421, "
    "sim. semântica=0.939 vs ground truth MedQuAD"
)

print(f"Enviando para {HF_HUB_REPO}...")
print(f"  Commit: {commit_msg[:80]}...")
print("")

api.upload_folder(
    folder_path=str(MODEL_DIR),
    repo_id=HF_HUB_REPO,
    commit_message=commit_msg,
)

print(f"Upload concluído!")
print(f"  URL: https://huggingface.co/{HF_HUB_REPO}")
