#!/usr/bin/env python3
"""
03_preparar_dataset_v2.py - Preparação do Dataset para Fine-Tuning (v2)

Melhorias sobre a v1:
1. Pula tradução se medquad_pt.jsonl já existir (commitável no repo)
2. Compõe dataset híbrido: 80% português + 20% inglês original
3. Inclui QA pairs de medicina brasileira (doenças endêmicas, SUS, etc.)

Este script:
1. Baixa o dataset MedQuAD do HuggingFace (lavita/MedQuAD - 47.4k pares QA)
2. Filtra registros sem resposta (~65% do dataset tem answer=None)
3. Traduz perguntas e respostas para português (se não existir cache)
4. Adiciona 20% de dados originais em inglês (preserva qualidade médica)
5. Adiciona QA brasileiro (dengue, malária, SUS, etc.)
6. Formata no padrão Alpaca e salva dataset final

Saídas:
- data/processed/medquad_pt.jsonl         # MedQuAD traduzido (cache)
- data/processed/medquad_en_sample.jsonl  # Amostra em inglês
- data/processed/brazilian_medical_qa.jsonl # QA brasileiro
- data/processed/training_data.jsonl      # Dataset final composto

Uso:
    python scripts/03_preparar_dataset_v2.py [--flags]

Flags:
    --test              Modo teste: 10 registros apenas
    --limit N           Limitar tradução a N registros
    --resume            Continuar do checkpoint (padrão)
    --no-resume         Ignorar checkpoint, começar do zero
    --force-translate   Forçar re-tradução mesmo se cache existir
    --en-ratio 0.20     Proporção de dados em inglês (padrão: 0.20)
    --skip-brazilian    Não incluir QA brasileiro
    --only-translate    Apenas traduzir, não compor dataset final

Requisitos:
    pip install datasets deep-translator tqdm
"""

import json
import os
import sys
import time
import random
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional

try:
    from datasets import load_dataset
    from deep_translator import GoogleTranslator
    from tqdm import tqdm
except ImportError as e:
    print(f"Erro: Dependência não encontrada: {e}")
    print("Instale com: pip install datasets deep-translator tqdm")
    sys.exit(1)

# Importar gerador de QA brasileiro
sys.path.insert(0, str(Path(__file__).parent.parent))
try:
    from src.data.brazilian_medical_qa import get_qa_without_metadata, get_statistics
    BRAZILIAN_QA_AVAILABLE = True
except ImportError:
    BRAZILIAN_QA_AVAILABLE = False
    print("⚠ Módulo brazilian_medical_qa não encontrado. QA brasileiro será ignorado.")


# ============================================================================
# CONFIGURAÇÕES
# ============================================================================

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"

# Arquivos de saída
TRANSLATED_FILE = PROCESSED_DIR / "medquad_pt.jsonl"      # Cache da tradução
EN_SAMPLE_FILE = PROCESSED_DIR / "medquad_en_sample.jsonl"  # Amostra inglês
BRAZILIAN_QA_FILE = PROCESSED_DIR / "brazilian_medical_qa.jsonl"  # QA brasileiro
OUTPUT_FILE = PROCESSED_DIR / "training_data.jsonl"        # Dataset final
CHECKPOINT_FILE = PROCESSED_DIR / "translation_checkpoint.json"

# Dataset
DATASET_NAME = "lavita/MedQuAD"
DATASET_SPLIT = "train"

# Tradução
CHECKPOINT_INTERVAL = 1000
SLEEP_BETWEEN_REQUESTS = 0.3
MAX_RETRIES = 3
MAX_TEXT_LENGTH = 4500

# Composição do dataset
DEFAULT_EN_RATIO = 0.20  # 20% inglês original
RANDOM_SEED = 42

# Formato Alpaca
INSTRUCTION_PT = "Responda a seguinte pergunta médica de forma clara e detalhada."
INSTRUCTION_EN = "Answer the following medical question clearly and in detail."


# ============================================================================
# FUNÇÕES DE TRADUÇÃO
# ============================================================================

def create_translator():
    """Cria instância do tradutor."""
    return GoogleTranslator(source='en', target='pt')


def translate_text(text: str, translator: GoogleTranslator, retries: int = MAX_RETRIES) -> str:
    """Traduz texto de inglês para português."""
    if text is None:
        return ""
    if len(text.strip()) == 0:
        return ""

    text = text.strip()

    if len(text) > MAX_TEXT_LENGTH:
        chunks = []
        current_chunk = ""
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
                wait_time = (attempt + 1) * 2
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
    """Salva checkpoint da tradução para poder resumir."""
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


def load_checkpoint() -> Tuple[List, int]:
    """Carrega checkpoint anterior se existir."""
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
# FUNÇÕES DE ARQUIVO
# ============================================================================

