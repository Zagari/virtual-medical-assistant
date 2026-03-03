#!/usr/bin/env python3
"""
03_preparar_dataset.py - Preparação do Dataset MedQuAD para Fine-Tuning

Este script:
1. Baixa o dataset MedQuAD do HuggingFace (lavita/MedQuAD - 47.4k pares QA)
2. Filtra registros sem resposta (~65% do dataset tem answer=None devido a copyright)
3. Traduz perguntas e respostas de inglês para português (deep-translator)
4. Formata no padrão Alpaca (instruction/input/output) para fine-tuning
5. Salva checkpoints a cada 1000 registros para poder resumir

Nota: O dataset MedQuAD original tem ~47k registros, mas apenas ~16k possuem
respostas completas. Os demais foram removidos por questões de copyright.

Saída: data/processed/training_data.jsonl

Uso:
    python scripts/03_preparar_dataset.py [--test] [--limit N]

Flags:
    --test      Modo teste: traduz apenas 10 registros
    --limit N   Limita a N registros (para testes parciais)
    --resume    Resume do último checkpoint (padrão: True)
    --no-resume Ignora checkpoint e começa do zero

Requisitos:
    pip install datasets deep-translator tqdm
"""

import json
import os
import sys
import time
import argparse
from datetime import datetime
from pathlib import Path

try:
    from datasets import load_dataset
    from deep_translator import GoogleTranslator
    from tqdm import tqdm
except ImportError as e:
    print(f"Erro: Dependência não encontrada: {e}")
    print("Instale com: pip install datasets deep-translator tqdm")
    sys.exit(1)


# ============================================================================
# CONFIGURAÇÕES
# ============================================================================

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
CHECKPOINT_FILE = PROCESSED_DIR / "translation_checkpoint.json"
OUTPUT_FILE = PROCESSED_DIR / "training_data.jsonl"

# Dataset
DATASET_NAME = "lavita/MedQuAD"
DATASET_SPLIT = "train"

# Tradução
CHECKPOINT_INTERVAL = 1000  # Salvar checkpoint a cada N registros
SLEEP_BETWEEN_REQUESTS = 0.3  # Segundos entre requisições (evita rate limit)
MAX_RETRIES = 3  # Tentativas em caso de erro
MAX_TEXT_LENGTH = 4500  # Limite do Google Translate via deep-translator

# Formato Alpaca
INSTRUCTION_PT = "Responda a seguinte pergunta médica de forma clara e detalhada."


# ============================================================================
# FUNÇÕES DE TRADUÇÃO
# ============================================================================

def create_translator():
    """Cria instância do tradutor."""
    return GoogleTranslator(source='en', target='pt')


def translate_text(text: str, translator: GoogleTranslator, retries: int = MAX_RETRIES) -> str:
    """
    Traduz texto de inglês para português.

    Args:
        text: Texto em inglês
        translator: Instância do GoogleTranslator
        retries: Número de tentativas em caso de erro

    Returns:
        Texto traduzido para português
    """
    # Handle None or empty text
    if text is None:
        return ""
    if len(text.strip()) == 0:
        return ""

    text = text.strip()

    # Textos longos precisam ser divididos
    if len(text) > MAX_TEXT_LENGTH:
        chunks = []
        current_chunk = ""

        # Dividir por sentenças para não cortar no meio
        sentences = text.replace(". ", ".|").split("|")

        for sentence in sentences:
            if len(current_chunk) + len(sentence) < MAX_TEXT_LENGTH:
                current_chunk += sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence

        if current_chunk:
            chunks.append(current_chunk)

        # Traduzir cada chunk
        translated_chunks = []
        for chunk in chunks:
            translated = _translate_with_retry(chunk, translator, retries)
            translated_chunks.append(translated)
            time.sleep(SLEEP_BETWEEN_REQUESTS)

        return " ".join(translated_chunks)

    return _translate_with_retry(text, translator, retries)


def _translate_with_retry(text: str, translator: GoogleTranslator, retries: int) -> str:
    """Traduz com retry em caso de erro."""
    for attempt in range(retries):
        try:
            result = translator.translate(text)
            return result if result else text
        except Exception as e:
            if attempt < retries - 1:
                wait_time = (attempt + 1) * 2  # Backoff: 2s, 4s, 6s
                print(f"\n  ⚠ Erro na tradução (tentativa {attempt + 1}/{retries}): {e}")
                print(f"    Aguardando {wait_time}s antes de tentar novamente...")
                time.sleep(wait_time)
            else:
                print(f"\n  ✗ Falha após {retries} tentativas. Mantendo texto original.")
                return text
    return text


