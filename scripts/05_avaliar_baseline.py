#!/usr/bin/env python3
"""
05_avaliar_baseline.py - Avaliação do Modelo Base (Mistral 7B)

Este script executa 50 perguntas médicas no modelo Mistral 7B BASE (sem fine-tuning)
para estabelecer uma linha de base de comparação.

Entrada:
    data/evaluation/perguntas_avaliacao.json

Saída:
    data/evaluation/baseline_responses.json

Uso:
    python scripts/05_avaliar_baseline.py [--limit N] [--device DEVICE]
    python scripts/05_avaliar_baseline.py --questions-file data/evaluation/validacao_amostra.json --tag val

Flags:
    --limit N            Limita a N perguntas (para testes rápidos)
    --device             Dispositivo: "cuda", "mps" ou "cpu" (auto-detecta)
    --tag TAG            Sufixo nos arquivos de saída (ex: val)
    --questions-file     Arquivo de perguntas alternativo

Requisitos:
    pip install transformers accelerate bitsandbytes torch

NOTA: Este script requer GPU com pelo menos 8GB de VRAM para rodar
      o modelo em 4-bit quantization.
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
    from tqdm import tqdm
except ImportError as e:
    print(f"Erro: Dependência não encontrada: {e}")
    print("Instale com: pip install transformers accelerate bitsandbytes torch tqdm")
    sys.exit(1)


# ============================================================================
# CONFIGURAÇÕES
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
EVALUATION_DIR = DATA_DIR / "evaluation"

DEFAULT_QUESTIONS_FILE = EVALUATION_DIR / "perguntas_avaliacao.json"
DEFAULT_OUTPUT_FILE = EVALUATION_DIR / "baseline_responses.json"

# Modelo base
MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.3"
MAX_NEW_TOKENS = 512
MAX_SEQ_LENGTH = 2048

# Prompt template (mesmo usado no fine-tuning)
ALPACA_PROMPT = """Abaixo está uma instrução que descreve uma tarefa, junto com uma entrada que fornece contexto adicional. Escreva uma resposta que complete adequadamente a solicitação.

### Instrução:
{}

### Entrada:
{}

### Resposta:
{}"""

INSTRUCTION = "Responda a seguinte pergunta médica de forma clara e detalhada."


# ============================================================================
# FUNÇÕES
# ============================================================================

def detect_device() -> str:
    """Detecta o melhor dispositivo disponível."""
    if torch.cuda.is_available():
        return "cuda"
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"
    else:
        return "cpu"


def load_model_and_tokenizer(device: str):
    """
    Carrega o modelo Mistral 7B base com quantização 4-bit.

    Args:
        device: Dispositivo para carregar o modelo

    Returns:
        Tupla (model, tokenizer)
    """
    print(f"Carregando modelo: {MODEL_NAME}")
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

        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True,
        )
    else:
        # Para MPS ou CPU, carregar em float16 sem quantização
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            torch_dtype=torch.float16 if device == "mps" else torch.float32,
            device_map="auto",
            trust_remote_code=True,
        )

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    tokenizer.pad_token = tokenizer.eos_token

    print("✓ Modelo carregado com sucesso!")
    return model, tokenizer


def generate_response(
    model,
    tokenizer,
    question: str,
    device: str,
    max_new_tokens: int = MAX_NEW_TOKENS
) -> str:
    """
    Gera resposta para uma pergunta médica.

    Args:
        model: Modelo carregado
        tokenizer: Tokenizer
        question: Pergunta em português
        device: Dispositivo
        max_new_tokens: Máximo de tokens na resposta

    Returns:
        Resposta gerada
    """
    # Formatar prompt
    prompt = ALPACA_PROMPT.format(INSTRUCTION, question, "")

    # Tokenizar
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

    # Gerar
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )

    # Decodificar
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Extrair apenas a resposta
    if "### Resposta:" in response:
        response = response.split("### Resposta:")[-1].strip()

    return response


def load_questions(filepath: Path) -> list:
    """Carrega perguntas do arquivo JSON."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['perguntas']


def save_results(results: dict, filepath: Path):
    """Salva resultados em JSON."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"✓ Resultados salvos em: {filepath}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Avalia o modelo Mistral 7B base com perguntas médicas"
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Limita a N perguntas (para testes rápidos)'
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
        help='Sufixo para arquivos de saída (ex: val)'
    )
    parser.add_argument(
        '--questions-file',
        type=str,
        default=None,
        help='Arquivo de perguntas alternativo'
    )

    args = parser.parse_args()

    # Resolver caminhos com base no tag
    questions_file = Path(args.questions_file) if args.questions_file else DEFAULT_QUESTIONS_FILE
    if args.tag:
        output_file = EVALUATION_DIR / f"baseline_responses_{args.tag}.json"
    else:
        output_file = DEFAULT_OUTPUT_FILE

    print("=" * 60)
    print("  AVALIAÇÃO DO MODELO BASE (Mistral 7B)")
    print("  Tech Challenge Fase 3 - FIAP")
    print("=" * 60)
    print()

    # Detectar dispositivo
    device = args.device or detect_device()
    print(f"Dispositivo detectado: {device}")

    if device == "cpu":
        print("⚠ AVISO: Executando em CPU será muito lento!")
        print("  Recomendado: GPU com pelo menos 8GB de VRAM")
        print()

    # Verificar arquivo de perguntas
    if not questions_file.exists():
        print(f"✗ ERRO: Arquivo de perguntas não encontrado!")
        print(f"  Esperado: {questions_file}")
        sys.exit(1)

    # Carregar perguntas
    print()
    print(f"Arquivo de perguntas: {questions_file}")
    if args.tag:
        print(f"Tag: {args.tag}")
    print(f"Saída: {output_file}")
    print()
    print("[1/3] Carregando perguntas...")
    questions = load_questions(questions_file)

    if args.limit:
        questions = questions[:args.limit]
        print(f"      Limitado a {args.limit} perguntas")

    print(f"      ✓ {len(questions)} perguntas carregadas")
    print()

    # Carregar modelo
    print("[2/3] Carregando modelo...")
    model, tokenizer = load_model_and_tokenizer(device)
    print()

    # Gerar respostas
    print("[3/3] Gerando respostas...")
    print()

    results = {
        "metadata": {
            "modelo": MODEL_NAME,
            "tipo": "baseline",
            "timestamp": datetime.now().isoformat(),
            "total_perguntas": len(questions),
            "device": device,
            "max_new_tokens": MAX_NEW_TOKENS,
        },
        "respostas": []
    }

    for q in tqdm(questions, desc="Avaliando"):
        response = generate_response(model, tokenizer, q['pergunta'], device)

        results['respostas'].append({
            "id": q['id'],
            "categoria": q['categoria'],
            "pergunta": q['pergunta'],
            "resposta": response,
        })

    print()

    # Salvar resultados
    save_results(results, output_file)

    print()
    print("=" * 60)
    print("  AVALIAÇÃO CONCLUÍDA!")
    print("=" * 60)
    print(f"  Modelo: {MODEL_NAME}")
    print(f"  Perguntas: {len(questions)}")
    print(f"  Arquivo: {output_file}")
    print()
    print("  Próximo passo:")
    print("    Execute o fine-tuning e depois:")
    print("    python scripts/06_avaliar_finetuned.py")
    print()


if __name__ == "__main__":
    main()
