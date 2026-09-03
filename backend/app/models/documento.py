import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.dominio.enums import OrigemDocumento, StatusItem, TipoDocumento
from app.models.base import ModeloBase, agora


class Documento(ModeloBase):
    __tablename__ = "documento"

    processo_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("processo.id", ondelete="CASCADE"), nullable=False, index=True)
    tipo: Mapped[TipoDocumento] = mapped_column(Enum(TipoDocumento, native_enum=False, length=40), nullable=False)
    tipo_detectado: Mapped[TipoDocumento | None] = mapped_column(Enum(TipoDocumento, native_enum=False, length=40), nullable=True)
    nome_arquivo: Mapped[str] = mapped_column(String(255), nullable=False)
    caminho_arquivo: Mapped[str | None] = mapped_column(String(500), nullable=True)
    tamanho_bytes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status_validacao: Mapped[StatusItem] = mapped_column(Enum(StatusItem, native_enum=False, length=32), default=StatusItem.pendente, nullable=False)
    motivo_status: Mapped[str | None] = mapped_column(Text, nullable=True)
    texto_extraido: Mapped[str | None] = mapped_column(Text, nullable=True)
    metodo_extracao: Mapped[str | None] = mapped_column(String(20), nullable=True)
    origem: Mapped[OrigemDocumento] = mapped_column(Enum(OrigemDocumento, native_enum=False, length=32), default=OrigemDocumento.upload_manual, nullable=False)
    recebido_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora, nullable=False)
    processamento_iniciado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    processamento_concluido_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    erro_processamento: Mapped[str | None] = mapped_column(Text, nullable=True)

    processo = relationship("Processo", back_populates="documentos")
    entidades = relationship("EntidadeExtraida", back_populates="documento", cascade="all, delete-orphan", order_by="EntidadeExtraida.extraido_em")
