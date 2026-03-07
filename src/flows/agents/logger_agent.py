"""Agente Logger (Auditoria) - Consolida e persiste log da interação."""

import json
import logging
from datetime import datetime
from pathlib import Path

from src.flows.state import MedicalAssistantState

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
LOGS_DIR = PROJECT_ROOT / "logs"


def _build_audit_record(state: MedicalAssistantState) -> dict:
    """Constrói registro completo de auditoria."""
    return {
        "timestamp": datetime.now().isoformat(),
        "session": {
            "query": state.get("query", ""),
            "patient_id": state.get("patient_id"),
        },
        "triagem": {
            "query_type": state.get("query_type", ""),
            "entities": state.get("entities", {}),
        },
        "context": {
            "protocols_count": len(state.get("protocols", [])),
            "protocols_sources": [
                p.get("source", "") for p in state.get("protocols", [])
            ],
            "patient_data_available": state.get("patient_data") is not None,
        },
        "response": {
            "draft_length": len(state.get("draft_response", "")),
            "final_length": len(state.get("final_response", "")),
            "confidence": state.get("confidence", ""),
            "sources": state.get("sources", []),
            "warnings": state.get("warnings", []),
        },
        "guardrails": {
            "result": state.get("guardrail_result", ""),
            "feedback": state.get("guardrail_feedback"),
            "retry_count": state.get("retry_count", 0),
        },
        "agent_trace": state.get("audit_log", []),
    }


def _persist_log(record: dict) -> None:
    """Persiste registro em arquivo JSON."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # Arquivo de log diário
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_file = LOGS_DIR / f"audit_{date_str}.jsonl"

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")

    logger.info("Logger: registro persistido em %s", log_file.name)


def logger_agent(state: MedicalAssistantState) -> dict:
    """Consolida e persiste log completo da interação."""
    query_type = state.get("query_type", "")
    logger.info("Logger: consolidando auditoria (query_type=%s)", query_type)

    # Se fora_de_escopo, gerar resposta padrão
    final_response = state.get("final_response", "")
    if query_type == "fora_de_escopo" and not final_response:
        final_response = (
            "Desculpe, esta pergunta está fora do escopo do assistente médico. "
            "Posso ajudar com consultas sobre protocolos clínicos, dados de "
            "pacientes, tratamentos e condutas médicas."
        )

    # Construir registro de auditoria
    audit_record = _build_audit_record(state)

    # Persistir log
    try:
        _persist_log(audit_record)
    except Exception as e:
        logger.error("Logger: falha ao persistir log - %s", e)

    audit_entry = {
        "agent": "logger",
        "timestamp": datetime.now().isoformat(),
        "status": "persisted",
    }

    result = {
        "audit_log": state.get("audit_log", []) + [audit_entry],
    }

    # Atualizar final_response se fora de escopo
    if query_type == "fora_de_escopo" and not state.get("final_response"):
        result["final_response"] = final_response

    return result
