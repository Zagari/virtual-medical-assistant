"""Modelos SQLAlchemy para o banco de dados do assistente medico."""

import uuid

from sqlalchemy import (
    Column,
    Date,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Paciente(Base):
    __tablename__ = "pacientes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(200), nullable=False)
    cpf = Column(String(14), unique=True, nullable=False)
    data_nascimento = Column(Date, nullable=False)
    sexo = Column(String(1), nullable=False)
    telefone = Column(String(20))
    endereco = Column(Text)
    comorbidades = Column(ARRAY(Text), default=[])
    alergias = Column(ARRAY(Text), default=[])
    medicamentos_uso = Column(ARRAY(Text), default=[])

    # Relationships
    exames = relationship("Exame", back_populates="paciente")
    prontuarios = relationship("Prontuario", back_populates="paciente")
    receitas = relationship("Receita", back_populates="paciente")


class Exame(Base):
    __tablename__ = "exames"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=False)
    tipo = Column(String(100), nullable=False)
    data = Column(Date, nullable=False)
    resultados = Column(JSONB)
    interpretacao = Column(Text)
    status = Column(String(20), default="realizado")

    paciente = relationship("Paciente", back_populates="exames")


class Prontuario(Base):
    __tablename__ = "prontuarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=False)
    data = Column(Date, nullable=False)
    diagnostico_cid = Column(String(10))
    diagnostico_texto = Column(Text)
    observacoes = Column(Text)

    paciente = relationship("Paciente", back_populates="prontuarios")


class Receita(Base):
    __tablename__ = "receitas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=False)
    data = Column(Date, nullable=False)
    condicao = Column(Text)
    medicamentos = Column(ARRAY(Text), default=[])
    validade_dias = Column(Integer)
    observacoes = Column(Text)

    paciente = relationship("Paciente", back_populates="receitas")
