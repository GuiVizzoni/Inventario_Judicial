import uuid
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.base import ModeloBase

T = TypeVar("T", bound=ModeloBase)


class RepositorioBase(Generic[T]):
    modelo: type[T]

    def __init__(self, sessao: Session):
        self.sessao = sessao

    def obter(self, id_: uuid.UUID) -> T | None:
        return self.sessao.get(self.modelo, id_)

    def listar(self) -> list[T]:
        return list(self.sessao.scalars(select(self.modelo)).all())

    def adicionar(self, entidade: T) -> T:
        self.sessao.add(entidade)
        self.sessao.flush()
        return entidade

    def remover(self, entidade: T) -> None:
        self.sessao.delete(entidade)
        self.sessao.flush()

    def salvar(self) -> None:
        self.sessao.commit()
