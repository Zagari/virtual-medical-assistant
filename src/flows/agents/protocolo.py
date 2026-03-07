"""Agente de Protocolo (RAG ChromaDB) - Busca semântica em protocolos clínicos."""

import logging
from datetime import datetime
from pathlib import Path

from src.flows.state import MedicalAssistantState

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


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


def _search_per_comorbidity(
    retriever, query: str, comorbidades: list[str], n_per: int = 3
) -> list[dict]:
    """Busca protocolos por comorbidade para cobertura equilibrada.

    Faz uma busca focada por comorbidade (ex: "exames hipertensão"),
    deduplica por ID e retorna os melhores resultados de cada uma.
    """
    seen_ids = set()
    all_results = []

    for comorbidade in comorbidades:
        focused_query = f"{query} {comorbidade}"
        results = retriever.search(focused_query, n_results=n_per)
        for r in results:
            rid = r["id"]
            if rid not in seen_ids:
                seen_ids.add(rid)
                all_results.append(r)

    return all_results


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

    # Enriquecer query base com entidade de condição (se extraída pela triagem)
    base_query = query
    condicao = entities.get("condicao")
    if condicao:
        base_query = f"{query} {condicao}"

    search_queries = []

    try:
        retriever = _get_retriever()

        if comorbidades:
            # Busca focada: uma busca por comorbidade para cobertura equilibrada
            logger.info(
                "Protocolo: busca por comorbidade — %s",
                ", ".join(comorbidades),
            )
            results = _search_per_comorbidity(
                retriever, base_query, comorbidades, n_per=3
            )
            search_queries = [f"{base_query} {c}" for c in comorbidades]
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

    audit_entry = {
        "agent": "protocolo",
        "timestamp": datetime.now().isoformat(),
        "search_queries": [q[:100] for q in search_queries],
        "results_count": len(protocols),
        "sources": [p["source"] for p in protocols],
        "comorbidades_used": comorbidades,
    }

    return {
        "protocols": protocols,
        "audit_log": state.get("audit_log", []) + [audit_entry],
    }
