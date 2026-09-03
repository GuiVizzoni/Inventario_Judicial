import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.dominio.enums import CategoriaPendencia, TipoDocumento
from app.models.base import ModeloBase


class Pendencia(ModeloBase):
    __tablename__ = "pendencia"

    processo_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("processo.id", ondelete="CASCADE"), nullable=False, index=True)
    categoria: Mapped[CategoriaPendencia] = mapped_column(Enum(CategoriaPendencia, native_enum=False, length=32), default=CategoriaPendencia.documento_ausente, nullable=False)
    tipo_documento: Mapped[TipoDocumento | None] = mapped_column(Enum(TipoDocumento, native_enum=False, length=40), nullable=True)
    documento_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("documento.id", ondelete="SET NULL"), nullable=True)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    bloqueante: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    link_portal: Mapped[str | None] = mapped_column(String(500), nullable=True)
    resolvida: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    resolvida_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    processo = relationship("Processo", back_populates="pendencias")
