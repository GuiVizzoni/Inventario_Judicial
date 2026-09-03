import uuid

from sqlalchemy import select

from app.models import Evento
from app.repositories.base import RepositorioBase


class EventoRepositorio(RepositorioBase[Evento]):
    modelo = Evento

    def listar_recentes(self, processo_id: uuid.UUID, limite: int = 10) -> list[Evento]:
        consulta = select(Evento).where(Evento.processo_id == processo_id).order_by(Evento.criado_em.desc()).limit(limite)
        return list(self.sessao.scalars(consulta).all())
