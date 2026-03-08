"""Interface Gradio do Assistente Virtual Médico."""

import gc
import json
import logging
import os
import sys
from pathlib import Path

import gradio as gr

# Adicionar raiz do projeto ao path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.flows.graph import run_assistant

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _load_patient_names() -> list[str]:
    """Carrega nomes dos pacientes (PostgreSQL -> fallback JSON)."""
    try:
        from sqlalchemy import text
        from sqlalchemy.orm import Session
        from src.database.connection import get_engine

        engine = get_engine()
        with Session(engine) as session:
            result = session.execute(text("SELECT nome FROM pacientes ORDER BY nome"))
            names = [row[0] for row in result]
        if names:
            logger.info("Pacientes carregados do PostgreSQL: %d", len(names))
            return names
    except Exception as e:
        logger.info("PostgreSQL indisponivel (%s) — usando JSON.", e)

    pacientes_file = PROJECT_ROOT / "data" / "synthetic" / "pacientes.json"
    if not pacientes_file.exists():
        return []
    try:
        with open(pacientes_file, encoding="utf-8") as f:
            data = json.load(f)
        names = sorted(p["nome"] for p in data if "nome" in p)
        logger.info("Pacientes carregados do JSON: %d", len(names))
        return names
    except Exception:
        return []


# ---------------------------------------------------------------------------
# LLM loader com cascata, lazy loading e liberacao de memoria
# ---------------------------------------------------------------------------

LABEL_FT_LOCAL = "Fine-Tuned (local)"
LABEL_FT_HUB = "Fine-Tuned (Hub)"
LABEL_FT_GGUF = "Fine-Tuned (GGUF)"
LABEL_BASELINE = "Mistral 7B (baseline)"
LABEL_NO_LLM = "Sem LLM (protocolos apenas)"

BASELINE_MODEL_ID = os.getenv("BASELINE_MODEL", "mistralai/Mistral-7B-Instruct-v0.3")
GGUF_FILENAME = os.getenv("GGUF_FILENAME", "medical-assistant-Q4_K_M.gguf")
GGUF_HUB_REPO = os.getenv("GGUF_HUB_REPO", "zagari/medical-assistant-mistral-7b-ft-gguf")

# Estado global do modelo ativo
_current_label: str | None = None
_current_llm_fn = None
_current_model_ref = None
_current_tokenizer_ref = None


def _has_cuda() -> bool:
    try:
        import torch
        return torch.cuda.is_available()
    except Exception:
        return False


def _resolve_ft_source() -> tuple[str | None, str | None]:
    """Determina onde o fine-tuned LoRA esta: local, hub, ou indisponivel."""
    ft_path = os.getenv(
        "FINE_TUNED_MODEL",
        str(PROJECT_ROOT / "models" / "medical-assistant-final"),
    )

    ft_resolved = Path(ft_path)
    if not ft_resolved.is_absolute():
        ft_resolved = PROJECT_ROOT / ft_resolved

    if ft_resolved.exists():
        return str(ft_resolved), LABEL_FT_LOCAL

    is_hub = "/" in ft_path and not ft_path.startswith(("/", "."))
    if is_hub:
        return ft_path, LABEL_FT_HUB

    return None, None


def _resolve_gguf_path() -> str | None:
    """Encontra arquivo GGUF local ou retorna None."""
    models_dir = PROJECT_ROOT / "models"
    if models_dir.exists():
        # Procurar em models/ e todas as subpastas (incluindo gguf_gguf/)
        for gguf in models_dir.glob("**/*.gguf"):
            return str(gguf)
    return None


def _unload_current():
    """Libera modelo atual da memoria (GPU e RAM)."""
    global _current_llm_fn, _current_model_ref, _current_tokenizer_ref, _current_label

    if _current_model_ref is not None:
        logger.info("Liberando modelo '%s' da memoria...", _current_label)
        del _current_model_ref
        del _current_tokenizer_ref
        _current_model_ref = None
        _current_tokenizer_ref = None
        _current_llm_fn = None
        gc.collect()

        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except Exception:
            pass

        logger.info("Memoria liberada.")

    _current_llm_fn = None
    _current_label = None


def _is_lora_adapter(model_path: str) -> bool:
    """Verifica se o diretorio contem adaptadores LoRA (adapter_config.json)."""
    return Path(model_path).is_dir() and (Path(model_path) / "adapter_config.json").exists()


