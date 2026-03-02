"""Conexao com banco PostgreSQL via SQLAlchemy."""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv

load_dotenv()


def get_database_url() -> str:
    """Monta a URL de conexao com o banco a partir de variaveis de ambiente."""
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "medical_assistant")
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "changeme")
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"


def get_engine(echo: bool = False):
    """Cria engine SQLAlchemy."""
    return create_engine(get_database_url(), echo=echo)


def get_session():
    """Cria sessao SQLAlchemy."""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()