# ============================================================================
# FUNÇÕES DE CHECKPOINT
# ============================================================================

def save_checkpoint(translated_data: list, current_index: int, total: int):
    """
    Salva checkpoint da tradução para poder resumir.

    Args:
        translated_data: Lista de registros já traduzidos
        current_index: Índice atual no dataset original
        total: Total de registros no dataset
    """
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    checkpoint = {
        "last_index": current_index,
        "timestamp": datetime.now().isoformat(),
        "total_translated": len(translated_data),
        "total_dataset": total,
        "progress_percent": round(100 * current_index / total, 2),
        "data": translated_data
    }

    with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
        json.dump(checkpoint, f, ensure_ascii=False, indent=2)

    print(f"\n  ✓ Checkpoint salvo: {current_index}/{total} ({checkpoint['progress_percent']}%)")


def load_checkpoint() -> tuple[list, int]:
    """
    Carrega checkpoint anterior se existir.

    Returns:
        Tupla (dados_traduzidos, índice_para_continuar)
    """
    if CHECKPOINT_FILE.exists():
        try:
            with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
                checkpoint = json.load(f)

            print(f"✓ Checkpoint encontrado!")
            print(f"  - Último índice: {checkpoint['last_index']}")
            print(f"  - Registros traduzidos: {checkpoint['total_translated']}")
            print(f"  - Progresso: {checkpoint['progress_percent']}%")
            print(f"  - Data: {checkpoint['timestamp']}")

            return checkpoint['data'], checkpoint['last_index']
        except Exception as e:
            print(f"⚠ Erro ao carregar checkpoint: {e}")
            print("  Iniciando do zero...")
            return [], 0

    return [], 0


def clear_checkpoint():
    """Remove arquivo de checkpoint."""
    if CHECKPOINT_FILE.exists():
        CHECKPOINT_FILE.unlink()
        print("✓ Checkpoint removido")


# ============================================================================
# FUNÇÕES DE FORMATAÇÃO
# ============================================================================

def format_as_alpaca(question: str, answer: str) -> dict:
    """
    Formata par QA no padrão Alpaca para fine-tuning.

    Formato esperado pelo SFTTrainer:
    {
        "instruction": "Instrução fixa",
        "input": "Pergunta",
        "output": "Resposta"
    }
    """
    return {
        "instruction": INSTRUCTION_PT,
        "input": question.strip(),
        "output": answer.strip()
    }


def save_as_jsonl(data: list, filepath: Path):
    """Salva dados no formato JSONL (uma linha JSON por registro)."""
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as f:
        for record in data:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')

    print(f"✓ Dataset salvo: {filepath}")
    print(f"  - Total de registros: {len(data)}")
    print(f"  - Tamanho: {filepath.stat().st_size / (1024*1024):.2f} MB")


# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def prepare_dataset(limit: int = None, resume: bool = True, test_mode: bool = False):
    """
    Pipeline principal de preparação do dataset.

    Args:
        limit: Limitar a N registros (None = todos)
        resume: Se True, continua do último checkpoint
        test_mode: Se True, processa apenas 10 registros
    """
    print("=" * 60)
    print("  PREPARAÇÃO DO DATASET MEDQUAD PARA FINE-TUNING")
    print("  Tech Challenge Fase 3 - FIAP")
    print("=" * 60)
    print()

    # Modo teste
    if test_mode:
        limit = 10
        print("🧪 MODO TESTE: Processando apenas 10 registros")
        print()

    # -------------------------------------------------------------------------
    # 1. Carregar dataset do HuggingFace
    # -------------------------------------------------------------------------
    print(f"[1/4] Carregando dataset: {DATASET_NAME}")
    print("      (isso pode demorar na primeira vez...)")

    try:
        dataset = load_dataset(DATASET_NAME, split=DATASET_SPLIT)
        total_records = len(dataset)
        print(f"      ✓ Dataset carregado: {total_records} registros")
    except Exception as e:
        print(f"      ✗ Erro ao carregar dataset: {e}")
        sys.exit(1)

    # Aplicar limite se especificado
    if limit and limit < total_records:
        print(f"      ℹ Limitando a {limit} registros")
        total_records = limit

    print()

    # -------------------------------------------------------------------------
    # 2. Verificar/carregar checkpoint
    # -------------------------------------------------------------------------
    print("[2/4] Verificando checkpoint anterior...")

    if resume:
        translated_data, start_index = load_checkpoint()
        if start_index > 0:
            print(f"      Continuando a partir do índice {start_index}")
    else:
        translated_data, start_index = [], 0
        clear_checkpoint()
        print("      Iniciando do zero (--no-resume)")

    print()

    # Se já completou, apenas salvar
    if start_index >= total_records:
        print("✓ Tradução já completa! Salvando arquivo final...")
        save_as_jsonl(translated_data[:total_records], OUTPUT_FILE)
        return

    # -------------------------------------------------------------------------
    # 3. Traduzir dataset
    # -------------------------------------------------------------------------
    print(f"[3/4] Traduzindo de inglês para português...")
    print(f"      Registros restantes: {total_records - start_index}")
    print(f"      Checkpoint a cada: {CHECKPOINT_INTERVAL} registros")
    print()

    translator = create_translator()

    # Progress bar
    pbar = tqdm(
        range(start_index, total_records),
        initial=start_index,
        total=total_records,
        desc="Traduzindo",
        unit="reg"
    )

    skipped_count = 0

    try:
        for i in pbar:
            row = dataset[i]

            # Extrair pergunta e resposta
            question = row.get('question', row.get('Question', ''))
            answer = row.get('answer', row.get('Answer', ''))

            # Skip records with None or empty answer (MedQuAD has ~65% without answers due to copyright)
            if answer is None or (isinstance(answer, str) and len(answer.strip()) == 0):
                skipped_count += 1
                pbar.set_postfix({
                    'traduzidos': len(translated_data),
                    'sem_resposta': skipped_count
                })
                continue

            # Skip records with None or empty question
            if question is None or (isinstance(question, str) and len(question.strip()) == 0):
                skipped_count += 1
                continue

            # Traduzir
            translated_question = translate_text(question, translator)
            time.sleep(SLEEP_BETWEEN_REQUESTS)

            translated_answer = translate_text(answer, translator)
            time.sleep(SLEEP_BETWEEN_REQUESTS)

            # Formatar como Alpaca
            formatted = format_as_alpaca(translated_question, translated_answer)
            translated_data.append(formatted)

            # Atualizar progress bar
            pbar.set_postfix({
                'traduzidos': len(translated_data),
                'Q_len': len(translated_question),
                'A_len': len(translated_answer)
            })

            # Salvar checkpoint periodicamente
            if (i + 1) % CHECKPOINT_INTERVAL == 0:
                save_checkpoint(translated_data, i + 1, total_records)

        # Checkpoint final
        save_checkpoint(translated_data, total_records, total_records)

        # Resumo dos registros pulados
        if skipped_count > 0:
            print(f"\n  ℹ Registros sem resposta (pulados): {skipped_count}")
            print(f"    Isso é esperado - MedQuAD tem ~65% de registros sem resposta devido a copyright")

    except KeyboardInterrupt:
        print("\n\n⚠ Interrompido pelo usuário!")
        print(f"  Salvando checkpoint com {len(translated_data)} registros...")
        save_checkpoint(translated_data, len(translated_data), total_records)
        print("  Você pode continuar depois com: python scripts/03_preparar_dataset.py")
        sys.exit(0)

    except Exception as e:
        print(f"\n\n✗ Erro durante tradução: {e}")
        print(f"  Salvando checkpoint com {len(translated_data)} registros...")
        save_checkpoint(translated_data, len(translated_data), total_records)
        raise

    print()

    # -------------------------------------------------------------------------
    # 4. Salvar dataset final
    # -------------------------------------------------------------------------
    print("[4/4] Salvando dataset final...")
    save_as_jsonl(translated_data, OUTPUT_FILE)

    # Limpar checkpoint após sucesso
    clear_checkpoint()

    print()
    print("=" * 60)
    print("  PREPARAÇÃO CONCLUÍDA!")
    print("=" * 60)
    print(f"  Arquivo: {OUTPUT_FILE}")
    print(f"  Registros: {len(translated_data)}")
    print(f"  Formato: Alpaca JSONL (instruction/input/output)")
    print()
    print("  Próximo passo:")
    print("    1. Faça upload de training_data.jsonl para o Google Drive")
    print("    2. Abra notebooks/03_fine_tuning.ipynb no Google Colab")
    print("    3. Execute o fine-tuning")
    print()


# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Prepara dataset MedQuAD para fine-tuning (tradução EN→PT)"
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Modo teste: processa apenas 10 registros'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Limita a N registros (para testes parciais)'
    )
    parser.add_argument(
        '--resume',
        action='store_true',
        default=True,
        help='Resume do último checkpoint (padrão)'
    )
    parser.add_argument(
        '--no-resume',
        action='store_true',
        help='Ignora checkpoint e começa do zero'
    )

    args = parser.parse_args()

    # --no-resume sobrescreve --resume
    resume = not args.no_resume

    prepare_dataset(
        limit=args.limit,
        resume=resume,
        test_mode=args.test
    )


if __name__ == "__main__":
    main()
