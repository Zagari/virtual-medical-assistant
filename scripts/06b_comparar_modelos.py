#!/usr/bin/env python3
"""
06b_comparar_modelos.py - Comparacao Unificada de 3 Modelos

Gera relatorio comparativo entre baseline, fine-tuned epoch 2 e epoch 5,
consolidando resultados de ambas as trilhas de avaliacao.

Trilha A (perguntas manuais): metricas de sobreposicao entre modelos
Trilha B (validacao MedQuAD): metricas contra ground truth + similaridade semantica

Entrada:
    Trilha A:
        data/evaluation/comparacao_resultados_epoch2.json
        data/evaluation/comparacao_resultados_epoch5.json
    Trilha B (opcional):
        data/evaluation/comparacao_resultados_epoch2_val.json
        data/evaluation/comparacao_resultados_epoch5_val.json

Saida:
    data/evaluation/comparacao_completa.json
    data/evaluation/comparacao_completa.md

Uso:
    python scripts/06b_comparar_modelos.py

Nao requer GPU.
"""

import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
EVALUATION_DIR = PROJECT_ROOT / "data" / "evaluation"

# Arquivos de entrada — Trilha A (perguntas manuais)
COMP_EPOCH2 = EVALUATION_DIR / "comparacao_resultados_epoch2.json"
COMP_EPOCH5 = EVALUATION_DIR / "comparacao_resultados_epoch5.json"

# Arquivos de entrada — Trilha B (validacao MedQuAD, opcional)
COMP_EPOCH2_VAL = EVALUATION_DIR / "comparacao_resultados_epoch2_val.json"
COMP_EPOCH5_VAL = EVALUATION_DIR / "comparacao_resultados_epoch5_val.json"

# Respostas para exemplos qualitativos
BASELINE_RESPONSES = EVALUATION_DIR / "baseline_responses.json"
FT_EPOCH2_RESPONSES = EVALUATION_DIR / "finetuned_responses_epoch2.json"
FT_EPOCH5_RESPONSES = EVALUATION_DIR / "finetuned_responses_epoch5.json"

# Saida
OUTPUT_JSON = EVALUATION_DIR / "comparacao_completa.json"
OUTPUT_MD = EVALUATION_DIR / "comparacao_completa.md"


def load_json(filepath: Path) -> dict | None:
    if not filepath.exists():
        return None
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data: dict, filepath: Path):
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def detect_repetition_rate(text: str, n: int = 3) -> float:
    """Detecta taxa de repeticao por n-gramas repetidos."""
    words = text.lower().split()
    if len(words) < n:
        return 0.0
    ngrams = [tuple(words[i:i+n]) for i in range(len(words) - n + 1)]
    if not ngrams:
        return 0.0
    unique = set(ngrams)
    return 1.0 - len(unique) / len(ngrams)


def calculate_repetition_rates(responses_file: Path) -> float | None:
    """Calcula taxa media de repeticao das respostas."""
    data = load_json(responses_file)
    if not data:
        return None
    rates = []
    for r in data.get('respostas', []):
        text = r.get('resposta', '')
        if text:
            rates.append(detect_repetition_rate(text))
    return sum(rates) / len(rates) if rates else 0.0


