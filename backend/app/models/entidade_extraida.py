import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.dominio.enums import CategoriaEntidade
from app.models.base import ModeloBase, agora


class EntidadeExtraida(ModeloBase):
    __tablename__ = "entidade_extraida"

    documento_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("documento.id", ondelete="CASCADE"), nullable=False, index=True)
    categoria: Mapped[CategoriaEntidade] = mapped_column(Enum(CategoriaEntidade, native_enum=False, length=32), default=CategoriaEntidade.outro, nullable=False)
    chave: Mapped[str] = mapped_column(String(80), nullable=False)
    valor: Mapped[str] = mapped_column(Text, nullable=False)
    confianca: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    modelo_llm: Mapped[str] = mapped_column(String(80), nullable=False)
    versao_extracao: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    duracao_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    extraido_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora, nullable=False)

    documento = relationship("Documento", back_populates="entidades")
