"""Agente Paciente Data (PostgreSQL) - Consulta dados clínicos do paciente."""

import logging
from datetime import date, datetime

from src.flows.state import MedicalAssistantState

logger = logging.getLogger(__name__)


def _serialize_value(val):
    """Serializa valores para JSON (date, UUID, etc.)."""
    if isinstance(val, (date, datetime)):
        return val.isoformat()
    return val


def _serialize_dict(d: dict) -> dict:
    """Serializa todos os valores de um dict."""
    return {k: _serialize_value(v) for k, v in d.items()}


def paciente_data_agent(state: MedicalAssistantState) -> dict:
    """Consulta dados do paciente no PostgreSQL."""
    entities = state.get("entities", {})
    patient_id = state.get("patient_id")
    paciente_nome = entities.get("paciente_nome")

    logger.info(
        "PacienteData: buscando patient_id=%s, nome=%s",
        patient_id, paciente_nome,
    )

    patient_data = None

    if patient_id or paciente_nome:
        try:
            from src.database.queries import (
                buscar_dados_completos_paciente,
                buscar_paciente_por_nome,
            )

            if paciente_nome:
                dados = buscar_dados_completos_paciente(paciente_nome)
            elif patient_id:
                # Buscar por ID — usar queries diretas
                from src.database.queries import (
                    buscar_exames_paciente,
                    buscar_prontuarios_paciente,
                    buscar_receitas_paciente,
                )
                pacientes = buscar_paciente_por_nome(patient_id)
                if pacientes:
                    p = pacientes[0]
                    pid = str(p["id"])
                    dados = {
                        "paciente": p,
                        "exames": buscar_exames_paciente(pid),
                        "prontuarios": buscar_prontuarios_paciente(pid),
                        "receitas": buscar_receitas_paciente(pid),
                    }
                else:
                    dados = None

            if dados:
                # Serializar para evitar problemas com JSON
                patient_data = {
                    "paciente": _serialize_dict(dados["paciente"]),
                    "exames": [_serialize_dict(e) for e in dados.get("exames", [])],
                    "prontuarios": [_serialize_dict(p) for p in dados.get("prontuarios", [])],
                    "receitas": [_serialize_dict(r) for r in dados.get("receitas", [])],
                }
                logger.info(
                    "PacienteData: encontrado - %d exames, %d prontuários, %d receitas",
                    len(patient_data["exames"]),
                    len(patient_data["prontuarios"]),
                    len(patient_data["receitas"]),
                )
            else:
                logger.warning("PacienteData: paciente não encontrado")

        except Exception as e:
            logger.error("PacienteData: erro na consulta - %s", e)

    audit_entry = {
        "agent": "paciente_data",
        "timestamp": datetime.now().isoformat(),
        "patient_id": patient_id,
        "paciente_nome": paciente_nome,
        "found": patient_data is not None,
    }

    return {
        "patient_data": patient_data,
        "audit_log": state.get("audit_log", []) + [audit_entry],
    }
