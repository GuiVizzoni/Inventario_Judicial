import uuid

from sqlalchemy import Enum, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.dominio.enums import StatusItem, TipoEvento
from app.models.base import ModeloBase


class Evento(ModeloBase):
    __tablename__ = "evento"

    processo_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("processo.id", ondelete="CASCADE"), nullable=False, index=True)
    tipo: Mapped[TipoEvento] = mapped_column(Enum(TipoEvento, native_enum=False, length=40), nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[StatusItem] = mapped_column(Enum(StatusItem, native_enum=False, length=32), default=StatusItem.concluido, nullable=False)
    referencia_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    ator: Mapped[str] = mapped_column(String(160), default="sistema", nullable=False)

    processo = relationship("Processo", back_populates="eventos")
