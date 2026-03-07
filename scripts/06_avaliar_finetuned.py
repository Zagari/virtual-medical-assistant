#!/usr/bin/env python3
"""
06_avaliar_finetuned.py - Avaliação do Modelo Fine-Tuned e Comparação

Este script:
1. Executa as mesmas 50 perguntas no modelo fine-tuned
2. Compara as respostas com o modelo base (baseline)
3. Gera métricas quantitativas (BLEU, ROUGE, comprimento)
4. Gera relatório comparativo lado a lado

Entrada:
    data/evaluation/perguntas_avaliacao.json
    data/evaluation/baseline_responses.json
    models/medical-assistant-final/ (ou caminho especificado)

Saída:
    data/evaluation/finetuned_responses.json
    data/evaluation/comparacao_resultados.json
    data/evaluation/comparacao_resultados.md (relatório legível)

Uso:
    python scripts/06_avaliar_finetuned.py [--model-path PATH] [--limit N]
    python scripts/06_avaliar_finetuned.py --model-path models/checkpoints/checkpoint-2000 --tag epoch2
    python scripts/06_avaliar_finetuned.py --tag epoch2_val --questions-file data/evaluation/validacao_amostra.json --baseline-file data/evaluation/baseline_responses_val.json

Flags:
    --model-path      Caminho para o modelo fine-tuned
    --limit N         Limita a N perguntas (para testes rápidos)
    --skip-metrics    Pula cálculo de métricas (mais rápido)
    --tag TAG         Sufixo nos arquivos de saída (ex: epoch2, epoch2_val)
    --questions-file  Arquivo de perguntas alternativo
    --baseline-file   Arquivo de baseline alternativo

Requisitos:
    pip install transformers peft accelerate bitsandbytes torch rouge-score nltk
"""

import json
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    from peft import PeftModel
    from tqdm import tqdm
except ImportError as e:
    print(f"Erro: Dependência não encontrada: {e}")
    print("Instale com: pip install transformers peft accelerate bitsandbytes torch tqdm")
    sys.exit(1)


# ============================================================================
# CONFIGURAÇÕES
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
EVALUATION_DIR = DATA_DIR / "evaluation"
MODELS_DIR = PROJECT_ROOT / "models"

DEFAULT_QUESTIONS_FILE = EVALUATION_DIR / "perguntas_avaliacao.json"
DEFAULT_BASELINE_FILE = EVALUATION_DIR / "baseline_responses.json"
DEFAULT_FINETUNED_FILE = EVALUATION_DIR / "finetuned_responses.json"
DEFAULT_COMPARISON_JSON = EVALUATION_DIR / "comparacao_resultados.json"
DEFAULT_COMPARISON_MD = EVALUATION_DIR / "comparacao_resultados.md"

# Modelos
BASE_MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.3"
DEFAULT_FINETUNED_PATH = MODELS_DIR / "medical-assistant-final"

MAX_NEW_TOKENS = 512
MAX_SEQ_LENGTH = 2048

# Prompt template
ALPACA_PROMPT = """Abaixo está uma instrução que descreve uma tarefa, junto com uma entrada que fornece contexto adicional. Escreva uma resposta que complete adequadamente a solicitação.

### Instrução:
{}

### Entrada:
{}

### Resposta:
{}"""

INSTRUCTION = "Responda a seguinte pergunta médica de forma clara e detalhada."


# ============================================================================
# FUNÇÕES DE MODELO
# ============================================================================

def detect_device() -> str:
    """Detecta o melhor dispositivo disponível."""
    if torch.cuda.is_available():
        return "cuda"
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"
    else:
        return "cpu"


