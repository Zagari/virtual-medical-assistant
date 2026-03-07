"""Interface Gradio do Assistente Virtual Médico."""

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

# ---------------------------------------------------------------------------
# LLM loader (opcional)
# ---------------------------------------------------------------------------

_llm_instance = None


def _load_llm():
    """Tenta carregar o modelo fine-tuned. Retorna None se indisponível."""
    global _llm_instance
    if _llm_instance is not None:
        return _llm_instance

    model_path = os.getenv("FINE_TUNED_MODEL", str(PROJECT_ROOT / "models" / "medical-assistant"))
    if not Path(model_path).exists():
        logger.info("Modelo fine-tuned não encontrado em %s — usando fallback.", model_path)
        return None

    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch

        logger.info("Carregando modelo fine-tuned de %s...", model_path)
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16,
            device_map="auto",
        )

        def llm_fn(prompt: str) -> str:
            inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=512,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id,
                )
            response = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
            return response.strip()

        _llm_instance = llm_fn
        logger.info("Modelo fine-tuned carregado com sucesso.")
        return _llm_instance
    except Exception as e:
        logger.warning("Falha ao carregar modelo: %s — usando fallback.", e)
        return None


# ---------------------------------------------------------------------------
# Função principal de consulta
# ---------------------------------------------------------------------------

def consultar(query: str, patient_id: str) -> tuple[str, str, str, str]:
    """
    Executa o assistente e retorna (resposta, confiança, fontes, audit_log).
    """
    if not query.strip():
        return "Por favor, digite uma consulta.", "", "", ""

    pid = patient_id.strip() if patient_id and patient_id.strip() else None
    llm = _load_llm()

    try:
        result = run_assistant(query=query.strip(), patient_id=pid, llm=llm)
    except Exception as e:
        logger.error("Erro ao executar assistente: %s", e)
        return f"Erro interno: {e}", "", "", ""

    # Resposta
    resposta = result.get("final_response", "Sem resposta.")

    # Confiança
    conf = result.get("confidence", "")
    conf_labels = {"alta": "🟢 Alta", "media": "🟡 Média", "baixa": "🔴 Baixa"}
    confianca = conf_labels.get(conf, conf)

    # Fontes
    sources = result.get("sources", [])
    fontes = "\n".join(f"• {s}" for s in sources) if sources else "Nenhuma fonte citada."

    # Audit log
    audit = result.get("audit_log", [])
    audit_str = json.dumps(audit, indent=2, ensure_ascii=False, default=str)

    return resposta, confianca, fontes, audit_str


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
    """Constrói e retorna a interface Gradio."""
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
                patient_input = gr.Textbox(
                    label="Paciente (opcional)",
                    placeholder="Nome ou ID do paciente",
                    lines=1,
                )
                submit_btn = gr.Button("Consultar", variant="primary", size="lg")

            with gr.Column(scale=1):
                confianca_output = gr.Textbox(label="Confiança", interactive=False)
                fontes_output = gr.Textbox(label="Fontes consultadas", lines=6, interactive=False)

        resposta_output = gr.Textbox(
            label="Resposta do Assistente",
            lines=15,
            interactive=False,
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

        submit_btn.click(
            fn=consultar,
            inputs=[query_input, patient_input],
            outputs=[resposta_output, confianca_output, fontes_output, audit_output],
        )
        query_input.submit(
            fn=consultar,
            inputs=[query_input, patient_input],
            outputs=[resposta_output, confianca_output, fontes_output, audit_output],
        )

    return demo


if __name__ == "__main__":
    demo = build_interface()
    demo.launch(server_name="0.0.0.0", server_port=7860, theme=gr.themes.Soft(primary_hue="red"))
