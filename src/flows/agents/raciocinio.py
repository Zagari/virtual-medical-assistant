"""Agente de Raciocínio (Mistral 7B Fine-Tuned) - Sintetiza resposta clínica."""

import logging
import re
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
6. Seja conciso: resuma os pontos essenciais em no máximo 300 palavras. Não repita trechos do contexto — sintetize.

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


def _truncate_at_sentence(text: str, max_len: int = 400) -> str:
    """Trunca texto no final da última sentença completa dentro do limite."""
    if len(text) <= max_len:
        return text
    truncated = text[:max_len]
    # Procurar último ponto final seguido de espaço ou newline
    for sep in (". ", ".\n", "\n\n"):
        pos = truncated.rfind(sep)
        if pos > max_len // 2:
            return truncated[: pos + 1]
    return truncated.rstrip() + "..."


def _clean_chunk_content(text: str) -> str:
    """Remove artefatos de PDF e pula prefixo garbled de chunks com overlap."""
    # 1. Remover linhas de cabeçalho de página do PDF
    text = re.sub(r"^\s*LINHA DE CUIDADO\s*[–\-].+$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()

    if not text:
        return text

    # 2. Verificar se começa "limpo" (maiúscula, header, bullet ou número)
    first_char = text[0]
    starts_clean = first_char.isupper() or first_char in "#*-•" or first_char.isdigit()

    if not starts_clean:
        # Chunk começa mid-sentence (overlap do chunking) — pular até próximo início limpo
        # Tentar: sentence boundary → paragraph break → newline com maiúscula
        for sep in (". ", ".\n"):
            pos = text[:200].find(sep)
            if pos != -1:
                rest = text[pos + len(sep) :].lstrip()
                if rest:
                    return rest
        # Tentar paragraph break
        pos = text[:200].find("\n\n")
        if pos != -1:
            rest = text[pos:].lstrip()
            if rest:
                return rest
    return text


def _fallback_response(
    query: str, protocols: list[dict], patient_data: dict | None
) -> str:
    """Resposta baseada em template quando LLM não está disponível."""
    parts = [f"Com base na consulta sobre: {query}\n"]

    # Dados do paciente (prioridade quando disponíveis)
    if patient_data:
        p = patient_data.get("paciente", {})
        if p:
            parts.append(f"**Dados do paciente {p.get('nome', 'N/A')}:**")
            sexo = p.get("sexo", "")
            nascimento = p.get("data_nascimento", "")
            if sexo or nascimento:
                parts.append(f"Sexo: {sexo} | Nascimento: {nascimento}")
            comorbidades = p.get("comorbidades", [])
            if comorbidades:
                parts.append(f"Comorbidades: {', '.join(comorbidades)}")
            alergias = p.get("alergias", [])
            if alergias:
                parts.append(f"Alergias: {', '.join(alergias)}")
            medicamentos = p.get("medicamentos_uso", [])
            if medicamentos:
                parts.append(f"Medicamentos em uso: {', '.join(medicamentos)}")

        exames = patient_data.get("exames", [])
        if exames:
            parts.append("\n**Últimos exames:**")
            for e in exames[:5]:
                tipo = e.get("tipo", "N/A")
                data = e.get("data", "N/A")
                interp = e.get("interpretacao", e.get("resultado", ""))
                parts.append(f"  - {tipo} ({data}): {interp}")

        prontuarios = patient_data.get("prontuarios", [])
        if prontuarios:
            parts.append("\n**Últimos prontuários:**")
            for pr in prontuarios[:3]:
                data = pr.get("data", "N/A")
                diag = pr.get("diagnostico_texto", pr.get("diagnostico_cid", "N/A"))
                parts.append(f"  - {data}: {diag}")

        receitas = patient_data.get("receitas", [])
        if receitas:
            parts.append("\n**Últimas receitas:**")
            for r in receitas[:3]:
                data = r.get("data", "N/A")
                condicao = r.get("condicao", "")
                meds = r.get("medicamentos", r.get("medicamento", ""))
                line = f"  - {data}"
                if condicao:
                    line += f" ({condicao})"
                if meds:
                    line += f": {meds}"
                parts.append(line)

    # Protocolos clínicos (limpos, deduplica por fonte)
    if protocols:
        parts.append("\n**Protocolos clínicos consultados:**")
        parts.append("_(Trechos extraídos automaticamente — sem síntese por LLM)_\n")
        has_diretos = any(p.get("relevance") == "direta" for p in protocols)
        seen_sources = set()
        shown = 0
        for p in protocols:
            source = p.get("source", "Protocolo")
            section = p.get("section", "")
            source_key = f"{source}|{section}"
            if source_key in seen_sources:
                continue
            seen_sources.add(source_key)

            header = f"[{source}]"
            if section:
                header += f" — {section}"
            relevance = p.get("relevance", "")

            # Só omitir conteúdo de complementares quando há protocolos diretos
            if relevance == "complementar" and has_diretos:
                parts.append(f"\n{header} _(complementar)_")
            else:
                raw = p.get("content", "")
                cleaned = _clean_chunk_content(raw)
                excerpt = _truncate_at_sentence(cleaned, max_len=200)
                if excerpt and len(excerpt) > 40:
                    parts.append(f"\n{header}\n{excerpt}")
                else:
                    parts.append(f"\n{header}")

            shown += 1
            if shown >= 5:
                break

    parts.append(
        "\n\n⚠️ IMPORTANTE: Esta resposta deve ser validada por um "
        "profissional de saúde antes de qualquer decisão clínica."
    )

    return "\n".join(parts)