def load_jsonl(filepath: Path) -> List[Dict]:
    """Carrega arquivo JSONL."""
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data


def save_jsonl(data: List[Dict], filepath: Path):
    """Salva dados no formato JSONL."""
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as f:
        for record in data:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')

    print(f"✓ Arquivo salvo: {filepath}")
    print(f"  - Total de registros: {len(data)}")
    print(f"  - Tamanho: {filepath.stat().st_size / (1024*1024):.2f} MB")


def format_as_alpaca_pt(question: str, answer: str) -> Dict:
    """Formata par QA no padrão Alpaca (português)."""
    return {
        "instruction": INSTRUCTION_PT,
        "input": question.strip(),
        "output": answer.strip()
    }


def format_as_alpaca_en(question: str, answer: str) -> Dict:
    """Formata par QA no padrão Alpaca (inglês)."""
    return {
        "instruction": INSTRUCTION_EN,
        "input": question.strip(),
        "output": answer.strip()
    }


# ============================================================================
# ETAPA 1: TRADUÇÃO
# ============================================================================

def translate_medquad(
    limit: Optional[int] = None,
    resume: bool = True,
    force: bool = False
) -> List[Dict]:
    """
    Traduz MedQuAD de inglês para português.

    Se já existir cache (medquad_pt.jsonl), retorna do cache.

    Args:
        limit: Limitar a N registros
        resume: Se True, continua do checkpoint
        force: Se True, força re-tradução mesmo com cache

    Returns:
        Lista de QA traduzidos no formato Alpaca
    """
    # Verificar cache
    if TRANSLATED_FILE.exists() and not force:
        print(f"✓ Cache de tradução encontrado: {TRANSLATED_FILE}")
        print("  Carregando dados traduzidos (use --force-translate para re-traduzir)")
        return load_jsonl(TRANSLATED_FILE)

    print(f"[TRADUÇÃO] Carregando dataset: {DATASET_NAME}")

    try:
        dataset = load_dataset(DATASET_NAME, split=DATASET_SPLIT)
        total_records = len(dataset)
        print(f"  ✓ Dataset carregado: {total_records} registros")
    except Exception as e:
        print(f"  ✗ Erro ao carregar dataset: {e}")
        sys.exit(1)

    if limit and limit < total_records:
        print(f"  ℹ Limitando a {limit} registros")
        total_records = limit

    # Verificar/carregar checkpoint
    if resume:
        translated_data, start_index = load_checkpoint()
        if start_index > 0:
            print(f"  Continuando a partir do índice {start_index}")
    else:
        translated_data, start_index = [], 0
        clear_checkpoint()

    # Se já completou
    if start_index >= total_records:
        print("✓ Tradução já completa!")
        save_jsonl(translated_data[:total_records], TRANSLATED_FILE)
        clear_checkpoint()
        return translated_data[:total_records]

    # Traduzir
    print(f"[TRADUÇÃO] Traduzindo de inglês para português...")
    print(f"  Registros restantes: {total_records - start_index}")

    translator = create_translator()
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

            question = row.get('question', row.get('Question', ''))
            answer = row.get('answer', row.get('Answer', ''))

            # Skip registros sem resposta
            if answer is None or (isinstance(answer, str) and len(answer.strip()) == 0):
                skipped_count += 1
                pbar.set_postfix({'traduzidos': len(translated_data), 'sem_resposta': skipped_count})
                continue

            if question is None or (isinstance(question, str) and len(question.strip()) == 0):
                skipped_count += 1
                continue

            # Traduzir
            translated_question = translate_text(question, translator)
            time.sleep(SLEEP_BETWEEN_REQUESTS)

            translated_answer = translate_text(answer, translator)
            time.sleep(SLEEP_BETWEEN_REQUESTS)

            formatted = format_as_alpaca_pt(translated_question, translated_answer)
            translated_data.append(formatted)

            pbar.set_postfix({
                'traduzidos': len(translated_data),
                'Q_len': len(translated_question),
                'A_len': len(translated_answer)
            })

            if (i + 1) % CHECKPOINT_INTERVAL == 0:
                save_checkpoint(translated_data, i + 1, total_records)

        # Checkpoint final
        save_checkpoint(translated_data, total_records, total_records)

        if skipped_count > 0:
            print(f"\n  ℹ Registros sem resposta (pulados): {skipped_count}")

    except KeyboardInterrupt:
        print("\n\n⚠ Interrompido pelo usuário!")
        save_checkpoint(translated_data, len(translated_data), total_records)
        sys.exit(0)

    except Exception as e:
        print(f"\n\n✗ Erro durante tradução: {e}")
        save_checkpoint(translated_data, len(translated_data), total_records)
        raise

    # Salvar cache da tradução
    print("\n[TRADUÇÃO] Salvando cache...")
    save_jsonl(translated_data, TRANSLATED_FILE)
    clear_checkpoint()

    return translated_data