def _load_model_transformers(model_name: str) -> tuple[callable, object, object] | None:
    """Carrega modelo via transformers (requer CUDA).

    Detecta automaticamente se model_name aponta para adaptadores LoRA
    (presenca de adapter_config.json) e, nesse caso, carrega o modelo base
    primeiro e aplica os adaptadores via PEFT.
    """
    try:
        import torch

        if not torch.cuda.is_available():
            logger.info("CUDA nao disponivel — pulando carregamento transformers de %s.", model_name)
            return None

        from transformers import AutoModelForCausalLM, AutoTokenizer

        if _is_lora_adapter(model_name):
            # --- LoRA adapter: carregar base + aplicar PEFT ---
            import json
            from peft import PeftModel

            adapter_cfg_path = Path(model_name) / "adapter_config.json"
            with open(adapter_cfg_path) as f:
                adapter_cfg = json.load(f)
            base_model_name = adapter_cfg.get("base_model_name_or_path", BASELINE_MODEL_ID)

            logger.info(
                "Detectado LoRA adapter em %s — carregando base '%s' + adaptadores...",
                model_name, base_model_name,
            )

            tokenizer = AutoTokenizer.from_pretrained(model_name)
            base_model = AutoModelForCausalLM.from_pretrained(
                base_model_name,
                torch_dtype=torch.float16,
                device_map="auto",
            )
            model = PeftModel.from_pretrained(base_model, model_name)
            model = model.merge_and_unload()
            logger.info("LoRA adapters merged com sucesso.")
        else:
            # --- Modelo completo (baseline ou merged) ---
            logger.info("Carregando modelo (transformers) de %s...", model_name)
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                device_map="auto",
            )

        def llm_fn(prompt: str) -> str:
            inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=1024,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id,
                )
            response = tokenizer.decode(
                outputs[0][inputs.input_ids.shape[1]:],
                skip_special_tokens=True,
            )
            return response.strip()

        logger.info("Modelo carregado com sucesso (transformers) de %s.", model_name)
        return llm_fn, model, tokenizer
    except Exception as e:
        logger.warning("Falha ao carregar modelo (transformers) de %s: %s", model_name, e)
        return None


def _load_model_gguf(gguf_path: str) -> tuple[callable, object, None] | None:
    """Carrega modelo GGUF via llama-cpp-python (CPU/Metal, sem CUDA)."""
    try:
        from llama_cpp import Llama

        logger.info("Carregando modelo GGUF de %s...", gguf_path)
        model = Llama(
            model_path=gguf_path,
            n_ctx=2048,
            n_threads=os.cpu_count() or 4,
            verbose=False,
        )

        def llm_fn(prompt: str) -> str:
            output = model(
                prompt,
                max_tokens=1024,
                temperature=0.7,
                stop=["### Instrução:", "### Entrada:", "</s>"],
            )
            return output["choices"][0]["text"].strip()

        logger.info("Modelo GGUF carregado com sucesso (%s).", gguf_path)
        return llm_fn, model, None
    except ImportError:
        logger.warning(
            "llama-cpp-python nao instalado — instale com: "
            "pip install llama-cpp-python"
        )
        return None
    except Exception as e:
        logger.warning("Falha ao carregar modelo GGUF de %s: %s", gguf_path, e)
        return None


def _download_gguf_from_hub() -> str | None:
    """Baixa arquivo GGUF do HF Hub para models/. Retorna path ou None."""
    try:
        from huggingface_hub import hf_hub_download

        dest_dir = PROJECT_ROOT / "models"
        dest_dir.mkdir(parents=True, exist_ok=True)

        logger.info(
            "Baixando GGUF de %s/%s...", GGUF_HUB_REPO, GGUF_FILENAME,
        )
        path = hf_hub_download(
            repo_id=GGUF_HUB_REPO,
            filename=GGUF_FILENAME,
            local_dir=str(dest_dir),
        )
        logger.info("GGUF baixado para %s.", path)
        return path
    except Exception as e:
        logger.warning("Falha ao baixar GGUF do Hub: %s", e)
        return None


def _probe_options() -> list[str]:
    """Verifica quais opcoes estao potencialmente disponiveis (sem carregar)."""
    options = []
    has_cuda = _has_cuda()

    # Fine-tuned LoRA (precisa de CUDA)
    ft_path, ft_label = _resolve_ft_source()
    if ft_label and has_cuda:
        options.append(ft_label)

    # Fine-tuned GGUF (funciona sem CUDA)
    gguf_local = _resolve_gguf_path()
    gguf_available = gguf_local is not None
    if not gguf_available:
        # Verificar se o pacote llama-cpp-python esta instalado
        try:
            import llama_cpp  # noqa: F401
            # GGUF pode ser baixado do Hub sob demanda
            gguf_available = True
        except ImportError:
            pass
    if gguf_available:
        options.append(LABEL_FT_GGUF)

    # Baseline (precisa de CUDA)
    if has_cuda:
        options.append(LABEL_BASELINE)

    options.append(LABEL_NO_LLM)
    return options


