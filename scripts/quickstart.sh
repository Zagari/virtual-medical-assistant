#!/usr/bin/env bash
# ============================================================================
# Quickstart — Assistente Virtual Médico
# ============================================================================
# Prepara e inicia o assistente com o mínimo de passos.
#
# Pré-requisitos:
#   - Python 3.11+
#   - Docker Desktop instalado e rodando
#   - pip install -r requirements.txt (já executado)
#
# Uso:
#   bash scripts/quickstart.sh
#
# O que este script faz:
#   1. Cria .env a partir do .env.example (se não existir)
#   2. Sobe PostgreSQL via Docker e popula com dados sintéticos
#   3. Indexa protocolos clínicos no ChromaDB
#   4. Inicia a interface Gradio
#
# O modelo fine-tuned é baixado automaticamente do Hugging Face Hub
# na primeira consulta (configurado no .env).
# ============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo "============================================================"
echo "  QUICKSTART — Assistente Virtual Médico"
echo "============================================================"
echo ""

# ----- Passo 1: .env -----
if [ ! -f .env ]; then
    echo "[1/4] Criando .env a partir de .env.example..."
    cp .env.example .env
    echo "      Modelo configurado: $(grep FINE_TUNED_MODEL .env | head -1)"
else
    echo "[1/4] .env já existe — mantendo configuração atual."
fi
echo ""

# ----- Passo 2: PostgreSQL -----
echo "[2/4] Configurando PostgreSQL (Docker)..."
python scripts/02_setup_postgres.py
echo ""

# ----- Passo 3: ChromaDB -----
echo "[3/4] Indexando protocolos clínicos no ChromaDB..."
python scripts/04_indexar_protocolos.py
echo ""

# ----- Passo 4: Gradio -----
echo "[4/4] Iniciando assistente..."
echo ""
echo "============================================================"
echo "  O assistente estará disponível em http://localhost:7860"
echo "============================================================"
echo ""
python scripts/07_iniciar_app.py
