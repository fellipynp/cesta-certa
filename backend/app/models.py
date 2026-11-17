from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .database import Base


class Usuario(Base):
    __tablename__ = "usuario"

    id_usuario = Column(Integer, primary_key=True)
    nome = Column(String(120), nullable=False)
    email = Column(String(120), nullable=False, unique=True)
    senha_hash = Column(String(255), nullable=False)  # nunca a senha em texto
    perfil = Column(String(20), nullable=False)  # coordenador ou voluntario
    ativo = Column(Boolean, nullable=False, default=True)
    tentativas_falhas = Column(Integer, nullable=False, default=0)
    bloqueado_ate = Column(DateTime, nullable=True)
    data_cadastro = Column(Date, nullable=False, default=date.today)

    __table_args__ = (
        CheckConstraint("perfil IN ('coordenador','voluntario')", name="ck_usuario_perfil"),
    )


class Familia(Base):
    __tablename__ = "familia"

    id_familia = Column(Integer, primary_key=True)
    nome_responsavel = Column(String(120), nullable=False)
    telefone = Column(String(15), nullable=False)
    endereco = Column(String(200), nullable=False)
    qtd_pessoas = Column(Integer, nullable=False)
    ativa = Column(Boolean, nullable=False, default=True)
    data_cadastro = Column(Date, nullable=False, default=date.today)

    entregas = relationship("Entrega", back_populates="familia")

    __table_args__ = (
        UniqueConstraint("nome_responsavel", "telefone", name="uq_familia_nome_telefone"),
        CheckConstraint("qtd_pessoas > 0", name="ck_familia_qtd_pessoas"),
    )


class Entrega(Base):
    __tablename__ = "entrega"

    id_entrega = Column(Integer, primary_key=True)
    id_familia = Column(Integer, ForeignKey("familia.id_familia"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)
    data_entrega = Column(Date, nullable=False, default=date.today)
    mes_referencia = Column(String(7), nullable=False)  # formato AAAA-MM

    familia = relationship("Familia", back_populates="entregas")

    __table_args__ = (
        # Garante no banco: uma entrega por família por mês (RF02).
        UniqueConstraint("id_familia", "mes_referencia", name="uq_entrega_familia_mes"),
    )


class ItemEstoque(Base):
    __tablename__ = "item_estoque"

    id_item = Column(Integer, primary_key=True)
    nome_produto = Column(String(120), nullable=False)
    unidade = Column(String(20), nullable=False)
    quantidade_atual = Column(Integer, nullable=False, default=0)
    data_validade = Column(Date, nullable=False)
    data_entrada = Column(Date, nullable=False, default=date.today)
    ativo = Column(Boolean, nullable=False, default=True)

    movimentacoes = relationship("Movimentacao", back_populates="item")

    __table_args__ = (
        CheckConstraint("quantidade_atual >= 0", name="ck_item_quantidade"),
        CheckConstraint(
            "unidade IN ('pacote','kg','litro','unidade')", name="ck_item_unidade"
        ),
    )


class Movimentacao(Base):
    __tablename__ = "movimentacao"

    id_movimentacao = Column(Integer, primary_key=True)
    id_item = Column(Integer, ForeignKey("item_estoque.id_item"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)
    tipo = Column(String(20), nullable=False)  # entrada, saida_cesta ou descarte
    quantidade = Column(Integer, nullable=False)
    data_hora = Column(DateTime, nullable=False, default=datetime.now)
    motivo = Column(String(200), nullable=True)

    item = relationship("ItemEstoque", back_populates="movimentacoes")

    __table_args__ = (
        CheckConstraint("quantidade > 0", name="ck_mov_quantidade"),
        CheckConstraint(
            "tipo IN ('entrada','saida_cesta','descarte')", name="ck_mov_tipo"
        ),
    )
