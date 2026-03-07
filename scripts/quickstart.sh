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
#   2. Detecta hardware e instala llama-cpp-python se necessário
#   3. Sobe PostgreSQL via Docker e popula com dados sintéticos
#   4. Indexa protocolos clínicos no ChromaDB
#   5. Inicia a interface Gradio
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
    echo "[1/5] Criando .env a partir de .env.example..."
    cp .env.example .env
    echo "      Modelo configurado: $(grep FINE_TUNED_MODEL .env | head -1)"
else
    echo "[1/5] .env já existe — mantendo configuração atual."
fi
echo ""

# ----- Passo 2: Detectar hardware e instalar llama-cpp-python -----
echo "[2/5] Verificando hardware e dependências para LLM..."

HAS_CUDA=$(python -c "import torch; print(torch.cuda.is_available())" 2>/dev/null || echo "False")
HAS_LLAMA_CPP=$(python -c "import llama_cpp" 2>/dev/null && echo "True" || echo "False")

if [ "$HAS_CUDA" = "True" ]; then
    echo "      GPU NVIDIA detectada — modelo será carregado via transformers."
elif [ "$HAS_LLAMA_CPP" = "True" ]; then
    echo "      llama-cpp-python já instalado — modelo GGUF disponível."
else
    echo "      Sem GPU NVIDIA — instalando llama-cpp-python para modelo GGUF..."
    if [ "$(uname)" = "Darwin" ] && [ "$(uname -m)" = "arm64" ]; then
        echo "      Apple Silicon detectado — compilando com Metal (aceleração GPU)."
        CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python
    else
        pip install llama-cpp-python
    fi
    echo "      llama-cpp-python instalado."
fi
echo ""

# ----- Passo 3: PostgreSQL -----
echo "[3/5] Configurando PostgreSQL (Docker)..."
python scripts/02_setup_postgres.py
echo ""

# ----- Passo 4: ChromaDB -----
echo "[4/5] Indexando protocolos clínicos no ChromaDB..."
python scripts/04_indexar_protocolos.py
echo ""

# ----- Passo 5: Gradio -----
echo "[5/5] Iniciando assistente..."
echo ""
echo "============================================================"
echo "  O assistente estará disponível em http://localhost:7860"
echo "============================================================"
echo ""
python scripts/07_iniciar_app.py
