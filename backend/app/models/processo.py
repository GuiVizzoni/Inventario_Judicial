import uuid
from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.dominio.enums import StatusProcesso
from app.models.base import ModeloBase


class Processo(ModeloBase):
    __tablename__ = "processo"

    numero_processo: Mapped[str | None] = mapped_column(String(40), nullable=True, index=True)
    status: Mapped[StatusProcesso] = mapped_column(Enum(StatusProcesso, native_enum=False, length=32), default=StatusProcesso.bloqueado, nullable=False)
    data_abertura: Mapped[date | None] = mapped_column(Date, nullable=True)
    data_obito: Mapped[date | None] = mapped_column(Date, nullable=True)
    nome_de_cujus: Mapped[str] = mapped_column(String(200), nullable=False)
    cpf_de_cujus: Mapped[str] = mapped_column(String(14), nullable=False)
    ultimo_domicilio: Mapped[str | None] = mapped_column(String(200), nullable=True)
    regime_bens: Mapped[str | None] = mapped_column(String(80), nullable=True)
    responsavel_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("usuario.id"), nullable=False, index=True)

    responsavel = relationship("Usuario", lazy="joined")
    documentos = relationship("Documento", back_populates="processo", cascade="all, delete-orphan", order_by="Documento.recebido_em")
    herdeiros = relationship("Herdeiro", back_populates="processo", cascade="all, delete-orphan", order_by="Herdeiro.criado_em")
    bens = relationship("Bem", back_populates="processo", cascade="all, delete-orphan", order_by="Bem.criado_em")
    pendencias = relationship("Pendencia", back_populates="processo", cascade="all, delete-orphan", order_by="Pendencia.criado_em")
    eventos = relationship("Evento", back_populates="processo", cascade="all, delete-orphan", order_by="Evento.criado_em.desc()")
