#!/usr/bin/env python3
"""
Script 07 - Iniciar Assistente Virtual Médico (Gradio)
======================================================
Inicia a interface Gradio do assistente médico multi-agente.

Uso:
    python scripts/07_iniciar_app.py [--port PORT] [--share]

Pré-requisitos:
    - ChromaDB indexado (scripts/04_indexar_protocolos.py)
    - PostgreSQL populado (scripts/02_setup_postgres.py)
    - Modelo fine-tuned em models/ (opcional — usa fallback se ausente)
"""

import argparse
import sys
from pathlib import Path

# Adicionar raiz do projeto ao path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def main():
    parser = argparse.ArgumentParser(
        description="Inicia o Assistente Virtual Médico (interface Gradio)."
    )
    parser.add_argument(
        "--port", type=int, default=7860,
        help="Porta do servidor (padrão: 7860)",
    )
    parser.add_argument(
        "--share", action="store_true",
        help="Gera link público via Gradio Share",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("SCRIPT 07 - Assistente Virtual Médico (Gradio)")
    print("=" * 60)

    # Verificar pré-condições
    chroma_dir = PROJECT_ROOT / "chroma_db"
    if not chroma_dir.exists():
        print(f"\nAVISO: ChromaDB não encontrado em {chroma_dir}")
        print("Execute: python scripts/04_indexar_protocolos.py")
        print("O assistente funcionará sem RAG.\n")

    from app.main import build_interface

    print(f"\nIniciando servidor na porta {args.port}...")
    if args.share:
        print("Modo share ativado — um link público será gerado.\n")

    demo = build_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=args.port,
        share=args.share,
        theme="soft",
    )


if __name__ == "__main__":
    main()
