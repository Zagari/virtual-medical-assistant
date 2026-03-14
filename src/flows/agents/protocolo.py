"""Agente de Protocolo (RAG ChromaDB) - Busca semântica em protocolos clínicos."""

import logging
from datetime import datetime
from pathlib import Path

from src.flows.state import MedicalAssistantState

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Stop words em português para limpeza de queries de busca semântica
_STOP_WORDS = frozenset(
    "a o e de do da dos das em no na nos nas um uma uns umas "
    "é está se que para por com não mais há foi ser ter como ao "
    "seu sua ele ela já também muito os as meu minha pelo pela "
    "lhe nos me te si nós vos ao aos à às este esta esse essa "
    "aquele aquela isto isso aquilo quem qual quanto quando onde "
    "estou estava esteve estão sendo sido será foram seria "
    "queixando relatando apresentando paciente sr sra dona seu".split()
)


def _get_retriever():
    """Inicializa o ProtocolRetriever (lazy loading)."""
    from src.assistant.rag import ProtocolRetriever

    chroma_dir = PROJECT_ROOT / "chroma_db"
    return ProtocolRetriever(persist_directory=str(chroma_dir))


def _rank_by_patient_relevance(
    protocols: list[dict], comorbidades: list[str]
) -> list[dict]:
    """Ranqueia protocolos por relevância às comorbidades do paciente."""
    if not comorbidades:
        return protocols

    # Normalizar termos de comorbidades para busca
    termos = []
    for c in comorbidades:
        termos.extend(c.lower().split())
    # Remover palavras genéricas
    stop = {"de", "do", "da", "dos", "das", "e", "ou", "com", "sem", "tipo", "não"}
    termos = [t for t in termos if t not in stop and len(t) > 2]

    diretos = []
    complementares = []

    for p in protocols:
        texto = f"{p['source']} {p['section']} {p['content']}".lower()
        matches = sum(1 for t in termos if t in texto)
        p_copy = dict(p)
        if matches > 0:
            p_copy["relevance"] = "direta"
            p_copy["relevance_score"] = matches
            diretos.append(p_copy)
        else:
            p_copy["relevance"] = "complementar"
            p_copy["relevance_score"] = 0
            complementares.append(p_copy)

    # Ordenar diretos por score (mais matches primeiro), depois por distância
    diretos.sort(key=lambda x: (-x["relevance_score"], x["distance"]))
    complementares.sort(key=lambda x: x["distance"])

    return diretos + complementares


def protocolo_agent(state: MedicalAssistantState) -> dict:
    """Busca protocolos clínicos relevantes no ChromaDB."""
    query = state["query"]
    entities = state.get("entities", {})
    patient_data = state.get("patient_data")

    # Extrair comorbidades do paciente (se disponíveis)
    comorbidades = []
    if patient_data:
        paciente = patient_data.get("paciente", {})
        comorbidades = paciente.get("comorbidades", [])

    # Construir query base otimizada para busca semântica:
    # remover nome do paciente e stop words para focar nos termos clínicos
    base_query = query
    patient_id = state.get("patient_id")
    if patient_id:
        base_query = base_query.replace(patient_id, "")
    # Remover stop words para melhorar a busca semântica
    words = base_query.split()
    clean_words = [w for w in words if w.lower().strip(".,;:!?") not in _STOP_WORDS and len(w) > 1]
    base_query = " ".join(clean_words) if clean_words else query
    condicao = entities.get("condicao")
    if condicao:
        base_query = f"{base_query} {condicao}"

    search_queries = []

    try:
        retriever = _get_retriever()

        if comorbidades:
            # Busca híbrida: query base (sintomas) + por comorbidade
            logger.info(
                "Protocolo: busca híbrida — query + comorbidades (%s)",
                ", ".join(comorbidades),
            )
            # 1. Busca pela query base (captura protocolos de emergência por sintomas)
            base_results = retriever.search(base_query, n_results=3)
            seen_ids = {r["id"] for r in base_results}
            results = list(base_results)

            # 2. Busca por comorbidade (cobertura equilibrada das condições do paciente)
            for comorbidade in comorbidades:
                focused_query = f"{base_query} {comorbidade}"
                comorb_results = retriever.search(focused_query, n_results=3)
                for r in comorb_results:
                    if r["id"] not in seen_ids:
                        seen_ids.add(r["id"])
                        results.append(r)

            search_queries = [base_query] + [f"{base_query} {c}" for c in comorbidades]
        else:
            # Busca ampla (sem dados do paciente ou sem comorbidades)
            logger.info("Protocolo: busca ampla '%s'", base_query[:80])
            results = retriever.search(base_query, n_results=5)
            search_queries = [base_query]

        protocols = []
        for r in results:
            protocols.append({
                "content": r["content"],
                "source": r["metadata"].get("source", "Desconhecido"),
                "section": r["metadata"].get("section", ""),
                "doc_type": r["metadata"].get("doc_type", ""),
                "distance": r["distance"],
            })

        # Ranking por relevância ao paciente
        if comorbidades:
            protocols = _rank_by_patient_relevance(protocols, comorbidades)
            n_diretos = sum(1 for p in protocols if p.get("relevance") == "direta")
            logger.info(
                "Protocolo: %d resultados (%d diretos, %d complementares)",
                len(protocols), n_diretos, len(protocols) - n_diretos,
            )
        else:
            for p in protocols:
                p["relevance"] = "complementar"
                p["relevance_score"] = 0
            logger.info("Protocolo: %d resultados (busca ampla)", len(protocols))

    except Exception as e:
        logger.error("Protocolo: erro na busca - %s", e)
        protocols = []

    # Gerar report amigável para interface
    if protocols:
        report_parts = [f"**{len(protocols)} protocolo(s) encontrado(s):**\n"]

        diretos = [p for p in protocols if p.get("relevance") == "direta"]
        complementares = [p for p in protocols if p.get("relevance") != "direta"]

        if diretos:
            report_parts.append("**📋 Relevância Direta:**")
            for p in diretos[:3]:
                source = p.get("source", "N/A")
                section = p.get("section", "")
                distance = p.get("distance", 0)
                section_info = f" | {section}" if section else ""
                report_parts.append(f"  • {source}{section_info} (dist: {distance:.2f})")

        if complementares:
            report_parts.append("\n**📎 Complementares:**")
            for p in complementares[:2]:
                source = p.get("source", "N/A")
                distance = p.get("distance", 0)
                report_parts.append(f"  • {source} (dist: {distance:.2f})")

        protocolo_report = "\n".join(report_parts)
    else:
        protocolo_report = "⚠️ Nenhum protocolo encontrado para esta consulta."

    audit_entry = {
        "agent": "protocolo",
        "timestamp": datetime.now().isoformat(),
        "search_queries": [q[:100] for q in search_queries],
        "results_count": len(protocols),
        "sources": [p["source"] for p in protocols],
        "comorbidades_used": comorbidades,
    }

    current_reports = state.get("agent_reports", {})
    current_reports["protocolo"] = protocolo_report

    return {
        "protocols": protocols,
        "agent_reports": current_reports,
        "audit_log": state.get("audit_log", []) + [audit_entry],
    }
