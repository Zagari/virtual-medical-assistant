"""Queries parametrizadas para consulta de dados de pacientes."""

from sqlalchemy import text
from sqlalchemy.orm import Session

from src.database.connection import get_engine


def buscar_paciente_por_nome(nome: str) -> list[dict]:
    """Busca pacientes por nome (parcial, case-insensitive)."""
    engine = get_engine()
    with Session(engine) as session:
        result = session.execute(
            text("""
                SELECT id, nome, cpf, data_nascimento, sexo,
                       comorbidades, alergias, medicamentos_uso
                FROM pacientes
                WHERE nome ILIKE :nome
                ORDER BY nome
            """),
            {"nome": f"%{nome}%"},
        )
        return [dict(row._mapping) for row in result]


def buscar_exames_paciente(paciente_id: str) -> list[dict]:
    """Retorna exames de um paciente, ordenados por data."""
    engine = get_engine()
    with Session(engine) as session:
        result = session.execute(
            text("""
                SELECT tipo, data, resultados, interpretacao, status
                FROM exames
                WHERE paciente_id = :pid
                ORDER BY data DESC
            """),
            {"pid": paciente_id},
        )
        return [dict(row._mapping) for row in result]


def buscar_prontuarios_paciente(paciente_id: str) -> list[dict]:
    """Retorna prontuarios de um paciente, ordenados por data."""
    engine = get_engine()
    with Session(engine) as session:
        result = session.execute(
            text("""
                SELECT data, diagnostico_cid, diagnostico_texto, observacoes
                FROM prontuarios
                WHERE paciente_id = :pid
                ORDER BY data DESC
            """),
            {"pid": paciente_id},
        )
        return [dict(row._mapping) for row in result]


def buscar_receitas_paciente(paciente_id: str) -> list[dict]:
    """Retorna receitas de um paciente, ordenadas por data."""
    engine = get_engine()
    with Session(engine) as session:
        result = session.execute(
            text("""
                SELECT data, condicao, medicamentos, validade_dias, observacoes
                FROM receitas
                WHERE paciente_id = :pid
                ORDER BY data DESC
            """),
            {"pid": paciente_id},
        )
        return [dict(row._mapping) for row in result]


def buscar_dados_completos_paciente(nome: str) -> dict | None:
    """Busca um paciente por nome e retorna todos os seus dados clinicos."""
    pacientes = buscar_paciente_por_nome(nome)
    if not pacientes:
        return None

    paciente = pacientes[0]  # Primeiro match
    pid = str(paciente["id"])

    return {
        "paciente": paciente,
        "exames": buscar_exames_paciente(pid),
        "prontuarios": buscar_prontuarios_paciente(pid),
        "receitas": buscar_receitas_paciente(pid),
    }