def activate_model(label: str) -> str:
    """Ativa modelo pelo label. Retorna mensagem de status."""
    global _current_label, _current_llm_fn, _current_model_ref, _current_tokenizer_ref

    if label == _current_label:
        return f"Modelo ativo: {label}"

    _unload_current()

    # Sem LLM
    if label == LABEL_NO_LLM:
        _current_label = LABEL_NO_LLM
        return "Modo sem LLM ativo — respostas baseadas apenas em protocolos."

    # Fine-tuned LoRA (transformers + CUDA)
    if label in (LABEL_FT_LOCAL, LABEL_FT_HUB):
        ft_path, _ = _resolve_ft_source()
        if ft_path:
            result = _load_model_transformers(ft_path)
            if result:
                _current_llm_fn, _current_model_ref, _current_tokenizer_ref = result
                _current_label = label
                return f"Modelo fine-tuned carregado de: {ft_path}"

        # Fallback: tentar GGUF
        logger.warning("Fine-tuned LoRA indisponivel, tentando GGUF...")
        return activate_model(LABEL_FT_GGUF)

    # Fine-tuned GGUF (CPU/Metal)
    if label == LABEL_FT_GGUF:
        gguf_path = _resolve_gguf_path()
        if not gguf_path:
            gguf_path = _download_gguf_from_hub()
        if gguf_path:
            result = _load_model_gguf(gguf_path)
            if result:
                _current_llm_fn, _current_model_ref, _current_tokenizer_ref = result
                _current_label = LABEL_FT_GGUF
                return f"Modelo GGUF carregado de: {gguf_path}"

        # Fallback: baseline ou sem LLM
        if _has_cuda():
            logger.warning("GGUF indisponivel, tentando baseline...")
            return activate_model(LABEL_BASELINE)
        logger.warning("GGUF indisponivel, ativando modo sem LLM.")
        _current_label = LABEL_NO_LLM
        return "Modelo GGUF nao disponivel — modo sem LLM ativo."

    # Baseline (transformers + CUDA)
    if label == LABEL_BASELINE:
        result = _load_model_transformers(BASELINE_MODEL_ID)
        if result:
            _current_llm_fn, _current_model_ref, _current_tokenizer_ref = result
            _current_label = LABEL_BASELINE
            return f"Modelo baseline carregado: {BASELINE_MODEL_ID}"

        logger.warning("Baseline indisponivel, ativando modo sem LLM.")
        _current_label = LABEL_NO_LLM
        return "Nenhum modelo disponivel — modo sem LLM ativo."

    _current_label = LABEL_NO_LLM
    return "Opcao desconhecida — modo sem LLM ativo."


def _startup_load() -> tuple[list[str], str, str]:
    """Startup: tenta cascata fine-tuned -> GGUF -> baseline -> sem LLM."""
    options = _probe_options()

    for label in options:
        status = activate_model(label)
        if _current_llm_fn is not None or _current_label == LABEL_NO_LLM:
            return options, _current_label, status

    return options, LABEL_NO_LLM, "Nenhum modelo carregado."


# ---------------------------------------------------------------------------
# Funcao principal de consulta
# ---------------------------------------------------------------------------

def consultar(query: str, patient_id: str, model_label: str) -> tuple[str, str, str, str, str, str]:
    """Executa o assistente e retorna (resposta, confianca, fontes, audit_log, modelo_ativo, status)."""
    if not query.strip():
        return "Por favor, digite uma consulta.", "", "", "", gr.update(), gr.update()

    pid = patient_id.strip() if patient_id and patient_id.strip() else None

    if model_label != _current_label:
        activate_model(model_label)

    # Detectar se houve fallback (modelo ativo difere do selecionado)
    modelo_ativo = _current_label or LABEL_NO_LLM
    if modelo_ativo != model_label:
        model_status_msg = f"⚠ {model_label} indisponível — usando: {modelo_ativo}"
    else:
        model_status_msg = f"Modelo ativo: {modelo_ativo}"

    try:
        result = run_assistant(query=query.strip(), patient_id=pid, llm=_current_llm_fn)
    except Exception as e:
        logger.error("Erro ao executar assistente: %s", e)
        return f"Erro interno: {e}", "", "", "", modelo_ativo, model_status_msg

    resposta = result.get("final_response", "Sem resposta.")

    conf = result.get("confidence", "")
    conf_labels = {"alta": "🟢 Alta", "media": "🟡 Média", "baixa": "🔴 Baixa"}
    confianca = conf_labels.get(conf, conf)

    sources = result.get("sources", [])
    fontes = "\n".join(f"• {s}" for s in sources) if sources else "Nenhuma fonte citada."

    audit = result.get("audit_log", [])
    audit_str = json.dumps(audit, indent=2, ensure_ascii=False, default=str)

    return resposta, confianca, fontes, audit_str, modelo_ativo, model_status_msg


