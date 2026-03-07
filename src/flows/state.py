"""State schema do grafo multi-agente LangGraph."""

from typing import Any, Literal, Optional, TypedDict


class MedicalAssistantState(TypedDict):
    # Entrada
    query: str
    patient_id: Optional[str]

    # Recursos injetados
    _llm: Optional[Any]

    # Triagem
    query_type: Literal["protocolo", "paciente", "ambos", "fora_de_escopo"]
    entities: dict

    # Contexto
    protocols: list[dict]
    patient_data: Optional[dict]

    # Raciocínio
    draft_response: str
    guardrail_result: Literal["aprovado", "reprovado"]
    guardrail_feedback: Optional[str]
    retry_count: int

    # Saída
    final_response: str
    sources: list[str]
    confidence: Literal["alta", "media", "baixa"]
    warnings: list[str]

    # Auditoria
    audit_log: list[dict]