def load_finetuned_model(model_path: str, device: str):
    """
    Carrega o modelo fine-tuned (base + adapters LoRA).

    Args:
        model_path: Caminho para os adapters LoRA salvos
        device: Dispositivo

    Returns:
        Tupla (model, tokenizer)
    """
    print(f"Carregando modelo fine-tuned de: {model_path}")
    print(f"Dispositivo: {device}")
    print("(isso pode demorar alguns minutos...)")
    print()

    # Configuração de quantização 4-bit
    if device == "cuda":
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
        )

        # Carregar modelo base
        base_model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL_NAME,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True,
        )
    else:
        base_model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL_NAME,
            torch_dtype=torch.float16 if device == "mps" else torch.float32,
            device_map="auto",
            trust_remote_code=True,
        )

    # Aplicar adapters LoRA
    model = PeftModel.from_pretrained(base_model, model_path)
    model.eval()

    # Carregar tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print("✓ Modelo fine-tuned carregado com sucesso!")
    return model, tokenizer


def generate_response(
    model,
    tokenizer,
    question: str,
    device: str,
    max_new_tokens: int = MAX_NEW_TOKENS
) -> str:
    """Gera resposta para uma pergunta médica."""
    prompt = ALPACA_PROMPT.format(INSTRUCTION, question, "")

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=MAX_SEQ_LENGTH - max_new_tokens,
    )

    if device == "cuda":
        inputs = {k: v.to("cuda") for k, v in inputs.items()}
    elif device == "mps":
        inputs = {k: v.to("mps") for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    if "### Resposta:" in response:
        response = response.split("### Resposta:")[-1].strip()

    return response


# ============================================================================
# FUNÇÕES DE MÉTRICAS
# ============================================================================

def calculate_metrics(
    baseline_responses: list,
    finetuned_responses: list,
    reference_answers: list | None = None,
) -> dict:
    """
    Calcula métricas comparativas entre baseline e fine-tuned.

    Args:
        baseline_responses: Respostas do modelo base
        finetuned_responses: Respostas do modelo fine-tuned
        reference_answers: Respostas de referência (ground truth), opcional

    Returns:
        Dict com métricas agregadas
    """
    try:
        from rouge_score import rouge_scorer
        import nltk
        from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
        nltk.download('punkt', quiet=True)
        nltk.download('punkt_tab', quiet=True)
    except ImportError:
        print("⚠ Bibliotecas de métricas não encontradas. Pulando métricas...")
        return None

    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    smoothing = SmoothingFunction().method1

    metrics = {
        "baseline": {
            "avg_length": 0,
            "total_length": 0,
        },
        "finetuned": {
            "avg_length": 0,
            "total_length": 0,
        },
        "comparison": {},
        "averages": {}
    }

    # Listas temporárias para médias
    bleu_scores = []
    rouge1_scores = []
    rouge2_scores = []
    rougeL_scores = []
    length_ratios = []

    # Métricas vs referência (quando disponível)
    has_reference = reference_answers is not None and len(reference_answers) > 0
    ref_bleu_base = []
    ref_bleu_ft = []
    ref_rouge1_base = []
    ref_rouge1_ft = []
    ref_rouge2_base = []
    ref_rouge2_ft = []
    ref_rougeL_base = []
    ref_rougeL_ft = []
    semantic_sim_base = []
    semantic_sim_ft = []

    # Carregar modelo de embeddings para similaridade semântica (se há referência)
    embed_model = None
    if has_reference:
        try:
            from sentence_transformers import SentenceTransformer
            print("      Carregando modelo de embeddings para similaridade semântica...")
            embed_model = SentenceTransformer('intfloat/multilingual-e5-base')
            print("      ✓ Modelo de embeddings carregado")
        except ImportError:
            print("      ⚠ sentence-transformers não encontrado. Pulando similaridade semântica.")

    for i, (baseline, finetuned) in enumerate(zip(baseline_responses, finetuned_responses)):
        base_resp = baseline.get('resposta', '')
        ft_resp = finetuned.get('resposta', '')

        # Comprimento
        base_len = len(base_resp)
        ft_len = len(ft_resp)
        metrics["baseline"]["total_length"] += base_len
        metrics["finetuned"]["total_length"] += ft_len

        if base_len > 0:
            length_ratios.append(ft_len / base_len)

        # BLEU e ROUGE: fine-tuned vs baseline
        try:
            base_tokens = nltk.word_tokenize(base_resp.lower())
            ft_tokens = nltk.word_tokenize(ft_resp.lower())
            if base_tokens and ft_tokens:
                bleu = sentence_bleu([base_tokens], ft_tokens, smoothing_function=smoothing)
                bleu_scores.append(bleu)
        except Exception:
            pass

        try:
            rouge_result = scorer.score(base_resp, ft_resp)
            rouge1_scores.append(rouge_result['rouge1'].fmeasure)
            rouge2_scores.append(rouge_result['rouge2'].fmeasure)
            rougeL_scores.append(rouge_result['rougeL'].fmeasure)
        except Exception:
            pass

        # Métricas vs referência
        if has_reference and i < len(reference_answers):
            ref_text = reference_answers[i]
            if ref_text:
                try:
                    ref_tokens = nltk.word_tokenize(ref_text.lower())
                    if ref_tokens:
                        if base_tokens:
                            ref_bleu_base.append(
                                sentence_bleu([ref_tokens], base_tokens, smoothing_function=smoothing)
                            )
                        if ft_tokens:
                            ref_bleu_ft.append(
                                sentence_bleu([ref_tokens], ft_tokens, smoothing_function=smoothing)
                            )
                except Exception:
                    pass

                try:
                    r_base = scorer.score(ref_text, base_resp)
                    ref_rouge1_base.append(r_base['rouge1'].fmeasure)
                    ref_rouge2_base.append(r_base['rouge2'].fmeasure)
                    ref_rougeL_base.append(r_base['rougeL'].fmeasure)

                    r_ft = scorer.score(ref_text, ft_resp)
                    ref_rouge1_ft.append(r_ft['rouge1'].fmeasure)
                    ref_rouge2_ft.append(r_ft['rouge2'].fmeasure)
                    ref_rougeL_ft.append(r_ft['rougeL'].fmeasure)
                except Exception:
                    pass

                if embed_model is not None:
                    try:
                        import numpy as np
                        # E5 model: usar prefixo "passage: " para textos
                        embs = embed_model.encode([
                            "passage: " + ref_text[:2000],
                            "passage: " + base_resp[:2000],
                            "passage: " + ft_resp[:2000],
                        ])
                        # Cosine similarity
                        def cosine_sim(a, b):
                            return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
                        semantic_sim_base.append(cosine_sim(embs[0], embs[1]))
                        semantic_sim_ft.append(cosine_sim(embs[0], embs[2]))
                    except Exception:
                        pass

    # Calcular médias
    n = len(baseline_responses)
    metrics["baseline"]["avg_length"] = metrics["baseline"]["total_length"] / n if n > 0 else 0
    metrics["finetuned"]["avg_length"] = metrics["finetuned"]["total_length"] / n if n > 0 else 0

    def safe_avg(lst):
        return sum(lst) / len(lst) if lst else 0

    metrics["averages"] = {
        "bleu": safe_avg(bleu_scores),
        "rouge1": safe_avg(rouge1_scores),
        "rouge2": safe_avg(rouge2_scores),
        "rougeL": safe_avg(rougeL_scores),
        "length_ratio": safe_avg(length_ratios),
    }

    # Adicionar métricas vs referência
    if has_reference:
        metrics["reference"] = {
            "baseline": {
                "bleu": safe_avg(ref_bleu_base),
                "rouge1": safe_avg(ref_rouge1_base),
                "rouge2": safe_avg(ref_rouge2_base),
                "rougeL": safe_avg(ref_rougeL_base),
            },
            "finetuned": {
                "bleu": safe_avg(ref_bleu_ft),
                "rouge1": safe_avg(ref_rouge1_ft),
                "rouge2": safe_avg(ref_rouge2_ft),
                "rougeL": safe_avg(ref_rougeL_ft),
            },
        }
        if semantic_sim_base:
            metrics["reference"]["baseline"]["semantic_similarity"] = safe_avg(semantic_sim_base)
            metrics["reference"]["finetuned"]["semantic_similarity"] = safe_avg(semantic_sim_ft)

    return metrics


# ============================================================================
# FUNÇÕES DE RELATÓRIO
# ============================================================================

def generate_markdown_report(
    baseline_responses: list,
    finetuned_responses: list,
    metrics: dict,
    output_path: Path,
    questions_with_ref: list | None = None,
):
    """Gera relatório Markdown comparativo."""

    lines = [
        "# Comparação: Modelo Base vs Fine-Tuned",
        "",
        f"**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Métricas Agregadas",
        "",
    ]

    if metrics:
        lines.extend([
            "### Sobreposição entre modelos (FT vs Baseline)",
            "",
            "| Métrica | Valor |",
            "|---------|-------|",
            f"| Comprimento médio (Base) | {metrics['baseline']['avg_length']:.0f} chars |",
            f"| Comprimento médio (Fine-tuned) | {metrics['finetuned']['avg_length']:.0f} chars |",
            f"| Ratio de comprimento (FT/Base) | {metrics['averages']['length_ratio']:.2f}x |",
            f"| BLEU Score | {metrics['averages']['bleu']:.4f} |",
            f"| ROUGE-1 F1 | {metrics['averages']['rouge1']:.4f} |",
            f"| ROUGE-2 F1 | {metrics['averages']['rouge2']:.4f} |",
            f"| ROUGE-L F1 | {metrics['averages']['rougeL']:.4f} |",
            "",
        ])

        # Métricas vs referência (se disponíveis)
        if "reference" in metrics:
            ref = metrics["reference"]
            lines.extend([
                "### Qualidade vs Referência (Ground Truth)",
                "",
                "| Métrica | Baseline | Fine-Tuned |",
                "|---------|----------|------------|",
                f"| BLEU | {ref['baseline']['bleu']:.4f} | {ref['finetuned']['bleu']:.4f} |",
                f"| ROUGE-1 F1 | {ref['baseline']['rouge1']:.4f} | {ref['finetuned']['rouge1']:.4f} |",
                f"| ROUGE-2 F1 | {ref['baseline']['rouge2']:.4f} | {ref['finetuned']['rouge2']:.4f} |",
                f"| ROUGE-L F1 | {ref['baseline']['rougeL']:.4f} | {ref['finetuned']['rougeL']:.4f} |",
            ])
            if "semantic_similarity" in ref.get("baseline", {}):
                lines.append(
                    f"| Similaridade Semântica | {ref['baseline']['semantic_similarity']:.4f} | {ref['finetuned']['semantic_similarity']:.4f} |"
                )
            lines.append("")
    else:
        lines.extend([
            "*Métricas não calculadas (instale rouge-score e nltk)*",
            "",
        ])

    lines.extend([
        "## Comparação por Categoria",
        "",
    ])

    # Agrupar por categoria
    categorias = {}
    for b, f in zip(baseline_responses, finetuned_responses):
        cat = b['categoria']
        if cat not in categorias:
            categorias[cat] = []
        categorias[cat].append((b, f))

    for cat, items in categorias.items():
        lines.extend([
            f"### {cat.title()}",
            "",
        ])

        for baseline, finetuned in items[:2]:  # Apenas 2 exemplos por categoria
            lines.extend([
                f"**Pergunta {baseline['id']}:** {baseline['pergunta']}",
                "",
                "<details>",
                "<summary>Ver respostas</summary>",
                "",
                "**Resposta do Modelo Base:**",
                "```",
                baseline['resposta'][:500] + ("..." if len(baseline['resposta']) > 500 else ""),
                "```",
                "",
                "**Resposta do Modelo Fine-Tuned:**",
                "```",
                finetuned['resposta'][:500] + ("..." if len(finetuned['resposta']) > 500 else ""),
                "```",
                "",
                "</details>",
                "",
            ])

    # Escrever arquivo
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"✓ Relatório Markdown salvo: {output_path}")


# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def load_json(filepath: Path) -> dict:
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data: dict, filepath: Path):
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Avalia o modelo fine-tuned e compara com baseline"
    )
    parser.add_argument(
        '--model-path',
        type=str,
        default=None,
        help='Caminho para o modelo fine-tuned'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Limita a N perguntas'
    )
    parser.add_argument(
        '--skip-metrics',
        action='store_true',
        help='Pula cálculo de métricas'
    )
    parser.add_argument(
        '--device',
        type=str,
        default=None,
        choices=['cuda', 'mps', 'cpu'],
        help='Dispositivo para execução'
    )
    parser.add_argument(
        '--tag',
        type=str,
        default=None,
        help='Sufixo para arquivos de saída (ex: epoch2, epoch2_val)'
    )
    parser.add_argument(
        '--questions-file',
        type=str,
        default=None,
        help='Arquivo de perguntas alternativo'
    )
    parser.add_argument(
        '--baseline-file',
        type=str,
        default=None,
        help='Arquivo de baseline alternativo'
    )

    args = parser.parse_args()

    # Resolver caminhos com base no tag
    questions_file = Path(args.questions_file) if args.questions_file else DEFAULT_QUESTIONS_FILE
    baseline_file = Path(args.baseline_file) if args.baseline_file else DEFAULT_BASELINE_FILE
    if args.tag:
        finetuned_file = EVALUATION_DIR / f"finetuned_responses_{args.tag}.json"
        comparison_json = EVALUATION_DIR / f"comparacao_resultados_{args.tag}.json"
        comparison_md = EVALUATION_DIR / f"comparacao_resultados_{args.tag}.md"
    else:
        finetuned_file = DEFAULT_FINETUNED_FILE
        comparison_json = DEFAULT_COMPARISON_JSON
        comparison_md = DEFAULT_COMPARISON_MD

    print("=" * 60)
    print("  AVALIAÇÃO DO MODELO FINE-TUNED")
    print("  Tech Challenge Fase 3 - FIAP")
    print("=" * 60)
    print()

    # Configurações
    device = args.device or detect_device()
    model_path = args.model_path or str(DEFAULT_FINETUNED_PATH)

    print(f"Dispositivo: {device}")
    print(f"Modelo: {model_path}")
    print()

    print(f"Perguntas: {questions_file}")
    print(f"Baseline: {baseline_file}")
    if args.tag:
        print(f"Tag: {args.tag}")
    print(f"Saída FT: {finetuned_file}")
    print()

    # Verificar arquivos necessários
    if not questions_file.exists():
        print(f"✗ ERRO: Arquivo de perguntas não encontrado: {questions_file}")
        sys.exit(1)

    if not baseline_file.exists():
        print(f"✗ ERRO: Arquivo de baseline não encontrado: {baseline_file}")
        print("  Execute primeiro: python scripts/05_avaliar_baseline.py")
        sys.exit(1)

    if not Path(model_path).exists():
        print(f"✗ ERRO: Modelo fine-tuned não encontrado: {model_path}")
        print("  Execute primeiro o notebook de fine-tuning")
        sys.exit(1)

    # Carregar perguntas e baseline
    print("[1/5] Carregando dados...")
    questions_data = load_json(questions_file)
    questions = questions_data['perguntas']
    baseline_data = load_json(baseline_file)
    baseline_responses = baseline_data['respostas']

    # Verificar se há respostas de referência (ground truth)
    reference_answers = None
    if questions and 'resposta_referencia' in questions[0]:
        reference_answers = [q.get('resposta_referencia', '') for q in questions]
        print(f"      ✓ Respostas de referência encontradas ({len(reference_answers)})")

    if args.limit:
        questions = questions[:args.limit]
        baseline_responses = baseline_responses[:args.limit]
        print(f"      Limitado a {args.limit} perguntas")

    print(f"      ✓ {len(questions)} perguntas carregadas")
    print(f"      ✓ {len(baseline_responses)} respostas baseline carregadas")
    print()

    # Carregar modelo fine-tuned
    print("[2/5] Carregando modelo fine-tuned...")
    model, tokenizer = load_finetuned_model(model_path, device)
    print()

    # Gerar respostas
    print("[3/5] Gerando respostas com modelo fine-tuned...")
    print()

    finetuned_results = {
        "metadata": {
            "modelo_base": BASE_MODEL_NAME,
            "modelo_finetuned": model_path,
            "tipo": "finetuned",
            "timestamp": datetime.now().isoformat(),
            "total_perguntas": len(questions),
            "device": device,
        },
        "respostas": []
    }

    for q in tqdm(questions, desc="Avaliando"):
        response = generate_response(model, tokenizer, q['pergunta'], device)

        finetuned_results['respostas'].append({
            "id": q['id'],
            "categoria": q['categoria'],
            "pergunta": q['pergunta'],
            "resposta": response,
        })

    print()

    # Salvar respostas fine-tuned
    print("[4/5] Salvando resultados...")
    save_json(finetuned_results, finetuned_file)
    print(f"      ✓ Respostas fine-tuned: {finetuned_file}")

    # Calcular métricas e comparação
    print()
    print("[5/5] Gerando comparação...")

    finetuned_responses = finetuned_results['respostas']

    if not args.skip_metrics:
        metrics = calculate_metrics(
            baseline_responses,
            finetuned_responses,
            reference_answers=reference_answers,
        )
    else:
        metrics = None
        print("      (métricas puladas)")

    # Salvar comparação JSON
    comparison = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "baseline_file": str(baseline_file),
            "finetuned_file": str(finetuned_file),
            "questions_file": str(questions_file),
            "total_perguntas": len(questions),
            "has_reference": reference_answers is not None,
        },
        "metrics": metrics,
    }
    save_json(comparison, comparison_json)
    print(f"      ✓ Comparação JSON: {comparison_json}")

    # Gerar relatório Markdown
    generate_markdown_report(
        baseline_responses,
        finetuned_responses,
        metrics,
        comparison_md,
        questions_with_ref=questions if reference_answers else None,
    )

    print()
    print("=" * 60)
    print("  AVALIAÇÃO CONCLUÍDA!")
    print("=" * 60)
    print()

    if metrics:
        print("  Resumo das Métricas (FT vs Baseline):")
        print(f"    Comprimento médio (Base):      {metrics['baseline']['avg_length']:.0f} chars")
        print(f"    Comprimento médio (Fine-tuned): {metrics['finetuned']['avg_length']:.0f} chars")
        print(f"    BLEU Score:  {metrics['averages']['bleu']:.4f}")
        print(f"    ROUGE-L F1:  {metrics['averages']['rougeL']:.4f}")
        if "reference" in metrics:
            ref = metrics["reference"]
            print()
            print("  Resumo das Métricas (vs Referência):")
            print(f"    BLEU (Base vs Ref):       {ref['baseline']['bleu']:.4f}")
            print(f"    BLEU (FT vs Ref):         {ref['finetuned']['bleu']:.4f}")
            print(f"    ROUGE-L (Base vs Ref):    {ref['baseline']['rougeL']:.4f}")
            print(f"    ROUGE-L (FT vs Ref):      {ref['finetuned']['rougeL']:.4f}")
            if "semantic_similarity" in ref.get("baseline", {}):
                print(f"    Sim. Semântica (Base):    {ref['baseline']['semantic_similarity']:.4f}")
                print(f"    Sim. Semântica (FT):      {ref['finetuned']['semantic_similarity']:.4f}")
        print()

    print("  Arquivos gerados:")
    print(f"    - {finetuned_file}")
    print(f"    - {comparison_json}")
    print(f"    - {comparison_md}")
    print()


if __name__ == "__main__":
    main()