def main():
    print("=" * 60)
    print("  COMPARACAO UNIFICADA DE MODELOS")
    print("=" * 60)
    print()

    # Carregar resultados
    print("[1/3] Carregando resultados das avaliacoes...")

    comp_epoch2 = load_json(COMP_EPOCH2)
    comp_epoch5 = load_json(COMP_EPOCH5)

    if not comp_epoch2 or not comp_epoch5:
        missing = []
        if not comp_epoch2:
            missing.append(str(COMP_EPOCH2))
        if not comp_epoch5:
            missing.append(str(COMP_EPOCH5))
        print(f"ERRO: Arquivos nao encontrados: {missing}")
        print("Execute primeiro:")
        print("  python scripts/06_avaliar_finetuned.py --model-path ... --tag epoch2")
        print("  python scripts/06_avaliar_finetuned.py --model-path ... --tag epoch5")
        raise SystemExit(1)

    # Trilha B (opcional)
    comp_epoch2_val = load_json(COMP_EPOCH2_VAL)
    comp_epoch5_val = load_json(COMP_EPOCH5_VAL)
    has_trilha_b = comp_epoch2_val is not None and comp_epoch5_val is not None

    print(f"      Trilha A: epoch2 e epoch5 carregados")
    if has_trilha_b:
        print(f"      Trilha B: epoch2_val e epoch5_val carregados")
    else:
        print(f"      Trilha B: nao disponivel (resultados de validacao ausentes)")
    print()

    # Calcular taxas de repeticao
    print("[2/3] Calculando taxas de repeticao...")
    rep_baseline = calculate_repetition_rates(BASELINE_RESPONSES)
    rep_epoch2 = calculate_repetition_rates(FT_EPOCH2_RESPONSES)
    rep_epoch5 = calculate_repetition_rates(FT_EPOCH5_RESPONSES)
    print(f"      Baseline: {rep_baseline:.4f}" if rep_baseline is not None else "      Baseline: N/A")
    print(f"      Epoch 2:  {rep_epoch2:.4f}" if rep_epoch2 is not None else "      Epoch 2: N/A")
    print(f"      Epoch 5:  {rep_epoch5:.4f}" if rep_epoch5 is not None else "      Epoch 5: N/A")
    print()

    # Montar dados consolidados
    m2 = comp_epoch2.get("metrics", {})
    m5 = comp_epoch5.get("metrics", {})

    consolidated = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "trilha_a": True,
            "trilha_b": has_trilha_b,
        },
        "trilha_a": {
            "descricao": "50 perguntas manuais — metricas de sobreposicao FT vs Baseline",
            "baseline": {
                "avg_length": m2.get("baseline", {}).get("avg_length", 0),
                "repetition_rate": rep_baseline,
            },
            "epoch2": {
                "avg_length": m2.get("finetuned", {}).get("avg_length", 0),
                "bleu_vs_baseline": m2.get("averages", {}).get("bleu", 0),
                "rouge1_vs_baseline": m2.get("averages", {}).get("rouge1", 0),
                "rouge2_vs_baseline": m2.get("averages", {}).get("rouge2", 0),
                "rougeL_vs_baseline": m2.get("averages", {}).get("rougeL", 0),
                "repetition_rate": rep_epoch2,
            },
            "epoch5": {
                "avg_length": m5.get("finetuned", {}).get("avg_length", 0),
                "bleu_vs_baseline": m5.get("averages", {}).get("bleu", 0),
                "rouge1_vs_baseline": m5.get("averages", {}).get("rouge1", 0),
                "rouge2_vs_baseline": m5.get("averages", {}).get("rouge2", 0),
                "rougeL_vs_baseline": m5.get("averages", {}).get("rougeL", 0),
                "repetition_rate": rep_epoch5,
            },
        },
    }

    if has_trilha_b:
        r2 = comp_epoch2_val.get("metrics", {}).get("reference", {})
        r5 = comp_epoch5_val.get("metrics", {}).get("reference", {})

        consolidated["trilha_b"] = {
            "descricao": "50 amostras validacao MedQuAD — metricas vs ground truth",
            "baseline": r2.get("baseline", {}),
            "epoch2": r2.get("finetuned", {}),
            "epoch5": r5.get("finetuned", {}),
        }

    save_json(consolidated, OUTPUT_JSON)
    print(f"      Salvo: {OUTPUT_JSON}")

    # Gerar relatorio Markdown
    print("[3/3] Gerando relatorio unificado...")
    lines = generate_report(consolidated, has_trilha_b)

    with open(OUTPUT_MD, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"      Salvo: {OUTPUT_MD}")

    print()
    print("=" * 60)
    print("  COMPARACAO CONCLUIDA")
    print("=" * 60)
    print()


def fmt(val, decimals=4):
    """Formata valor numerico ou retorna N/A."""
    if val is None:
        return "N/A"
    return f"{val:.{decimals}f}"


