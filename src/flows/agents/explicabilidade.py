"""Agente de Explicabilidade - Adiciona citações, confiança e formata resposta."""

import logging
from datetime import datetime

from src.flows.state import MedicalAssistantState

logger = logging.getLogger(__name__)

DISCLAIMER = (
    "⚠️ Esta resposta é uma sugestão baseada em protocolos clínicos e dados "
    "disponíveis. Toda decisão clínica deve ser validada pelo médico responsável."
)


def _extract_sources(
    protocols: list[dict], patient_data: dict | None
) -> tuple[list[str], list[str]]:
    """Extrai fontes citáveis separadas por relevância.

    Returns:
        Tupla (fontes_diretas, fontes_complementares).
    """
    diretas = []
    complementares = []
    seen = set()

    for p in protocols:
        source = p.get("source", "")
        section = p.get("section", "")
        citation = f"[{source}]" if source else ""
        if section:
            citation = f"[{source}, Seção: {section}]"
        if citation and citation not in seen:
            seen.add(citation)
            if p.get("relevance") == "direta":
                diretas.append(citation)
            else:
                complementares.append(citation)

    # Fontes de dados do paciente são sempre diretas
    if patient_data and patient_data.get("paciente"):
        nome = patient_data["paciente"].get("nome", "N/A")
        diretas.append(f"[Prontuário: {nome}]")

        exames = patient_data.get("exames", [])
        for e in exames[:3]:
            tipo = e.get("tipo", "")
            data = e.get("data", "")
            if tipo:
                diretas.append(f"[Exame: {tipo}, Data: {data}]")

    return diretas, complementares


def _assess_confidence(
    protocols: list[dict],
    patient_data: dict | None,
    guardrail_result: str,
    retry_count: int,
) -> str:
    """Avalia nível de confiança da resposta."""
    score = 0

    # Protocolos encontrados aumentam confiança
    if protocols:
        if len(protocols) >= 3:
            score += 3
        elif len(protocols) >= 1:
            score += 2

        # Distância média dos resultados (menor = mais relevante)
        avg_distance = sum(p.get("distance", 1.0) for p in protocols) / len(protocols)
        if avg_distance < 0.5:
            score += 2
        elif avg_distance < 1.0:
            score += 1

    # Dados de paciente disponíveis
    if patient_data and patient_data.get("paciente"):
        score += 2

    # Penalizar retries
    if retry_count > 0:
        score -= retry_count

    if score >= 5:
        return "alta"
    elif score >= 3:
        return "media"
    return "baixa"


def _generate_warnings(
    confidence: str,
    protocols: list[dict],
    patient_data: dict | None,
    retry_count: int,
) -> list[str]:
    """Gera advertências relevantes."""
    warnings = []

    if confidence == "baixa":
        warnings.append("Confiança baixa: poucos dados disponíveis para fundamentar a resposta.")

    if not protocols:
        warnings.append("Nenhum protocolo clínico foi encontrado para esta consulta.")

    if patient_data is None:
        # Só avisar se a query parecia precisar de dados do paciente
        pass

    if retry_count > 0:
        warnings.append(
            f"Resposta foi refinada {retry_count}x pelo guardrails de segurança."
        )

    return warnings


def explicabilidade_agent(state: MedicalAssistantState) -> dict:
    """Adiciona citações, confiança e formata resposta final."""
    draft_response = state.get("draft_response", "")
    protocols = state.get("protocols", [])
    patient_data = state.get("patient_data")
    guardrail_result = state.get("guardrail_result", "aprovado")
    retry_count = state.get("retry_count", 0)

    logger.info("Explicabilidade: formatando resposta final")

    # Extrair fontes (separadas por relevância)
    fontes_diretas, fontes_complementares = _extract_sources(protocols, patient_data)
    all_sources = fontes_diretas + fontes_complementares

    # Avaliar confiança
    confidence = _assess_confidence(
        protocols, patient_data, guardrail_result, retry_count
    )

    # Gerar advertências
    warnings = _generate_warnings(
        confidence, protocols, patient_data, retry_count
    )

    # Montar resposta final
    final_parts = [draft_response]

    if fontes_diretas:
        final_parts.append("\n\n📋 **Fontes consultadas:**")
        for s in fontes_diretas:
            final_parts.append(f"  • {s}")

    if fontes_complementares:
        final_parts.append("\n📎 **Fontes complementares:**")
        for s in fontes_complementares:
            final_parts.append(f"  • {s}")

    confidence_labels = {
        "alta": "🟢 Alta",
        "media": "🟡 Média",
        "baixa": "🔴 Baixa",
    }
    final_parts.append(
        f"\n📊 **Confiança:** {confidence_labels.get(confidence, confidence)}"
    )

    if warnings:
        final_parts.append("\n⚠️ **Advertências:**")
        for w in warnings:
            final_parts.append(f"  • {w}")

    final_parts.append(f"\n{DISCLAIMER}")

    final_response = "\n".join(final_parts)

    logger.info(
        "Explicabilidade: confiança=%s, diretas=%d, complementares=%d, warnings=%d",
        confidence, len(fontes_diretas), len(fontes_complementares), len(warnings),
    )

    # Gerar report amigável para interface
    report_parts = [
        f"**Confiança:** {confidence_labels.get(confidence, confidence)}",
        f"**Fontes diretas:** {len(fontes_diretas)}",
        f"**Fontes complementares:** {len(fontes_complementares)}",
    ]

    if fontes_diretas:
        report_parts.append("\n**Fontes citadas:**")
        for s in fontes_diretas[:4]:
            report_parts.append(f"  • {s}")

    if warnings:
        report_parts.append(f"\n**Advertências:** {len(warnings)}")
        for w in warnings:
            report_parts.append(f"  ⚠️ {w}")

    explicabilidade_report = "\n".join(report_parts)

    audit_entry = {
        "agent": "explicabilidade",
        "timestamp": datetime.now().isoformat(),
        "confidence": confidence,
        "sources_direct": len(fontes_diretas),
        "sources_complementary": len(fontes_complementares),
        "warnings": warnings,
    }

    current_reports = state.get("agent_reports", {})
    current_reports["explicabilidade"] = explicabilidade_report

    return {
        "final_response": final_response,
        "sources": all_sources,
        "confidence": confidence,
        "warnings": warnings,
        "agent_reports": current_reports,
        "audit_log": state.get("audit_log", []) + [audit_entry],
    }
