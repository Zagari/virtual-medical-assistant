"""Agente de Triagem (Router) - Classifica a query e extrai entidades."""

import json
import logging
import re
from datetime import datetime

from src.flows.state import MedicalAssistantState

logger = logging.getLogger(__name__)

TRIAGEM_PROMPT = """Você é um agente de triagem médica. Analise a pergunta do médico e classifique-a.

PERGUNTA: {query}

Responda EXATAMENTE neste formato JSON (sem markdown, sem ```):
{{
    "query_type": "<protocolo|paciente|ambos|fora_de_escopo>",
    "entities": {{
        "paciente_nome": "<nome do paciente ou null>",
        "condicao": "<condição médica mencionada ou null>",
        "medicamento": "<medicamento mencionado ou null>",
        "exame": "<exame mencionado ou null>"
    }}
}}

REGRAS DE CLASSIFICAÇÃO:
- "protocolo": pergunta sobre protocolo clínico, tratamento, diagnóstico genérico (sem mencionar paciente específico)
- "paciente": pergunta sobre dados de um paciente específico (exames, prontuário, medicamentos)
- "ambos": pergunta que envolve protocolo E dados de um paciente específico
- "fora_de_escopo": pergunta não relacionada à medicina ou ao hospital
"""


def _parse_triagem_response(response_text: str) -> dict:
    """Extrai JSON da resposta da LLM."""
    # Tentar extrair JSON de bloco de código
    json_match = re.search(r'\{[\s\S]*\}', response_text)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

    # Fallback: classificação por heurística
    return {
        "query_type": "protocolo",
        "entities": {
            "paciente_nome": None,
            "condicao": None,
            "medicamento": None,
            "exame": None,
        },
    }


def _classify_by_heuristic(query: str) -> dict:
    """Classificação por heurística quando LLM não está disponível."""
    query_lower = query.lower()

    has_patient = any(
        kw in query_lower
        for kw in ["paciente", "sr.", "sra.", "dona", "seu"]
    )
    has_protocol = any(
        kw in query_lower
        for kw in [
            "protocolo", "tratamento", "diagnóstico", "conduta",
            "diretriz", "sintomas", "medicamento", "dose",
            "exame", "indicação", "contraindicação",
        ]
    )
    has_symptoms = any(
        kw in query_lower
        for kw in [
            "dor", "dor no peito", "palpitação", "palpitações",
            "falta de ar", "dispneia", "náusea", "vômito",
            "tontura", "desmaio", "sangramento", "convulsão",
            "confusão mental", "cefaleia", "edema", "tosse",
            "febre", "calafrio", "sudorese", "síncope",
            "queixando", "queixa", "apresentando", "relata",
        ]
    )
    is_medical = has_patient or has_protocol or has_symptoms or any(
        kw in query_lower
        for kw in [
            "pressão", "diabetes", "asma", "dpoc", "infarto",
            "avc", "hipertensão", "glicemia",
        ]
    )

    if has_patient and (has_protocol or has_symptoms):
        query_type = "ambos"
    elif has_patient:
        query_type = "paciente"
    elif has_protocol or is_medical:
        query_type = "protocolo"
    else:
        query_type = "fora_de_escopo"

    return {
        "query_type": query_type,
        "entities": {
            "paciente_nome": None,
            "condicao": None,
            "medicamento": None,
            "exame": None,
        },
    }


def triagem_agent(state: MedicalAssistantState) -> dict:
    """Classifica a query e extrai entidades."""
    query = state["query"]
    logger.info("Triagem: classificando query: %s", query[:80])

    # Tentar usar LLM para classificação
    llm = state.get("_llm")
    if llm is not None:
        try:
            prompt = TRIAGEM_PROMPT.format(query=query)
            response = llm(prompt)
            result = _parse_triagem_response(response)
        except Exception as e:
            logger.warning("Triagem: LLM falhou (%s), usando heurística", e)
            result = _classify_by_heuristic(query)
    else:
        result = _classify_by_heuristic(query)

    query_type = result.get("query_type", "protocolo")
    entities = result.get("entities", {})

    # Propagar patient_id para paciente_nome se não foi extraído da query
    # (quando o paciente é selecionado via dropdown, não aparece no texto)
    if state.get("patient_id") and not entities.get("paciente_nome"):
        entities["paciente_nome"] = state.get("patient_id")

    # Se patient_id foi fornecido na entrada, ajustar classificação
    if state.get("patient_id"):
        if query_type == "protocolo":
            query_type = "ambos"
        elif query_type == "paciente":
            # Verificar se a query contém conteúdo clínico que justifique busca de protocolos
            q = state["query"].lower()
            has_clinical_content = any(
                kw in q
                for kw in [
                    "dor", "febre", "palpitação", "palpitações", "dispneia",
                    "falta de ar", "sangramento", "convulsão", "tontura",
                    "náusea", "vômito", "edema", "tosse", "queixa",
                    "queixando", "apresentando", "relata", "sintoma",
                    "protocolo", "tratamento", "conduta", "diagnóstico",
                    "pressão", "diabetes", "infarto", "avc", "sepse",
                ]
            )
            if has_clinical_content:
                query_type = "ambos"

    logger.info("Triagem: query_type=%s, entities=%s", query_type, entities)

    # Gerar report amigável para interface
    query_type_labels = {
        "protocolo": "📋 Consulta de Protocolo",
        "paciente": "👤 Consulta de Paciente",
        "ambos": "📋👤 Protocolo + Paciente",
        "fora_de_escopo": "❌ Fora de Escopo",
    }
    triagem_report_parts = [
        f"**Tipo:** {query_type_labels.get(query_type, query_type)}",
    ]
    if entities.get("paciente_nome"):
        triagem_report_parts.append(f"**Paciente:** {entities['paciente_nome']}")
    if entities.get("condicao"):
        triagem_report_parts.append(f"**Condição:** {entities['condicao']}")
    if entities.get("medicamento"):
        triagem_report_parts.append(f"**Medicamento:** {entities['medicamento']}")
    if entities.get("exame"):
        triagem_report_parts.append(f"**Exame:** {entities['exame']}")

    triagem_report = "\n".join(triagem_report_parts)

    audit_entry = {
        "agent": "triagem",
        "timestamp": datetime.now().isoformat(),
        "query_type": query_type,
        "entities": entities,
    }

    current_reports = state.get("agent_reports", {})
    current_reports["triagem"] = triagem_report

    return {
        "query_type": query_type,
        "entities": entities,
        "agent_reports": current_reports,
        "audit_log": state.get("audit_log", []) + [audit_entry],
    }
