import uuid

from sqlalchemy import select

from app.models import Bem
from app.repositories.base import RepositorioBase


class BemRepositorio(RepositorioBase[Bem]):
    modelo = Bem

    def listar_por_processo(self, processo_id: uuid.UUID) -> list[Bem]:
        consulta = select(Bem).where(Bem.processo_id == processo_id).order_by(Bem.criado_em)
        return list(self.sessao.scalars(consulta).all())
