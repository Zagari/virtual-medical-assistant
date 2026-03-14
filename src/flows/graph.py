"""Definição do grafo multi-agente LangGraph para o Assistente Médico."""

import logging

from langgraph.graph import END, StateGraph

from src.flows.agents import (
    explicabilidade_agent,
    guardrails_agent,
    logger_agent,
    paciente_data_agent,
    protocolo_agent,
    raciocinio_agent,
    triagem_agent,
)
from src.flows.state import MedicalAssistantState

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Funções de roteamento condicional
# ---------------------------------------------------------------------------

def route_after_triagem(state: MedicalAssistantState) -> str:
    """Rota após triagem baseada no tipo de query."""
    query_type = state.get("query_type", "fora_de_escopo")

    if query_type == "protocolo":
        return "protocolo"
    elif query_type in ("paciente", "ambos"):
        return "paciente_data"
    else:
        return "logger"


def route_after_paciente_data(state: MedicalAssistantState) -> str:
    """Rota após busca de dados do paciente."""
    query_type = state.get("query_type", "paciente")

    if query_type == "ambos":
        return "protocolo"
    return "raciocinio"


def route_after_guardrails(state: MedicalAssistantState) -> str:
    """Rota após validação dos guardrails."""
    guardrail_result = state.get("guardrail_result", "aprovado")
    retry_count = state.get("retry_count", 0)

    if guardrail_result == "aprovado":
        return "explicabilidade"

    # Reprovado: retry se ainda não atingiu limite
    if retry_count < 2:
        logger.info("Guardrails: reprovado, enviando para retry (%d/2)", retry_count)
        return "raciocinio"

    # Limite de retries atingido: seguir com warnings
    logger.warning("Guardrails: limite de retries atingido, seguindo com warnings")
    return "explicabilidade"


# ---------------------------------------------------------------------------
# Montagem do grafo
# ---------------------------------------------------------------------------

def build_graph() -> StateGraph:
    """Constrói e retorna o grafo compilado do assistente médico."""

    graph = StateGraph(MedicalAssistantState)

    # Adicionar nós
    graph.add_node("triagem", triagem_agent)
    graph.add_node("protocolo", protocolo_agent)
    graph.add_node("paciente_data", paciente_data_agent)
    graph.add_node("raciocinio", raciocinio_agent)
    graph.add_node("guardrails", guardrails_agent)
    graph.add_node("explicabilidade", explicabilidade_agent)
    graph.add_node("logger", logger_agent)

    # Entry point
    graph.set_entry_point("triagem")

    # Arestas condicionais
    graph.add_conditional_edges("triagem", route_after_triagem, {
        "protocolo": "protocolo",
        "paciente_data": "paciente_data",
        "logger": "logger",
    })

    graph.add_conditional_edges("paciente_data", route_after_paciente_data, {
        "protocolo": "protocolo",
        "raciocinio": "raciocinio",
    })

    graph.add_conditional_edges("guardrails", route_after_guardrails, {
        "explicabilidade": "explicabilidade",
        "raciocinio": "raciocinio",
    })

    # Arestas fixas
    graph.add_edge("protocolo", "raciocinio")
    graph.add_edge("raciocinio", "guardrails")
    graph.add_edge("explicabilidade", "logger")
    graph.add_edge("logger", END)

    return graph.compile()


# Grafo compilado pronto para uso
app = build_graph()


def run_assistant(
    query: str,
    patient_id: str | None = None,
    llm=None,
) -> dict:
    """
    Executa o assistente médico com uma query.

    Args:
        query: Pergunta do médico
        patient_id: ID ou nome do paciente (opcional)
        llm: Callable da LLM (opcional, para triagem e raciocínio)

    Returns:
        Estado final com final_response, sources, confidence, etc.
    """
    initial_state = {
        "query": query,
        "patient_id": patient_id,
        "query_type": "protocolo",
        "entities": {},
        "protocols": [],
        "patient_data": None,
        "draft_response": "",
        "guardrail_result": "aprovado",
        "guardrail_feedback": None,
        "retry_count": 0,
        "final_response": "",
        "sources": [],
        "confidence": "baixa",
        "warnings": [],
        "audit_log": [],
        "agent_reports": {},
    }

    # Injetar LLM no state (será removida do output)
    if llm is not None:
        initial_state["_llm"] = llm

    result = app.invoke(initial_state)

    # Remover chave interna
    result.pop("_llm", None)

    return result