def generate_report(data: dict, has_trilha_b: bool) -> list[str]:
    """Gera relatorio Markdown unificado."""
    ta = data["trilha_a"]
    base = ta["baseline"]
    e2 = ta["epoch2"]
    e5 = ta["epoch5"]

    lines = [
        "# Comparacao Completa: Baseline vs Epoch 2 vs Epoch 5",
        "",
        f"**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Trilha A — Sobreposicao entre Modelos (50 perguntas manuais)",
        "",
        "Metricas calculadas comparando cada modelo fine-tuned com o baseline.",
        "",
        "| Metrica | Baseline | FT Epoch 2 | FT Epoch 5 |",
        "|---------|----------|------------|------------|",
        f"| Comprimento medio | {fmt(base['avg_length'], 0)} chars | {fmt(e2['avg_length'], 0)} chars | {fmt(e5['avg_length'], 0)} chars |",
        f"| BLEU vs Baseline | — | {fmt(e2['bleu_vs_baseline'])} | {fmt(e5['bleu_vs_baseline'])} |",
        f"| ROUGE-1 F1 vs Baseline | — | {fmt(e2['rouge1_vs_baseline'])} | {fmt(e5['rouge1_vs_baseline'])} |",
        f"| ROUGE-2 F1 vs Baseline | — | {fmt(e2['rouge2_vs_baseline'])} | {fmt(e5['rouge2_vs_baseline'])} |",
        f"| ROUGE-L F1 vs Baseline | — | {fmt(e2['rougeL_vs_baseline'])} | {fmt(e5['rougeL_vs_baseline'])} |",
        f"| Taxa de repeticao (3-gramas) | {fmt(base.get('repetition_rate'))} | {fmt(e2.get('repetition_rate'))} | {fmt(e5.get('repetition_rate'))} |",
        "",
    ]

    if has_trilha_b:
        tb = data["trilha_b"]
        tb_base = tb["baseline"]
        tb_e2 = tb["epoch2"]
        tb_e5 = tb["epoch5"]

        lines.extend([
            "## Trilha B — Qualidade vs Ground Truth (50 amostras validacao MedQuAD)",
            "",
            "Metricas calculadas comparando as respostas de cada modelo com a resposta de referencia.",
            "",
            "| Metrica | Baseline | FT Epoch 2 | FT Epoch 5 |",
            "|---------|----------|------------|------------|",
            f"| BLEU vs Referencia | {fmt(tb_base.get('bleu'))} | {fmt(tb_e2.get('bleu'))} | {fmt(tb_e5.get('bleu'))} |",
            f"| ROUGE-1 F1 vs Ref | {fmt(tb_base.get('rouge1'))} | {fmt(tb_e2.get('rouge1'))} | {fmt(tb_e5.get('rouge1'))} |",
            f"| ROUGE-2 F1 vs Ref | {fmt(tb_base.get('rouge2'))} | {fmt(tb_e2.get('rouge2'))} | {fmt(tb_e5.get('rouge2'))} |",
            f"| ROUGE-L F1 vs Ref | {fmt(tb_base.get('rougeL'))} | {fmt(tb_e2.get('rougeL'))} | {fmt(tb_e5.get('rougeL'))} |",
        ])

        if "semantic_similarity" in tb_base:
            lines.append(
                f"| Similaridade Semantica | {fmt(tb_base.get('semantic_similarity'))} | {fmt(tb_e2.get('semantic_similarity'))} | {fmt(tb_e5.get('semantic_similarity'))} |"
            )

        lines.append("")

    # Exemplos qualitativos
    baseline_data = load_json(BASELINE_RESPONSES)
    epoch2_data = load_json(FT_EPOCH2_RESPONSES)
    epoch5_data = load_json(FT_EPOCH5_RESPONSES)

    if baseline_data and epoch2_data and epoch5_data:
        lines.extend([
            "## Exemplos Qualitativos (3 modelos lado a lado)",
            "",
        ])

        b_resps = baseline_data['respostas']
        e2_resps = epoch2_data['respostas']
        e5_resps = epoch5_data['respostas']

        # Agrupar por categoria
        categorias = {}
        for b, e2r, e5r in zip(b_resps, e2_resps, e5_resps):
            cat = b['categoria']
            if cat not in categorias:
                categorias[cat] = []
            categorias[cat].append((b, e2r, e5r))

        for cat, items in categorias.items():
            lines.extend([
                f"### {cat.title()}",
                "",
            ])

            for b, e2r, e5r in items[:1]:  # 1 exemplo por categoria
                lines.extend([
                    f"**Pergunta {b['id']}:** {b['pergunta']}",
                    "",
                    "<details>",
                    "<summary>Ver respostas dos 3 modelos</summary>",
                    "",
                    "**Baseline:**",
                    "```",
                    b['resposta'][:400] + ("..." if len(b['resposta']) > 400 else ""),
                    "```",
                    "",
                    "**Fine-Tuned Epoch 2:**",
                    "```",
                    e2r['resposta'][:400] + ("..." if len(e2r['resposta']) > 400 else ""),
                    "```",
                    "",
                    "**Fine-Tuned Epoch 5:**",
                    "```",
                    e5r['resposta'][:400] + ("..." if len(e5r['resposta']) > 400 else ""),
                    "```",
                    "",
                    "</details>",
                    "",
                ])

    # Recomendacao
    lines.extend([
        "## Recomendacao",
        "",
        "Com base nos resultados acima, a recomendacao sera preenchida apos analise dos dados.",
        "",
    ])

    return lines


if __name__ == "__main__":
    main()
