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


def protocolo_agent(state: MedicalAssistantState) -> dict:
    """Busca protocolos clínicos relevantes no ChromaDB."""
    query = state["query"]
    entities = state.get("entities", {})

    # Enriquecer query com entidades extraídas
    search_query = query
    condicao = entities.get("condicao")
    if condicao:
        search_query = f"{query} {condicao}"

    logger.info("Protocolo: buscando '%s'", search_query[:80])

    try:
        retriever = _get_retriever()
        results = retriever.search(search_query, n_results=5)

        protocols = []
        for r in results:
            protocols.append({
                "content": r["content"],
                "source": r["metadata"].get("source", "Desconhecido"),
                "section": r["metadata"].get("section", ""),
                "doc_type": r["metadata"].get("doc_type", ""),
                "distance": r["distance"],
            })

        logger.info("Protocolo: %d resultados encontrados", len(protocols))

    except Exception as e:
        logger.error("Protocolo: erro na busca - %s", e)
        protocols = []

    audit_entry = {
        "agent": "protocolo",
        "timestamp": datetime.now().isoformat(),
        "search_query": search_query[:200],
        "results_count": len(protocols),
        "sources": [p["source"] for p in protocols],
    }

    return {
        "protocols": protocols,
        "audit_log": state.get("audit_log", []) + [audit_entry],
    }