# ---------------------------------------------------------------------------
# Exemplos
# ---------------------------------------------------------------------------

EXAMPLES = [
    ["Qual o protocolo de tratamento para hipertensão arterial?", ""],
    ["Quais exames de seguimento para diabetes tipo 2?", "Maria Alice Ferreira"],
    ["Conduta para suspeita de IAM com supra de ST?", ""],
    ["Quais os últimos exames do paciente Bruno Barros?", "Bruno Barros"],
    ["Protocolo de sepse: quando iniciar antibioticoterapia?", ""],
    ["Qual a receita do dia?", ""],
]


# ---------------------------------------------------------------------------
# Interface Gradio
# ---------------------------------------------------------------------------

def build_interface() -> gr.Blocks:
    """Constroi e retorna a interface Gradio."""

    options, default_label, startup_status = _startup_load()
    logger.info("Startup: %s", startup_status)

    with gr.Blocks(
        title="Assistente Virtual Médico — FIAP Tech Challenge",
    ) as demo:
        gr.Markdown(
            """
            # 🏥 Assistente Virtual Médico
            **Tech Challenge Fase 3** — FIAP Pós-Graduação em IA para Devs

            Sistema multi-agente com LangGraph, RAG (ChromaDB) e guardrails de segurança.
            Todas as respostas são sugestões e devem ser validadas por um profissional de saúde.
            """
        )

        with gr.Row():
            with gr.Column(scale=3):
                query_input = gr.Textbox(
                    label="Consulta médica",
                    placeholder="Ex: Qual o protocolo de tratamento para hipertensão?",
                    lines=3,
                )
                patient_names = _load_patient_names()
                patient_input = gr.Dropdown(
                    choices=[""] + patient_names,
                    value="",
                    label="Paciente (opcional)",
                    allow_custom_value=True,
                    filterable=True,
                )
                submit_btn = gr.Button("Consultar", variant="primary", size="lg")

            with gr.Column(scale=1):
                model_selector = gr.Radio(
                    choices=options,
                    value=default_label,
                    label="Modelo LLM",
                    info="Selecione o modelo para gerar respostas",
                )
                model_status = gr.Textbox(
                    label="Status do modelo",
                    value=startup_status,
                    interactive=False,
                    lines=2,
                )
                confianca_output = gr.Textbox(label="Confiança", interactive=False)
                fontes_output = gr.Textbox(
                    label="Fontes consultadas", lines=6, interactive=False,
                )

        gr.Markdown("### Resposta do Assistente")
        resposta_output = gr.Markdown(
            value="*Aguardando consulta...*",
        )

        with gr.Accordion("Log de Auditoria", open=False):
            audit_output = gr.Code(label="Audit Log (JSON)", language="json")

        gr.Examples(
            examples=EXAMPLES,
            inputs=[query_input, patient_input],
            label="Exemplos de consultas",
        )

        gr.Markdown(
            """
            ---
            **Grupo Sala 14** | Adriana Martins · Diego Oliveira · Eduardo Zagari · Renan Torres
            """
        )

        def on_model_change(label):
            status = activate_model(label)
            modelo_ativo = _current_label or LABEL_NO_LLM
            if modelo_ativo != label:
                status = f"⚠ {label} indisponível — usando: {modelo_ativo}"
            return modelo_ativo, status

        model_selector.change(
            fn=on_model_change,
            inputs=[model_selector],
            outputs=[model_selector, model_status],
        )

        consultar_outputs = [
            resposta_output, confianca_output, fontes_output, audit_output,
            model_selector, model_status,
        ]

        submit_btn.click(
            fn=consultar,
            inputs=[query_input, patient_input, model_selector],
            outputs=consultar_outputs,
        )
        query_input.submit(
            fn=consultar,
            inputs=[query_input, patient_input, model_selector],
            outputs=consultar_outputs,
        )

    return demo


if __name__ == "__main__":
    demo = build_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        theme=gr.themes.Soft(primary_hue="red"),
    )
