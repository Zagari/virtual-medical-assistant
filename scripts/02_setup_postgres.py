#!/usr/bin/env python3
"""
Script 02 - Setup PostgreSQL
==============================
Sobe container Docker com PostgreSQL, cria tabelas e popula com dados sinteticos.

Pre-condicoes:
    - Docker Desktop instalado e rodando
    - data/synthetic/pacientes.json existe (rodar script 01 antes)

Uso:
    python scripts/02_setup_postgres.py

Saida:
    Container Docker 'medical_assistant_db' rodando na porta 5432
    Tabelas: pacientes, exames, prontuarios, receitas (populadas)
"""

import json
import os
import shutil
import subprocess
import sys
import time
from datetime import date
from pathlib import Path
from uuid import UUID

# Adicionar raiz do projeto ao path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Configuracao do container
CONTAINER_NAME = "medical_assistant_db"
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "medical_assistant")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "changeme")

DATA_DIR = PROJECT_ROOT / "data" / "synthetic"


def check_prerequisites():
    """Verifica pre-condicoes."""
    # Docker
    if not shutil.which("docker"):
        print("ERRO: Docker não encontrado no PATH.")
        print("Instale o Docker Desktop: https://www.docker.com/products/docker-desktop/")
        sys.exit(1)

    # Verificar se Docker daemon esta rodando
    result = subprocess.run(
        ["docker", "info"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print("ERRO: Docker daemon não está rodando.")
        print("Inicie o Docker Desktop e tente novamente.")
        sys.exit(1)

    # Dados sinteticos
    if not (DATA_DIR / "pacientes.json").exists():
        print("ERRO: data/synthetic/pacientes.json não encontrado.")
        print("Execute primeiro: python scripts/01_gerar_dados_sinteticos.py")
        sys.exit(1)

    print("Pre-condições OK: Docker rodando, dados sintéticos disponíveis.")


def start_postgres_container():
    """Sobe container PostgreSQL se nao estiver rodando."""
    # Verificar se container ja existe
    result = subprocess.run(
        ["docker", "ps", "-a", "--filter", f"name={CONTAINER_NAME}", "--format", "{{.Status}}"],
        capture_output=True,
        text=True,
    )
    status = result.stdout.strip()

    if "Up" in status:
        print(f"Container '{CONTAINER_NAME}' já está rodando.")
        return

    if status:
        # Container existe mas esta parado
        print(f"Iniciando container '{CONTAINER_NAME}' existente...")
        subprocess.run(["docker", "start", CONTAINER_NAME], check=True)
    else:
        # Criar novo container
        print(f"Criando container '{CONTAINER_NAME}'...")
        subprocess.run(
            [
                "docker", "run", "-d",
                "--name", CONTAINER_NAME,
                "-e", f"POSTGRES_DB={POSTGRES_DB}",
                "-e", f"POSTGRES_USER={POSTGRES_USER}",
                "-e", f"POSTGRES_PASSWORD={POSTGRES_PASSWORD}",
                "-p", f"{POSTGRES_PORT}:5432",
                "postgres:16-alpine",
            ],
            check=True,
        )

    # Aguardar banco ficar pronto
    print("Aguardando PostgreSQL ficar pronto", end="")
    for _ in range(30):
        result = subprocess.run(
            [
                "docker", "exec", CONTAINER_NAME,
                "pg_isready", "-U", POSTGRES_USER, "-d", POSTGRES_DB,
            ],
            capture_output=True,
        )
        if result.returncode == 0:
            print(" OK!")
            return
        print(".", end="", flush=True)
        time.sleep(1)

    print("\nERRO: PostgreSQL não ficou pronto em 30 segundos.")
    sys.exit(1)


def create_tables():
    """Cria tabelas usando SQLAlchemy models."""
    from src.database.connection import get_engine
    from src.database.models import Base

    engine = get_engine()
    print("Criando tabelas...")
    Base.metadata.drop_all(engine)  # Limpa tabelas existentes
    Base.metadata.create_all(engine)
    print("  Tabelas criadas: pacientes, exames, prontuarios, receitas")


def load_json(filename: str) -> list[dict]:
    """Carrega arquivo JSON de data/synthetic/."""
    filepath = DATA_DIR / filename
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


def populate_database():
    """Popula banco com dados sinteticos."""
    from src.database.connection import get_engine
    from src.database.models import Exame, Paciente, Prontuario, Receita

    from sqlalchemy.orm import Session

    engine = get_engine()

    # Carregar dados
    patients_data = load_json("pacientes.json")
    exams_data = load_json("exames.json")
    consultations_data = load_json("prontuarios.json")
    prescriptions_data = load_json("receitas.json")

    with Session(engine) as session:
        # Pacientes
        print(f"Inserindo {len(patients_data)} pacientes...")
        for p in patients_data:
            paciente = Paciente(
                id=UUID(p["id"]),
                nome=p["nome"],
                cpf=p["cpf"],
                data_nascimento=date.fromisoformat(p["data_nascimento"]),
                sexo=p["sexo"],
                telefone=p["telefone"],
                endereco=p["endereco"],
                comorbidades=p["comorbidades"],
                alergias=p["alergias"],
                medicamentos_uso=p["medicamentos_uso"],
            )
            session.add(paciente)
        session.flush()

        # Exames
        print(f"Inserindo {len(exams_data)} exames...")
        for e in exams_data:
            exame = Exame(
                id=UUID(e["id"]),
                paciente_id=UUID(e["paciente_id"]),
                tipo=e["tipo"],
                data=date.fromisoformat(e["data"]),
                resultados=e["resultados"],
                interpretacao=e["interpretacao"],
                status=e["status"],
            )
            session.add(exame)
        session.flush()

        # Prontuarios
        print(f"Inserindo {len(consultations_data)} prontuários...")
        for c in consultations_data:
            prontuario = Prontuario(
                id=UUID(c["id"]),
                paciente_id=UUID(c["paciente_id"]),
                data=date.fromisoformat(c["data"]),
                diagnostico_cid=c["diagnostico_cid"],
                diagnostico_texto=c["diagnostico_texto"],
                observacoes=c["observacoes"],
            )
            session.add(prontuario)
        session.flush()

        # Receitas
        print(f"Inserindo {len(prescriptions_data)} receitas...")
        for r in prescriptions_data:
            receita = Receita(
                id=UUID(r["id"]),
                paciente_id=UUID(r["paciente_id"]),
                data=date.fromisoformat(r["data"]),
                condicao=r["condicao"],
                medicamentos=r["medicamentos"],
                validade_dias=r["validade_dias"],
                observacoes=r["observacoes"],
            )
            session.add(receita)

        session.commit()
        print("  Commit realizado com sucesso!")


def validate_database():
    """Valida que os dados foram inseridos corretamente."""
    from src.database.connection import get_engine

    from sqlalchemy import text
    from sqlalchemy.orm import Session

    engine = get_engine()
    with Session(engine) as session:
        tables = {
            "pacientes": session.execute(text("SELECT COUNT(*) FROM pacientes")).scalar(),
            "exames": session.execute(text("SELECT COUNT(*) FROM exames")).scalar(),
            "prontuarios": session.execute(text("SELECT COUNT(*) FROM prontuarios")).scalar(),
            "receitas": session.execute(text("SELECT COUNT(*) FROM receitas")).scalar(),
        }

    print("\nValidação do banco:")
    for table, count in tables.items():
        print(f"  {table:<15} {count:>5} registros")

    # Amostra: paciente com mais comorbidades
    with Session(engine) as session:
        result = session.execute(
            text("""
                SELECT nome, array_length(comorbidades, 1) as n_comorbidades, comorbidades
                FROM pacientes
                ORDER BY array_length(comorbidades, 1) DESC NULLS LAST
                LIMIT 3
            """)
        ).fetchall()
        print("\nPacientes com mais comorbidades:")
        for row in result:
            print(f"  {row[0]}: {row[1]} condições - {row[2]}")


def main():
    print("=" * 60)
    print("SCRIPT 02 - Setup PostgreSQL")
    print("=" * 60)

    check_prerequisites()
    start_postgres_container()
    create_tables()
    populate_database()
    validate_database()

    print("\n" + "=" * 60)
    print("Concluído! Banco PostgreSQL populado com dados sintéticos.")
    print(f"Container: {CONTAINER_NAME} (porta {POSTGRES_PORT})")
    print("Próximo passo: python scripts/03_preparar_dataset.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
