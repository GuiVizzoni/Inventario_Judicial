import uuid

from sqlalchemy import Boolean, Enum, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.dominio.enums import StatusItem
from app.models.base import ModeloBase


class Herdeiro(ModeloBase):
    __tablename__ = "herdeiro"

    processo_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("processo.id", ondelete="CASCADE"), nullable=False, index=True)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    cpf: Mapped[str | None] = mapped_column(String(14), nullable=True)
    parentesco: Mapped[str] = mapped_column(String(60), nullable=False)
    pre_morto: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    conjuge: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    representa_herdeiro_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("herdeiro.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[StatusItem] = mapped_column(Enum(StatusItem, native_enum=False, length=32), default=StatusItem.pendente, nullable=False)

    processo = relationship("Processo", back_populates="herdeiros")
    representado = relationship("Herdeiro", remote_side="Herdeiro.id", foreign_keys=[representa_herdeiro_id])
