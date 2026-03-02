#!/usr/bin/env python3
"""
Script 01 - Gerar Dados Sinteticos
===================================
Gera pacientes ficticios, exames, prontuarios e receitas medicas.
Os dados sao salvos em data/synthetic/ como arquivos JSON.

Uso:
    python scripts/01_gerar_dados_sinteticos.py [--n_patients 80]

Saida:
    data/synthetic/pacientes.json      - 80 pacientes com comorbidades
    data/synthetic/exames.json         - ~240 exames (2-4 por paciente)
    data/synthetic/prontuarios.json    - ~280 prontuarios (2-5 por paciente)
    data/synthetic/receitas.json       - ~160 receitas (1-3 por paciente)
"""

import argparse
import sys
from pathlib import Path

# Adicionar raiz do projeto ao path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.data.synthetic_generator import generate_all


def main():
    parser = argparse.ArgumentParser(
        description="Gera dados sintéticos de pacientes para o assistente médico."
    )
    parser.add_argument(
        "--n_patients",
        type=int,
        default=80,
        help="Número de pacientes a gerar (padrão: 80)",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("SCRIPT 01 - Geração de Dados Sintéticos")
    print("=" * 60)

    output_dir = PROJECT_ROOT / "data" / "synthetic"

    result = generate_all(
        n_patients=args.n_patients,
        output_dir=str(output_dir),
    )

    print("\n" + "=" * 60)
    print("Concluído! Arquivos gerados em data/synthetic/")
    print("Próximo passo: python scripts/02_setup_postgres.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
