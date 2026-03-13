"""Exporta o modelo fine-tuned (LoRA) para formato GGUF quantizado.

Executa no servidor com GPU (onde o modelo foi treinado).
O GGUF resultante funciona em qualquer maquina (CPU, Mac, Windows).

Uso:
    python scripts/08_exportar_gguf.py
    python scripts/08_exportar_gguf.py --model-path models/checkpoints/checkpoint-2000 --gguf-filename medical-assistant-epoch2-Q4_K_M.gguf
    python scripts/08_exportar_gguf.py --model-path models/medical-assistant-final --gguf-filename medical-assistant-epoch5-Q4_K_M.gguf

Pre-requisitos:
    pip install llama-cpp-python
    (o unsloth ja deve estar instalado no ambiente de treino)

O que faz:
    1. Merge dos adapters LoRA com o modelo base (Mistral 7B)
    2. Exporta para GGUF com quantizacao Q4_K_M (~4GB)
    3. Opcionalmente faz upload para o Hugging Face Hub
"""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# ---------------------------------------------------------------------------
# Configuracao
# ---------------------------------------------------------------------------

DEFAULT_MODEL_DIR = PROJECT_ROOT / "models" / "medical-assistant-final"
GGUF_OUTPUT_DIR = Path("/mnt/dados/interno/gguf")
QUANTIZATION = "q4_k_m"
GGUF_README_PATH = PROJECT_ROOT / "models" / "gguf" / "README.md"

load_dotenv(PROJECT_ROOT / ".env")

HF_TOKEN = os.getenv("HF_TOKEN", "")
GGUF_HUB_REPO = os.getenv("GGUF_HUB_REPO", "zagari/medical-assistant-mistral-7b-ft-gguf")
DEFAULT_GGUF_FILENAME = os.getenv("GGUF_FILENAME", "medical-assistant-Q4_K_M.gguf")


def main():
    parser = argparse.ArgumentParser(
        description="Exporta modelo fine-tuned (LoRA) para GGUF quantizado"
    )
    parser.add_argument(
        '--model-path', type=str, default=None,
        help='Caminho para o modelo fine-tuned (default: models/medical-assistant-final)'
    )
    parser.add_argument(
        '--gguf-filename', type=str, default=None,
        help='Nome do arquivo GGUF no HF Hub (default: medical-assistant-Q4_K_M.gguf)'
    )
    args = parser.parse_args()

    model_dir = Path(args.model_path) if args.model_path else DEFAULT_MODEL_DIR
    gguf_filename = args.gguf_filename or DEFAULT_GGUF_FILENAME

    print("=" * 60)
    print("  EXPORTAR MODELO FINE-TUNED PARA GGUF")
    print("=" * 60)
    print()
    print(f"  Modelo: {model_dir}")
    print(f"  GGUF:   {gguf_filename}")
    print()

    if not model_dir.exists():
        print(f"ERRO: Modelo nao encontrado em {model_dir}")
        print("Execute o fine-tuning primeiro.")
        sys.exit(1)

    # ----- Passo 1: Carregar modelo com Unsloth -----
    print("[1/3] Carregando modelo fine-tuned com Unsloth...")
    from unsloth import FastLanguageModel

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=str(model_dir),
        max_seq_length=2048,
        dtype=None,
        load_in_4bit=True,
    )
    print("      Modelo carregado.")
    print()

    # ----- Passo 2: Exportar para GGUF -----
    print(f"[2/3] Exportando para GGUF ({QUANTIZATION})...")
    print(f"      Destino: {GGUF_OUTPUT_DIR}")
    GGUF_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    model.save_pretrained_gguf(
        str(GGUF_OUTPUT_DIR),
        tokenizer,
        quantization_method=QUANTIZATION,
    )

    # Encontrar arquivo gerado
    # Unsloth adiciona sufixo "_gguf" ao diretorio de saida
    gguf_actual_dir = Path(str(GGUF_OUTPUT_DIR) + "_gguf")
    search_dirs = [GGUF_OUTPUT_DIR, gguf_actual_dir]
    gguf_files = []
    for d in search_dirs:
        if d.exists():
            gguf_files.extend(d.glob("*.gguf"))
    if not gguf_files:
        print("ERRO: Nenhum arquivo GGUF gerado.")
        print(f"  Procurei em: {[str(d) for d in search_dirs]}")
        sys.exit(1)

    gguf_file = gguf_files[0]
    size_gb = gguf_file.stat().st_size / (1024 ** 3)
    print(f"      Arquivo gerado: {gguf_file.name} ({size_gb:.2f} GB)")
    print()

    # ----- Passo 3: Upload para HF Hub (opcional) -----
    if not HF_TOKEN:
        print("[3/3] Upload para HF Hub: PULADO (HF_TOKEN nao configurado)")
        print()
        print("Para fazer upload manualmente:")
        print(f"  huggingface-cli upload {GGUF_HUB_REPO} {gguf_file} {gguf_filename}")
    else:
        print(f"[3/3] Enviando para HF Hub: {GGUF_HUB_REPO}...")
        from huggingface_hub import HfApi, login

        login(token=HF_TOKEN)
        api = HfApi()
        api.create_repo(repo_id=GGUF_HUB_REPO, exist_ok=True, private=False)

        # Upload README (model card)
        readme_path = GGUF_README_PATH
        if readme_path.exists():
            api.upload_file(
                path_or_fileobj=str(readme_path),
                path_in_repo="README.md",
                repo_id=GGUF_HUB_REPO,
                commit_message="Adicionar model card",
            )
            print("      README.md enviado.")

        # Upload GGUF
        api.upload_file(
            path_or_fileobj=str(gguf_file),
            path_in_repo=gguf_filename,
            repo_id=GGUF_HUB_REPO,
            commit_message=f"Upload GGUF {QUANTIZATION} ({gguf_filename})",
        )
        print(f"      Enviado: https://huggingface.co/{GGUF_HUB_REPO}")

    print()
    print("=" * 60)
    print("  EXPORTACAO CONCLUIDA")
    print("=" * 60)
    print()
    print(f"Arquivo GGUF: {gguf_file}")
    print(f"Tamanho: {size_gb:.2f} GB")
    print()
    print("Para usar no app sem GPU:")
    print("  1. Copie o .gguf para models/ no destino")
    print("  2. pip install llama-cpp-python")
    print("  3. python scripts/07_iniciar_app.py")


if __name__ == "__main__":
    main()
