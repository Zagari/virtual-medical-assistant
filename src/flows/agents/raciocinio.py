"""Agente de Raciocínio (Mistral 7B Fine-Tuned) - Sintetiza resposta clínica."""

import logging
from datetime import datetime

from src.flows.state import MedicalAssistantState

logger = logging.getLogger(__name__)

RACIOCINIO_PROMPT = """Você é um assistente médico especializado. Com base no contexto fornecido, responda à pergunta do médico de forma clara, precisa e fundamentada.

PERGUNTA DO MÉDICO: {query}

{context_section}

{feedback_section}

INSTRUÇÕES:
1. Responda em português, de forma técnica mas acessível
2. Fundamente sua resposta nos protocolos e dados fornecidos
3. NUNCA prescreva medicamentos diretamente — sempre sugira e indique validação médica
4. Se não tiver informação suficiente, diga claramente o que falta
5. Inclua ressalvas quando apropriado

RESPOSTA:"""


def _format_protocols(protocols: list[dict]) -> str:
    """Formata protocolos para inclusão no prompt."""
    if not protocols:
        return ""

    parts = ["PROTOCOLOS CLÍNICOS RELEVANTES:"]
    for i, p in enumerate(protocols, 1):
        source = p.get("source", "Desconhecido")
        section = p.get("section", "")
        content = p.get("content", "")
        header = f"\n[{i}] Fonte: {source}"
        if section:
            header += f" | Seção: {section}"
        parts.append(f"{header}\n{content}")

    return "\n".join(parts)


def _format_patient_data(patient_data: dict | None) -> str:
    """Formata dados do paciente para inclusão no prompt."""
    if not patient_data:
        return ""

    parts = ["DADOS DO PACIENTE:"]
    p = patient_data.get("paciente", {})
    if p:
        nome = p.get("nome", "N/A")
        sexo = p.get("sexo", "N/A")
        nascimento = p.get("data_nascimento", "N/A")
        comorbidades = p.get("comorbidades", [])
        alergias = p.get("alergias", [])
        medicamentos = p.get("medicamentos_uso", [])

        parts.append(f"Nome: {nome} | Sexo: {sexo} | Nascimento: {nascimento}")
        if comorbidades:
            parts.append(f"Comorbidades: {', '.join(comorbidades)}")
        if alergias:
            parts.append(f"Alergias: {', '.join(alergias)}")
        if medicamentos:
            parts.append(f"Medicamentos em uso: {', '.join(medicamentos)}")

    exames = patient_data.get("exames", [])
    if exames:
        parts.append("\nÚltimos exames:")
        for e in exames[:5]:
            parts.append(f"  - {e.get('tipo', 'N/A')} ({e.get('data', 'N/A')}): {e.get('interpretacao', 'N/A')}")

    prontuarios = patient_data.get("prontuarios", [])
    if prontuarios:
        parts.append("\nÚltimos prontuários:")
        for pr in prontuarios[:3]:
            parts.append(f"  - {pr.get('data', 'N/A')}: {pr.get('diagnostico_texto', 'N/A')}")

    return "\n".join(parts)


def raciocinio_agent(state: MedicalAssistantState) -> dict:
    """Sintetiza resposta clínica usando LLM com contexto."""
    query = state["query"]
    protocols = state.get("protocols", [])
    patient_data = state.get("patient_data")
    retry_count = state.get("retry_count", 0)
    guardrail_feedback = state.get("guardrail_feedback")

    # Montar contexto
    context_parts = []
    protocols_text = _format_protocols(protocols)
    if protocols_text:
        context_parts.append(protocols_text)
    patient_text = _format_patient_data(patient_data)
    if patient_text:
        context_parts.append(patient_text)

    context_section = "\n\n".join(context_parts) if context_parts else "Nenhum contexto adicional disponível."

    # Se é retry, incluir feedback do guardrails
    feedback_section = ""
    if guardrail_feedback and retry_count > 0:
        feedback_section = (
            f"ATENÇÃO - SUA RESPOSTA ANTERIOR FOI REPROVADA PELO GUARDRAILS:\n"
            f"Motivo: {guardrail_feedback}\n"
            f"Corrija os problemas apontados nesta nova resposta."
        )

    prompt = RACIOCINIO_PROMPT.format(
        query=query,
        context_section=context_section,
        feedback_section=feedback_section,
    )

    logger.info("Raciocínio: gerando resposta (retry=%d)", retry_count)

    # Usar LLM
    llm = state.get("_llm")
    if llm is not None:
        try:
            draft_response = llm(prompt)
        except Exception as e:
            logger.error("Raciocínio: LLM falhou - %s", e)
            draft_response = _fallback_response(query, protocols, patient_data)
    else:
        draft_response = _fallback_response(query, protocols, patient_data)

    audit_entry = {
        "agent": "raciocinio",
        "timestamp": datetime.now().isoformat(),
        "retry_count": retry_count,
        "had_protocols": len(protocols) > 0,
        "had_patient_data": patient_data is not None,
        "response_length": len(draft_response),
    }

    return {
        "draft_response": draft_response,
        "audit_log": state.get("audit_log", []) + [audit_entry],
    }


def _fallback_response(
    query: str, protocols: list[dict], patient_data: dict | None
) -> str:
    """Resposta baseada em template quando LLM não está disponível."""
    parts = [f"Com base na consulta sobre: {query}\n"]

    if protocols:
        parts.append("De acordo com os protocolos clínicos consultados:")
        for p in protocols[:3]:
            source = p.get("source", "Protocolo")
            content = p.get("content", "")[:300]
            parts.append(f"\n[{source}]: {content}")

    if patient_data:
        p = patient_data.get("paciente", {})
        if p:
            parts.append(f"\nDados do paciente {p.get('nome', 'N/A')}:")
            comorbidades = p.get("comorbidades", [])
            if comorbidades:
                parts.append(f"Comorbidades: {', '.join(comorbidades)}")

    parts.append(
        "\n\n⚠️ IMPORTANTE: Esta resposta deve ser validada por um "
        "profissional de saúde antes de qualquer decisão clínica."
    )

    return "\n".join(parts)
