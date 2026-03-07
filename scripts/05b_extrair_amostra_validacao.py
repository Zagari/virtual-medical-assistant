#!/usr/bin/env python3
"""
05b_extrair_amostra_validacao.py - Extrai amostra do conjunto de validacao

Reproduz o split 90/10 (seed=42) feito no notebook de fine-tuning e
seleciona 50 amostras do conjunto de validacao COM respostas de referencia.

Essas amostras servem para avaliacao quantitativa contra ground truth
(BLEU, ROUGE, similaridade semantica).

Entrada:
    data/processed/training_data.jsonl

Saida:
    data/evaluation/validacao_amostra.json

Uso:
    python scripts/05b_extrair_amostra_validacao.py [--n-samples 50] [--seed 42]

Nao requer GPU — roda localmente.
"""

import json
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
TRAINING_DATA = PROJECT_ROOT / "data" / "processed" / "training_data.jsonl"
OUTPUT_FILE = PROJECT_ROOT / "data" / "evaluation" / "validacao_amostra.json"

SPLIT_SEED = 42
SPLIT_TEST_SIZE = 0.1
SAMPLE_SEED = 42
N_SAMPLES = 50


def main():
    parser = argparse.ArgumentParser(
        description="Extrai amostra do conjunto de validacao MedQuAD"
    )
    parser.add_argument(
        '--n-samples', type=int, default=N_SAMPLES,
        help='Numero de amostras a extrair (default: 50)'
    )
    parser.add_argument(
        '--seed', type=int, default=SAMPLE_SEED,
        help='Seed para amostragem (default: 42)'
    )
    args = parser.parse_args()

    print("=" * 60)
    print("  EXTRAIR AMOSTRA DE VALIDACAO")
    print("=" * 60)
    print()

    if not TRAINING_DATA.exists():
        print(f"ERRO: Arquivo de treino nao encontrado: {TRAINING_DATA}")
        print("Execute primeiro: python scripts/03_preparar_dataset.py")
        raise SystemExit(1)

    # Carregar dataset e reproduzir o split do notebook
    print("[1/3] Carregando dataset e reproduzindo split 90/10 (seed=42)...")
    try:
        from datasets import Dataset
    except ImportError:
        print("ERRO: Biblioteca 'datasets' nao encontrada.")
        print("Instale com: pip install datasets")
        raise SystemExit(1)

    # Carregar JSONL
    records = []
    with open(TRAINING_DATA, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    print(f"      Total de exemplos: {len(records)}")

    # Reproduzir exatamente o split do notebook
    dataset = Dataset.from_list(records)
    split = dataset.train_test_split(test_size=SPLIT_TEST_SIZE, seed=SPLIT_SEED)
    validation = split["test"]

    print(f"      Treino: {len(split['train'])} | Validacao: {len(validation)}")
    print()

    # Amostrar N exemplos
    print(f"[2/3] Selecionando {args.n_samples} amostras (seed={args.seed})...")
    import random
    rng = random.Random(args.seed)
    indices = sorted(rng.sample(range(len(validation)), min(args.n_samples, len(validation))))
    samples = [validation[i] for i in indices]

    print(f"      {len(samples)} amostras selecionadas")
    print()

    # Montar saida no formato esperado pelos scripts 05/06
    print("[3/3] Salvando arquivo de avaliacao...")
    output = {
        "metadata": {
            "description": f"{len(samples)} amostras do conjunto de validacao MedQuAD",
            "fonte": "training_data.jsonl (test_size=0.1, seed=42)",
            "split_seed": SPLIT_SEED,
            "sample_seed": args.seed,
            "total_validacao": len(validation),
            "total": len(samples),
        },
        "perguntas": []
    }

    for i, sample in enumerate(samples, start=1):
        pergunta = sample.get("input", "")
        resposta = sample.get("output", "")

        output["perguntas"].append({
            "id": i,
            "categoria": "validacao",
            "pergunta": pergunta,
            "resposta_referencia": resposta,
        })

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"      Salvo em: {OUTPUT_FILE}")
    print()
    print("=" * 60)
    print("  EXTRACAO CONCLUIDA")
    print("=" * 60)
    print()
    print(f"  Amostras: {len(samples)}")
    print(f"  Arquivo: {OUTPUT_FILE}")
    print()
    print("  Proximo passo (no servidor):")
    print("    python scripts/05_avaliar_baseline.py \\")
    print("      --questions-file data/evaluation/validacao_amostra.json --tag val")
    print()


if __name__ == "__main__":
    main()
