import uuid
from decimal import Decimal

from sqlalchemy import Enum, ForeignKey, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.dominio.enums import CategoriaBem, OrigemBem, StatusItem
from app.models.base import ModeloBase


class Bem(ModeloBase):
    __tablename__ = "bem"

    processo_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("processo.id", ondelete="CASCADE"), nullable=False, index=True)
    descricao: Mapped[str] = mapped_column(String(300), nullable=False)
    categoria: Mapped[CategoriaBem] = mapped_column(Enum(CategoriaBem, native_enum=False, length=32), default=CategoriaBem.outro, nullable=False)
    valor_estimado: Mapped[Decimal] = mapped_column(Numeric(16, 2), default=Decimal("0"), nullable=False)
    identificador: Mapped[str | None] = mapped_column(String(120), nullable=True)
    origem: Mapped[OrigemBem] = mapped_column(Enum(OrigemBem, native_enum=False, length=32), default=OrigemBem.formulario, nullable=False)
    status: Mapped[StatusItem] = mapped_column(Enum(StatusItem, native_enum=False, length=32), default=StatusItem.pendente, nullable=False)

    processo = relationship("Processo", back_populates="bens")
