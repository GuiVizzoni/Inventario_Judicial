import uuid

from sqlalchemy import select

from app.models import Herdeiro
from app.repositories.base import RepositorioBase


class HerdeiroRepositorio(RepositorioBase[Herdeiro]):
    modelo = Herdeiro

    def listar_por_processo(self, processo_id: uuid.UUID) -> list[Herdeiro]:
        consulta = select(Herdeiro).where(Herdeiro.processo_id == processo_id).order_by(Herdeiro.criado_em)
        return list(self.sessao.scalars(consulta).all())
