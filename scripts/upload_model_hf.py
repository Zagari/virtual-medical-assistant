#!/usr/bin/env python3
"""
Upload do modelo fine-tuned (LoRA adapters) para o Hugging Face Hub.

Envia os arquivos do adapter + README.md (Model Card) para o repositorio
configurado em HF_HUB_REPO.

Uso:
    python scripts/upload_model_hf.py
    python scripts/upload_model_hf.py --model-path models/medical-assistant-epoch_1_5

Requer HF_TOKEN no arquivo .env do projeto (com permissao Write).
"""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# ============================================================================
# CONFIGURACAO
# ============================================================================

PROJECT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_MODEL_DIR = PROJECT_DIR / "models" / "medical-assistant-final"

load_dotenv(PROJECT_DIR / ".env")
HF_TOKEN = os.getenv("HF_TOKEN", "")
HF_HUB_REPO = os.getenv("HF_HUB_REPO", "zagari/medical-assistant-mistral-7b-ft")


def main():
    parser = argparse.ArgumentParser(
        description="Upload de adapters LoRA + Model Card para o Hugging Face Hub."
    )
    parser.add_argument(
        "--model-path", type=str, default=None,
        help=f"Caminho do modelo (default: {DEFAULT_MODEL_DIR})",
    )
    args = parser.parse_args()

    model_dir = Path(args.model_path) if args.model_path else DEFAULT_MODEL_DIR

    # ========================================================================
    # VALIDACOES
    # ========================================================================

    if not HF_TOKEN:
        print("ERRO: HF_TOKEN nao configurado.")
        print("  Configure no arquivo .env do projeto:")
        print("    HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxx")
        print()
        print("  Crie seu token em: https://huggingface.co/settings/tokens (permissao Write)")
        sys.exit(1)

    if not model_dir.exists():
        print(f"ERRO: Diretorio do modelo nao encontrado: {model_dir}")
        sys.exit(1)

    required_files = ["adapter_config.json", "adapter_model.safetensors"]
    missing = [f for f in required_files if not (model_dir / f).exists()]
    if missing:
        print(f"ERRO: Arquivos faltando no modelo: {', '.join(missing)}")
        sys.exit(1)

    readme_path = model_dir / "README.md"
    if not readme_path.exists():
        print(f"AVISO: README.md (Model Card) nao encontrado em {model_dir}")

    # ========================================================================
    # LISTAR ARQUIVOS
    # ========================================================================

    print("=" * 60)
    print("  Upload do modelo para Hugging Face Hub")
    print("=" * 60)
    print()
    print(f"  Modelo local: {model_dir}")
    print(f"  Destino:      https://huggingface.co/{HF_HUB_REPO}")
    print()
    print("  Arquivos:")
    total_size = 0
    for f in sorted(model_dir.iterdir()):
        if f.is_file():
            size_mb = f.stat().st_size / (1024 * 1024)
            total_size += size_mb
            print(f"    {f.name}: {size_mb:.2f} MB")
    print(f"  Total: {total_size:.2f} MB")
    print()

    # ========================================================================
    # UPLOAD
    # ========================================================================

    from huggingface_hub import HfApi, login

    login(token=HF_TOKEN)
    print("Autenticado no Hugging Face Hub")

    api = HfApi()
    api.create_repo(repo_id=HF_HUB_REPO, exist_ok=True, private=False)

    commit_msg = "Upload LoRA adapters + Model Card"

    print(f"Enviando para {HF_HUB_REPO}...")
    print()

    api.upload_folder(
        folder_path=str(model_dir),
        repo_id=HF_HUB_REPO,
        commit_message=commit_msg,
    )

    print(f"Upload concluido!")
    print(f"  URL: https://huggingface.co/{HF_HUB_REPO}")


if __name__ == "__main__":
    main()
