from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.dominio.enums import PapelUsuario
from app.models.base import ModeloBase


class Usuario(ModeloBase):
    __tablename__ = "usuario"

    nome: Mapped[str] = mapped_column(String(160), nullable=False)
    email: Mapped[str] = mapped_column(String(160), unique=True, index=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    papel: Mapped[PapelUsuario] = mapped_column(Enum(PapelUsuario, native_enum=False, length=32), default=PapelUsuario.advogado, nullable=False)
    oab: Mapped[str | None] = mapped_column(String(40), nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