# ============================================================================
# ETAPA 2: AMOSTRA EM INGLÊS
# ============================================================================

def get_english_sample(
    pt_data: List[Dict],
    en_ratio: float = DEFAULT_EN_RATIO,
    seed: int = RANDOM_SEED
) -> List[Dict]:
    """
    Seleciona amostra do MedQuAD original em inglês.

    Args:
        pt_data: Dados traduzidos (para calcular proporção)
        en_ratio: Proporção de dados em inglês (0.20 = 20%)
        seed: Seed para reprodutibilidade

    Returns:
        Lista de QA em inglês no formato Alpaca
    """
    # Verificar cache
    if EN_SAMPLE_FILE.exists():
        print(f"✓ Amostra inglês encontrada: {EN_SAMPLE_FILE}")
        return load_jsonl(EN_SAMPLE_FILE)

    print(f"[INGLÊS] Selecionando {en_ratio:.0%} de dados em inglês...")

    random.seed(seed)

    # Calcular quantos registros EN adicionar
    n_pt = len(pt_data)
    n_en = int(n_pt * en_ratio / (1 - en_ratio))

    print(f"  - Registros PT: {n_pt}")
    print(f"  - Registros EN a adicionar: {n_en}")

    # Carregar MedQuAD original
    dataset = load_dataset(DATASET_NAME, split=DATASET_SPLIT)

    # Filtrar índices com resposta válida
    valid_indices = [
        i for i, row in enumerate(dataset)
        if row.get('answer') is not None and len(str(row.get('answer', '')).strip()) > 0
    ]

    print(f"  - Índices válidos disponíveis: {len(valid_indices)}")

    # Amostrar
    n_en = min(n_en, len(valid_indices))
    en_indices = random.sample(valid_indices, n_en)

    # Formatar
    en_data = []
    for i in tqdm(en_indices, desc="Preparando EN", unit="reg"):
        row = dataset[i]
        en_data.append(format_as_alpaca_en(
            row['question'],
            row['answer']
        ))

    # Salvar cache
    save_jsonl(en_data, EN_SAMPLE_FILE)

    return en_data


# ============================================================================
# ETAPA 3: QA BRASILEIRO
# ============================================================================

def get_brazilian_qa() -> List[Dict]:
    """
    Carrega QA pairs de medicina brasileira.

    Returns:
        Lista de QA brasileiro no formato Alpaca
    """
    # Verificar cache
    if BRAZILIAN_QA_FILE.exists():
        print(f"✓ QA brasileiro encontrado: {BRAZILIAN_QA_FILE}")
        return load_jsonl(BRAZILIAN_QA_FILE)

    if not BRAZILIAN_QA_AVAILABLE:
        print("⚠ Módulo brazilian_medical_qa não disponível. Pulando...")
        return []

    print("[BRASILEIRO] Gerando QA de medicina brasileira...")

    # Estatísticas
    stats = get_statistics()
    for cat, count in stats.items():
        if cat != "Total":
            print(f"  - {cat}: {count} QA pairs")
    print(f"  TOTAL: {stats['Total']} QA pairs")

    # Gerar
    brazilian_qa = get_qa_without_metadata()

    # Salvar cache
    save_jsonl(brazilian_qa, BRAZILIAN_QA_FILE)

    return brazilian_qa


# ============================================================================
# ETAPA 4: COMPOSIÇÃO FINAL
# ============================================================================

def compose_final_dataset(
    pt_data: List[Dict],
    en_data: List[Dict],
    brazilian_qa: List[Dict],
    seed: int = RANDOM_SEED
) -> List[Dict]:
    """
    Compõe dataset final combinando todas as fontes.

    Args:
        pt_data: MedQuAD traduzido para português
        en_data: Amostra do MedQuAD original em inglês
        brazilian_qa: QA de medicina brasileira
        seed: Seed para embaralhamento

    Returns:
        Dataset final combinado e embaralhado
    """
    print("[COMPOSIÇÃO] Combinando datasets...")

    random.seed(seed)

    combined = pt_data + en_data + brazilian_qa

    print(f"  - Português (MedQuAD traduzido): {len(pt_data)}")
    print(f"  - Inglês (MedQuAD original): {len(en_data)}")
    print(f"  - Brasileiro (nativo): {len(brazilian_qa)}")
    print(f"  - TOTAL: {len(combined)}")

    # Calcular proporções
    total = len(combined)
    if total > 0:
        print(f"\n  Proporções finais:")
        print(f"    - PT: {len(pt_data)/total:.1%}")
        print(f"    - EN: {len(en_data)/total:.1%}")
        print(f"    - BR: {len(brazilian_qa)/total:.1%}")

    # Embaralhar
    random.shuffle(combined)

    return combined


# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def prepare_dataset(
    limit: Optional[int] = None,
    resume: bool = True,
    test_mode: bool = False,
    force_translate: bool = False,
    en_ratio: float = DEFAULT_EN_RATIO,
    skip_brazilian: bool = False,
    only_translate: bool = False
):
    """
    Pipeline principal de preparação do dataset.

    Args:
        limit: Limitar a N registros
        resume: Se True, continua do checkpoint
        test_mode: Se True, processa apenas 10 registros
        force_translate: Se True, força re-tradução
        en_ratio: Proporção de dados em inglês
        skip_brazilian: Se True, não inclui QA brasileiro
        only_translate: Se True, apenas traduz (não compõe dataset)
    """
    print("=" * 70)
    print("  PREPARAÇÃO DO DATASET PARA FINE-TUNING (v2)")
    print("  Tech Challenge Fase 3 - FIAP")
    print("  Dataset Híbrido: PT + EN + Brasileiro")
    print("=" * 70)
    print()

    if test_mode:
        limit = 10
        print("🧪 MODO TESTE: Processando apenas 10 registros")
        print()

    # -------------------------------------------------------------------------
    # Etapa 1: Tradução (ou carregar cache)
    # -------------------------------------------------------------------------
    print("=" * 50)
    print("  ETAPA 1: Tradução MedQuAD")
    print("=" * 50)

    pt_data = translate_medquad(
        limit=limit,
        resume=resume,
        force=force_translate
    )

    if only_translate:
        print("\n✓ Apenas tradução solicitada. Finalizando.")
        return

    print()

    # -------------------------------------------------------------------------
    # Etapa 2: Amostra em inglês
    # -------------------------------------------------------------------------
    print("=" * 50)
    print("  ETAPA 2: Amostra em Inglês")
    print("=" * 50)

    en_data = get_english_sample(pt_data, en_ratio=en_ratio)

    print()

    # -------------------------------------------------------------------------
    # Etapa 3: QA Brasileiro
    # -------------------------------------------------------------------------
    print("=" * 50)
    print("  ETAPA 3: QA Brasileiro")
    print("=" * 50)

    if skip_brazilian:
        print("  Pulando QA brasileiro (--skip-brazilian)")
        brazilian_qa = []
    else:
        brazilian_qa = get_brazilian_qa()

    print()

    # -------------------------------------------------------------------------
    # Etapa 4: Composição final
    # -------------------------------------------------------------------------
    print("=" * 50)
    print("  ETAPA 4: Composição Final")
    print("=" * 50)

    final_data = compose_final_dataset(pt_data, en_data, brazilian_qa)

    print()
    save_jsonl(final_data, OUTPUT_FILE)

    # -------------------------------------------------------------------------
    # Resumo final
    # -------------------------------------------------------------------------
    print()
    print("=" * 70)
    print("  PREPARAÇÃO CONCLUÍDA!")
    print("=" * 70)
    print()
    print("  Arquivos gerados:")
    print(f"    - {TRANSLATED_FILE} (cache tradução)")
    print(f"    - {EN_SAMPLE_FILE} (amostra inglês)")
    if not skip_brazilian:
        print(f"    - {BRAZILIAN_QA_FILE} (QA brasileiro)")
    print(f"    - {OUTPUT_FILE} (dataset final)")
    print()
    print(f"  Total de registros: {len(final_data)}")
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
        description="Prepara dataset híbrido para fine-tuning (PT + EN + BR)"
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
        help='Limita tradução a N registros'
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
    parser.add_argument(
        '--force-translate',
        action='store_true',
        help='Força re-tradução mesmo se cache existir'
    )
    parser.add_argument(
        '--en-ratio',
        type=float,
        default=DEFAULT_EN_RATIO,
        help=f'Proporção de dados em inglês (padrão: {DEFAULT_EN_RATIO})'
    )
    parser.add_argument(
        '--skip-brazilian',
        action='store_true',
        help='Não incluir QA brasileiro'
    )
    parser.add_argument(
        '--only-translate',
        action='store_true',
        help='Apenas traduzir, não compor dataset final'
    )

    args = parser.parse_args()

    resume = not args.no_resume

    prepare_dataset(
        limit=args.limit,
        resume=resume,
        test_mode=args.test,
        force_translate=args.force_translate,
        en_ratio=args.en_ratio,
        skip_brazilian=args.skip_brazilian,
        only_translate=args.only_translate
    )


if __name__ == "__main__":
    main()
