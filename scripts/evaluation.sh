#!/bin/bash
set -euo pipefail

# ============================================================
# evaluation.sh - Pipeline Completo de Avaliacao Multi-Checkpoint
#
# Executa avaliacoes para todos os checkpoints disponiveis,
# nas duas trilhas (A: perguntas manuais, B: validacao MedQuAD).
#
# Uso:
#   bash scripts/evaluation.sh             # roda tudo (pula existentes)
#   bash scripts/evaluation.sh --force     # re-executa tudo
#
# Requer GPU para scripts 05 e 06.
# ============================================================

# Mapeamento de checkpoints:
#
#   Tag        Checkpoint                       Steps   ~Epoch
#   --------   ------------------------------   -----   ------
#   epoch0_5   models/checkpoints/checkpoint-500    500    0.4
#   epoch1     models/checkpoints/checkpoint-1000  1000    0.9
#   epoch1_5   models/checkpoints/checkpoint-1500  1500    1.3
#   epoch2     models/checkpoints/checkpoint-2000  2000    1.7
#   epoch2_5   models/checkpoints/checkpoint-2500  2500    2.2
#   epoch4     models/checkpoints/checkpoint-5000  5000    4.3
#   epoch5     models/medical-assistant-final      5780    5.0

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
EVAL_DIR="$PROJECT_ROOT/data/evaluation"

cd "$PROJECT_ROOT"

FORCE=false
if [[ "${1:-}" == "--force" ]]; then
    FORCE=true
fi

# Tags e caminhos (arrays paralelos para manter a ordem)
TAGS=(       epoch0_5                              epoch1                                epoch1_5                              epoch2                                epoch2_5                              epoch4                                epoch5)
CKPT_PATHS=( models/checkpoints/checkpoint-500     models/checkpoints/checkpoint-1000    models/checkpoints/checkpoint-1500    models/checkpoints/checkpoint-2000    models/checkpoints/checkpoint-2500    models/checkpoints/checkpoint-5000    models/medical-assistant-final)

# Trilha B
VAL_QUESTIONS="data/evaluation/validacao_amostra.json"
VAL_BASELINE="data/evaluation/baseline_responses_val.json"

echo "============================================================"
echo "  PIPELINE DE AVALIACAO MULTI-CHECKPOINT"
echo "============================================================"
echo ""

# Listar checkpoints disponiveis
echo "Checkpoints configurados:"
AVAILABLE_TAGS=()
AVAILABLE_PATHS=()
for i in "${!TAGS[@]}"; do
    tag="${TAGS[$i]}"
    path="${CKPT_PATHS[$i]}"
    if [[ -d "$path" ]]; then
        echo "  [ok] $tag -> $path"
        AVAILABLE_TAGS+=("$tag")
        AVAILABLE_PATHS+=("$path")
    else
        echo "  [--] $tag -> $path (nao encontrado, sera pulado)"
    fi
done

if [[ ${#AVAILABLE_TAGS[@]} -eq 0 ]]; then
    echo ""
    echo "ERRO: Nenhum checkpoint encontrado!"
    exit 1
fi

echo ""
echo "Total: ${#AVAILABLE_TAGS[@]} checkpoints disponiveis"
echo ""

# ============================================================
# Passo 0: Gerar amostra de validacao (se necessario)
# ============================================================
echo "============================================================"
echo "[0/4] Amostra de validacao"
echo "============================================================"
if [[ ! -f "$VAL_QUESTIONS" ]]; then
    echo "Gerando validacao_amostra.json..."
    python scripts/05b_extrair_amostra_validacao.py
else
    echo "validacao_amostra.json ja existe."
fi
echo ""

# ============================================================
# Passo 1: Baseline
# ============================================================
echo "============================================================"
echo "[1/4] Baseline"
echo "============================================================"

# Trilha A
if [[ ! -f "$EVAL_DIR/baseline_responses.json" ]] || $FORCE; then
    echo "Trilha A: gerando baseline_responses.json..."
    python scripts/05_avaliar_baseline.py
else
    echo "Trilha A: baseline_responses.json ja existe."
fi

# Trilha B
if [[ ! -f "$VAL_BASELINE" ]] || $FORCE; then
    echo "Trilha B: gerando baseline_responses_val.json..."
    python scripts/05_avaliar_baseline.py \
        --questions-file "$VAL_QUESTIONS" --tag val
else
    echo "Trilha B: baseline_responses_val.json ja existe."
fi
echo ""

# ============================================================
# Passo 2: Avaliar cada checkpoint (Trilha A + B)
# ============================================================
echo "============================================================"
echo "[2/4] Avaliando checkpoints fine-tuned"
echo "============================================================"
echo ""

for i in "${!AVAILABLE_TAGS[@]}"; do
    tag="${AVAILABLE_TAGS[$i]}"
    path="${AVAILABLE_PATHS[$i]}"

    echo "------------------------------------------------------------"
    echo "  [$tag] Modelo: $path"
    echo "------------------------------------------------------------"

    # Trilha A
    output_a="$EVAL_DIR/finetuned_responses_${tag}.json"
    if [[ ! -f "$output_a" ]] || $FORCE; then
        echo "  Trilha A..."
        python scripts/06_avaliar_finetuned.py \
            --model-path "$path" --tag "$tag"
    else
        echo "  Trilha A: ja avaliado (finetuned_responses_${tag}.json existe)."
    fi

    # Trilha B
    output_b="$EVAL_DIR/finetuned_responses_${tag}_val.json"
    if [[ ! -f "$output_b" ]] || $FORCE; then
        echo "  Trilha B..."
        python scripts/06_avaliar_finetuned.py \
            --model-path "$path" --tag "${tag}_val" \
            --questions-file "$VAL_QUESTIONS" \
            --baseline-file "$VAL_BASELINE"
    else
        echo "  Trilha B: ja avaliado (finetuned_responses_${tag}_val.json existe)."
    fi

    echo ""
done

# ============================================================
# Passo 3: Comparacao unificada
# ============================================================
echo "============================================================"
echo "[3/4] Comparacao unificada"
echo "============================================================"
python scripts/06b_comparar_modelos.py
echo ""

# ============================================================
# Resumo
# ============================================================
echo "============================================================"
echo "  PIPELINE CONCLUIDO"
echo "============================================================"
echo ""
echo "Resultados em: $EVAL_DIR/"
echo "  - comparacao_completa.json"
echo "  - comparacao_completa.md"
echo ""
echo "Checkpoints avaliados: ${AVAILABLE_TAGS[*]}"
echo ""
