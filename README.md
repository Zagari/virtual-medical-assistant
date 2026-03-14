# Virtual Medical Assistant

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Hugging Face](https://img.shields.io/badge/HuggingFace-Model-orange)](https://huggingface.co/zagari/medical-assistant-mistral-7b-ft)

Assistente Virtual Médico com IA Generativa, desenvolvido como parte do **Tech Challenge Fase 3** do curso de Pós-Graduação em Inteligência Artificial para Devs da FIAP.

## Visão Geral

O sistema integra cinco pilares de IA generativa:

1. **Fine-tuning** do Mistral 7B Instruct v0.3 com QLoRA 4-bit usando o dataset MedQuAD traduzido para português (~20.500 pares QA)
2. **RAG** (Retrieval-Augmented Generation) com 14 Linhas de Cuidado reais + 5 protocolos de emergência sintéticos indexados no ChromaDB
3. **Grafo Multi-Agente** em LangGraph com 7 agentes especializados
4. **Segurança** com guardrails que impedem prescrições diretas e exigem validação humana
5. **Interface** Gradio para demonstração interativa

### Resultados do Fine-Tuning

A avaliação multi-checkpoint revelou:
- **Ponto ótimo**: ~1,3 épocas (checkpoint-1500)
- **Ganhos**: +668% BLEU, +141% ROUGE-L vs baseline
- **Descoberta**: Colapso catastrófico após época 1.5 (5 épocas é excessivo para QLoRA em modelos 7B+)

## Arquitetura

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Interface Gradio                               │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      Grafo Multi-Agente (LangGraph)                      │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌────────┐│
│  │ Triagem  │──▶│Protocolo │──▶│Raciocínio│──▶│Guardrails│──▶│Explica-││
│  │          │   │  + RAG   │   │   LLM    │   │          │   │bilidade││
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘   └────────┘│
│       │              │                              │              │    │
│       ▼              │                              │              │    │
│  ┌──────────┐        │                              │              │    │
│  │ Paciente │────────┘                              │              │    │
│  │   Data   │                                       │              │    │
│  └──────────┘                                       └──────────────┼───▶│
│                                                                    │    │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                      Logger (Auditoria)                          │◀──┘
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
         │                    │
         ▼                    ▼
   ┌──────────┐        ┌──────────┐
   │PostgreSQL│        │ ChromaDB │
   │(Pacientes│        │(Protoco- │
   │  Exames) │        │   los)   │
   └──────────┘        └──────────┘
```

## Quickstart (5 minutos)

Para testar o assistente sem re-treinar o modelo:

```bash
# Clone o repositório
git clone https://github.com/Zagari/virtual-medical-assistant.git
cd virtual-medical-assistant

# Instale dependências
pip install -r requirements.txt

# Execute o quickstart
bash scripts/quickstart.sh
```

O script automaticamente:
1. Cria o `.env` a partir do `.env.example`
2. Detecta hardware (GPU NVIDIA → LoRA, senão → GGUF)
3. Sobe PostgreSQL via Docker e popula com 80 pacientes sintéticos
4. Indexa protocolos clínicos no ChromaDB
5. Inicia a interface em http://localhost:7860

### Pré-requisitos

- Python 3.11+
- Docker Desktop (para PostgreSQL)
- **GPU NVIDIA (CUDA)** para usar modelo fine-tuned via LoRA
- **Ou qualquer máquina** para usar modelo GGUF (CPU/Apple Silicon)

## Estrutura do Projeto

```
virtual-medical-assistant/
├── scripts/                    # Pipeline numerado (01-08)
│   ├── 01_gerar_dados_sinteticos.py
│   ├── 02_setup_postgres.py
│   ├── 03_preparar_dataset.py
│   ├── 04_indexar_protocolos.py
│   ├── 05_avaliar_baseline.py
│   ├── 06_avaliar_finetuned.py
│   ├── 07_iniciar_app.py
│   └── 08_exportar_gguf.py
├── src/
│   ├── data/                   # Geração de dados sintéticos
│   ├── database/               # Models e queries PostgreSQL
│   ├── assistant/              # RAG com ChromaDB
│   ├── flows/                  # LangGraph
│   │   ├── graph.py            # Definição do grafo
│   │   ├── state.py            # Estado compartilhado
│   │   └── agents/             # 7 agentes especializados
│   └── security/               # Guardrails
├── app/
│   └── main.py                 # Interface Gradio
├── notebooks/
│   ├── 03_fine_tuning.ipynb           # Google Colab
│   ├── 03_fine_tuning_local.ipynb     # Servidor local
│   └── 03_fine_tuning_early_stopping.ipynb
├── data/
│   ├── synthetic/              # 80 pacientes fictícios
│   ├── processed/              # Dataset de treino (~20.500 QA)
│   ├── linhas_de_cuidado/      # 14 protocolos clínicos (PDF → Markdown)
│   └── evaluation/             # Resultados de avaliação
├── docs/                       # Relatório técnico LaTeX
└── models/                     # Checkpoints e modelos finais
```

## Pipeline de Reprodução

### Reprodução Completa (do zero)

```bash
# 0. Setup
pip install -r requirements.txt
cp .env.example .env

# 1. Gerar dados sintéticos (80 pacientes)
python scripts/01_gerar_dados_sinteticos.py

# 2. Setup PostgreSQL
python scripts/02_setup_postgres.py

# 3. Preparar dataset (MedQuAD + tradução)
python scripts/03_preparar_dataset.py

# --- PAUSA: Fine-tuning (Google Colab ou Local) ---
# Opção A: Usar modelo pré-treinado do Hub (já configurado)
# Opção B: notebooks/03_fine_tuning.ipynb no Colab
# Opção C: notebooks/03_fine_tuning_local.ipynb (GPU 16GB+)

# 4. Indexar protocolos no ChromaDB
python scripts/04_indexar_protocolos.py

# 5-6. Avaliação (opcional)
python scripts/05_avaliar_baseline.py
python scripts/06_avaliar_finetuned.py

# 7. Iniciar assistente
python scripts/07_iniciar_app.py
```

### O que já está pronto no repositório

- **Dados sintéticos** (`data/synthetic/`) - 80 pacientes com exames, prontuários, receitas
- **Dataset de treino** (`data/processed/training_data.jsonl`) - ~20.500 pares QA
- **Protocolos em Markdown** (`data/linhas_de_cuidado/extracted/`) - 14 Linhas de Cuidado
- **Modelo fine-tuned** - Download automático do [Hugging Face Hub](https://huggingface.co/zagari/medical-assistant-mistral-7b-ft)

## Agentes do Sistema

| Agente | Responsabilidade |
|--------|-----------------|
| **Triagem** | Classifica consulta (protocolo/paciente/ambos) e extrai entidades |
| **Protocolo** | Busca semântica no ChromaDB com ranking por comorbidades |
| **Paciente Data** | Consulta PostgreSQL (exames, prontuários, receitas) |
| **Raciocínio** | Gera resposta usando LLM fine-tuned com contexto |
| **Guardrails** | Valida resposta (sem prescrição direta, requer validação humana) |
| **Explicabilidade** | Adiciona fontes, confiança e warnings |
| **Logger** | Persiste audit trail em JSONL |

## Configuração

### Variáveis de Ambiente (`.env`)

```bash
# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=medical_assistant
POSTGRES_USER=postgres
POSTGRES_PASSWORD=changeme

# Modelo Fine-Tuned (local ou Hub)
FINE_TUNED_MODEL=zagari/medical-assistant-mistral-7b-ft

# Modelo Baseline
BASELINE_MODEL=mistralai/Mistral-7B-Instruct-v0.3

# GGUF (para CPU/Apple Silicon)
GGUF_FILENAME=medical-assistant-Q4_K_M.gguf
GGUF_HUB_REPO=zagari/medical-assistant-mistral-7b-ft-gguf
```

### Seleção de Modelo

O sistema detecta automaticamente o hardware e oferece opções:

| Hardware | Modelo Usado | Performance |
|----------|--------------|-------------|
| GPU NVIDIA (CUDA) | LoRA fine-tuned | ~2-5s/resposta |
| CPU/Apple Silicon | GGUF Q4_K_M | ~5-15s/resposta |
| Sem LLM | Fallback determinístico | Instantâneo |

## Stack Tecnológica

### Core
- **LangChain** / **LangGraph** - Orquestração multi-agente
- **ChromaDB** - Vector store para RAG
- **Sentence Transformers** - Embeddings multilíngues (E5)

### LLM / Fine-tuning
- **Mistral 7B Instruct v0.3** - Modelo base
- **QLoRA** (PEFT + bitsandbytes) - Fine-tuning 4-bit
- **llama-cpp-python** - Inferência GGUF

### Database
- **PostgreSQL** - Dados estruturados de pacientes
- **SQLAlchemy** - ORM

### Interface
- **Gradio** - UI web

## Segurança

O sistema implementa múltiplas camadas de segurança:

1. **Guardrails de Resposta**:
   - Bloqueia prescrições diretas ("tome X mg")
   - Exige disclaimer de validação humana
   - Impede diagnósticos definitivos ("o paciente tem")

2. **Retry Automático**:
   - Até 2 tentativas com feedback para correção

3. **Audit Trail**:
   - Logging completo em `logs/audit_{date}.jsonl`
   - Trace de cada agente com timestamp

4. **Dados Fictícios**:
   - Todos os pacientes são sintéticos (Faker pt_BR)
   - Gerados com coerência clínica

## Aviso de Segurança

> **Este sistema foi projetado exclusivamente como ferramenta de SUPORTE À DECISÃO CLÍNICA, nunca como substituto do profissional de saúde. Todas as respostas incluem avisos de validação humana obrigatória.**

## Grupo

**Sala 14** - Tech Challenge Fase 3

- Adriana Martins de Souza - RM 368050
- Diego Oliveira da Silva - RM 367964
- Eduardo Nicola F. Zagari - RM 368021
- Renan de Assis Torres - RM 368513

## Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

## Links

- [Repositório GitHub](https://github.com/Zagari/virtual-medical-assistant)
- [Modelo no Hugging Face Hub](https://huggingface.co/zagari/medical-assistant-mistral-7b-ft)
- [Vídeo Demonstrativo](https://youtube.com/TODO)
