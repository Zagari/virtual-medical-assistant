#!/usr/bin/env python3
"""
06b_comparar_modelos.py - Comparacao Unificada de Modelos (Dinamico)

Descobre automaticamente quais checkpoints foram avaliados e gera
relatorio comparativo consolidando ambas as trilhas de avaliacao.

Trilha A (perguntas manuais): metricas de sobreposicao entre modelos
Trilha B (validacao MedQuAD): metricas contra ground truth + similaridade semantica

Descobre os arquivos disponíveis em data/evaluation/:
    comparacao_resultados_{tag}.json      -> Trilha A
    comparacao_resultados_{tag}_val.json  -> Trilha B

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

BASELINE_RESPONSES = EVALUATION_DIR / "baseline_responses.json"
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


def tag_sort_key(tag: str) -> float:
    """Ordena tags por numero do epoch (epoch0_5 -> 0.5, epoch2 -> 2.0)."""
    num_str = tag.replace("epoch", "").replace("_", ".")
    try:
        return float(num_str)
    except ValueError:
        return 999.0


def tag_display_name(tag: str) -> str:
    """Converte tag em nome legivel (epoch2_5 -> 'Epoch 2.5')."""
    num_str = tag.replace("epoch", "").replace("_", ".")
    try:
        num = float(num_str)
        if num == int(num):
            return f"Epoch {int(num)}"
        return f"Epoch {num}"
    except ValueError:
        return tag


def discover_epochs() -> list[str]:
    """Descobre quais epochs foram avaliados (Trilha A)."""
    epochs = []
    for f in EVALUATION_DIR.glob("comparacao_resultados_*.json"):
        tag = f.stem.replace("comparacao_resultados_", "")
        if tag.endswith("_val"):
            continue
        epochs.append(tag)
    return sorted(epochs, key=tag_sort_key)


def discover_val_epochs() -> list[str]:
    """Descobre quais epochs foram avaliados (Trilha B)."""
    epochs = []
    for f in EVALUATION_DIR.glob("comparacao_resultados_*_val.json"):
        tag = f.stem.replace("comparacao_resultados_", "")
        if tag.endswith("_val"):
            tag = tag[:-4]
        epochs.append(tag)
    return sorted(epochs, key=tag_sort_key)


def main():
    print("=" * 60)
    print("  COMPARACAO UNIFICADA DE MODELOS")
    print("=" * 60)
    print()

    # Descobrir epochs disponíveis
    print("[1/3] Descobrindo avaliacoes disponiveis...")
    epochs = discover_epochs()
    val_epochs = discover_val_epochs()

    if not epochs:
        print("ERRO: Nenhum arquivo comparacao_resultados_*.json encontrado.")
        print("Execute primeiro:")
        print("  python scripts/06_avaliar_finetuned.py --model-path ... --tag ...")
        raise SystemExit(1)

    has_trilha_b = len(val_epochs) > 0

    print(f"      Trilha A: {', '.join(epochs)} ({len(epochs)} checkpoints)")
    if has_trilha_b:
        print(f"      Trilha B: {', '.join(val_epochs)} ({len(val_epochs)} checkpoints)")
    else:
        print("      Trilha B: nao disponivel")
    print()

    # Carregar dados de comparacao
    comparisons = {}
    for tag in epochs:
        filepath = EVALUATION_DIR / f"comparacao_resultados_{tag}.json"
        comparisons[tag] = load_json(filepath)

    val_comparisons = {}
    for tag in val_epochs:
        filepath = EVALUATION_DIR / f"comparacao_resultados_{tag}_val.json"
        val_comparisons[tag] = load_json(filepath)

    # Calcular taxas de repeticao
    print("[2/3] Calculando taxas de repeticao...")
    rep_baseline = calculate_repetition_rates(BASELINE_RESPONSES)
    print(f"      Baseline: {rep_baseline:.4f}" if rep_baseline is not None else "      Baseline: N/A")

    rep_rates = {}
    for tag in epochs:
        responses_file = EVALUATION_DIR / f"finetuned_responses_{tag}.json"
        rep_rates[tag] = calculate_repetition_rates(responses_file)
        display = tag_display_name(tag)
        val = rep_rates[tag]
        print(f"      {display}: {val:.4f}" if val is not None else f"      {display}: N/A")
    print()

    # Montar dados consolidados
    # Pegar avg_length do baseline do primeiro comparison disponivel
    first_comp = comparisons[epochs[0]]
    baseline_avg_length = (
        first_comp.get("metrics", {}).get("baseline", {}).get("avg_length", 0)
        if first_comp else 0
    )

    consolidated = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "epochs": epochs,
            "val_epochs": val_epochs,
            "trilha_a": True,
            "trilha_b": has_trilha_b,
        },
        "trilha_a": {
            "descricao": "50 perguntas manuais — metricas de sobreposicao FT vs Baseline",
            "baseline": {
                "avg_length": baseline_avg_length,
                "repetition_rate": rep_baseline,
            },
        },
    }

    for tag in epochs:
        comp = comparisons[tag]
        if not comp:
            continue
        m = comp.get("metrics", {})
        consolidated["trilha_a"][tag] = {
            "avg_length": m.get("finetuned", {}).get("avg_length", 0),
            "bleu_vs_baseline": m.get("averages", {}).get("bleu", 0),
            "rouge1_vs_baseline": m.get("averages", {}).get("rouge1", 0),
            "rouge2_vs_baseline": m.get("averages", {}).get("rouge2", 0),
            "rougeL_vs_baseline": m.get("averages", {}).get("rougeL", 0),
            "repetition_rate": rep_rates.get(tag),
        }

    if has_trilha_b:
        consolidated["trilha_b"] = {
            "descricao": "50 amostras validacao MedQuAD — metricas vs ground truth",
        }
        # Pegar baseline do primeiro val comparison
        first_val = val_comparisons[val_epochs[0]]
        if first_val:
            consolidated["trilha_b"]["baseline"] = (
                first_val.get("metrics", {}).get("reference", {}).get("baseline", {})
            )

        for tag in val_epochs:
            comp = val_comparisons[tag]
            if not comp:
                continue
            consolidated["trilha_b"][tag] = (
                comp.get("metrics", {}).get("reference", {}).get("finetuned", {})
            )

    save_json(consolidated, OUTPUT_JSON)
    print(f"      Salvo: {OUTPUT_JSON}")

    # Gerar relatorio Markdown
    print("[3/3] Gerando relatorio unificado...")
    lines = generate_report(consolidated, epochs, val_epochs, has_trilha_b)

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


def generate_report(
    data: dict,
    epochs: list[str],
    val_epochs: list[str],
    has_trilha_b: bool,
) -> list[str]:
    """Gera relatorio Markdown unificado."""
    ta = data["trilha_a"]
    base = ta["baseline"]

    # Nomes das colunas
    model_names = ["Baseline"] + [f"FT {tag_display_name(tag)}" for tag in epochs]

    title = "Baseline vs " + " vs ".join(tag_display_name(tag) for tag in epochs)

    lines = [
        f"# Comparacao Completa: {title}",
        "",
        f"**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Modelos avaliados:** {len(model_names)} (baseline + {len(epochs)} checkpoints)",
        "",
        "## Trilha A — Sobreposicao entre Modelos (50 perguntas manuais)",
        "",
        "Metricas calculadas comparando cada modelo fine-tuned com o baseline.",
        "",
    ]

    # Header da tabela
    header = "| Metrica | " + " | ".join(model_names) + " |"
    sep = "|" + "|".join(["---------"] + ["------------"] * len(epochs)) + "|"
    lines.extend([header, sep])

    # Comprimento medio
    row = f"| Comprimento medio | {fmt(base['avg_length'], 0)} chars"
    for tag in epochs:
        e = ta.get(tag, {})
        row += f" | {fmt(e.get('avg_length'), 0)} chars"
    row += " |"
    lines.append(row)

    # Metricas de sobreposicao
    for metric_key, metric_label in [
        ("bleu_vs_baseline", "BLEU vs Baseline"),
        ("rouge1_vs_baseline", "ROUGE-1 F1 vs Baseline"),
        ("rouge2_vs_baseline", "ROUGE-2 F1 vs Baseline"),
        ("rougeL_vs_baseline", "ROUGE-L F1 vs Baseline"),
    ]:
        row = f"| {metric_label} | —"
        for tag in epochs:
            e = ta.get(tag, {})
            row += f" | {fmt(e.get(metric_key))}"
        row += " |"
        lines.append(row)

    # Taxa de repeticao
    row = f"| Taxa de repeticao (3-gramas) | {fmt(base.get('repetition_rate'))}"
    for tag in epochs:
        e = ta.get(tag, {})
        row += f" | {fmt(e.get('repetition_rate'))}"
    row += " |"
    lines.append(row)

    lines.append("")

    # Trilha B
    if has_trilha_b:
        tb = data["trilha_b"]
        tb_base = tb.get("baseline", {})

        val_model_names = ["Baseline"] + [f"FT {tag_display_name(tag)}" for tag in val_epochs]
        val_header = "| Metrica | " + " | ".join(val_model_names) + " |"
        val_sep = "|" + "|".join(["---------"] + ["------------"] * len(val_epochs)) + "|"

        lines.extend([
            "## Trilha B — Qualidade vs Ground Truth (50 amostras validacao MedQuAD)",
            "",
            "Metricas calculadas comparando as respostas de cada modelo com a resposta de referencia.",
            "",
            val_header, val_sep,
        ])

        for metric_key, metric_label in [
            ("bleu", "BLEU vs Referencia"),
            ("rouge1", "ROUGE-1 F1 vs Ref"),
            ("rouge2", "ROUGE-2 F1 vs Ref"),
            ("rougeL", "ROUGE-L F1 vs Ref"),
        ]:
            row = f"| {metric_label} | {fmt(tb_base.get(metric_key))}"
            for tag in val_epochs:
                e = tb.get(tag, {})
                row += f" | {fmt(e.get(metric_key))}"
            row += " |"
            lines.append(row)

        if "semantic_similarity" in tb_base:
            row = f"| Similaridade Semantica | {fmt(tb_base.get('semantic_similarity'))}"
            for tag in val_epochs:
                e = tb.get(tag, {})
                row += f" | {fmt(e.get('semantic_similarity'))}"
            row += " |"
            lines.append(row)

        lines.append("")

    # Exemplos qualitativos
    baseline_data = load_json(BASELINE_RESPONSES)
    epoch_responses = {}
    for tag in epochs:
        responses_file = EVALUATION_DIR / f"finetuned_responses_{tag}.json"
        resp_data = load_json(responses_file)
        if resp_data:
            epoch_responses[tag] = resp_data

    if baseline_data and epoch_responses:
        available_tags = [t for t in epochs if t in epoch_responses]
        n_models = len(available_tags) + 1

        lines.extend([
            f"## Exemplos Qualitativos ({n_models} modelos lado a lado)",
            "",
        ])

        b_resps = baseline_data['respostas']

        # Respostas por epoch
        epoch_resps = {}
        for tag in available_tags:
            epoch_resps[tag] = epoch_responses[tag]['respostas']

        # Agrupar por categoria
        categorias = {}
        for idx, b in enumerate(b_resps):
            cat = b['categoria']
            if cat not in categorias:
                categorias[cat] = []
            entry = {"baseline": b, "idx": idx}
            categorias[cat].append(entry)

        for cat, items in categorias.items():
            lines.extend([
                f"### {cat.title()}",
                "",
            ])

            for entry in items[:1]:  # 1 exemplo por categoria
                b = entry["baseline"]
                idx = entry["idx"]

                lines.extend([
                    f"**Pergunta {b['id']}:** {b['pergunta']}",
                    "",
                    "<details>",
                    f"<summary>Ver respostas dos {n_models} modelos</summary>",
                    "",
                    "**Baseline:**",
                    "```",
                    b['resposta'][:400] + ("..." if len(b['resposta']) > 400 else ""),
                    "```",
                    "",
                ])

                for tag in available_tags:
                    resps = epoch_resps.get(tag, [])
                    if idx < len(resps):
                        r = resps[idx]
                        display = tag_display_name(tag)
                        lines.extend([
                            f"**Fine-Tuned {display}:**",
                            "```",
                            r['resposta'][:400] + ("..." if len(r['resposta']) > 400 else ""),
                            "```",
                            "",
                        ])

                lines.extend([
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
