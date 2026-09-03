import uuid

from sqlalchemy import select

from app.models import Processo
from app.repositories.base import RepositorioBase


class ProcessoRepositorio(RepositorioBase[Processo]):
    modelo = Processo

    def listar_por_responsavel(self, usuario_id: uuid.UUID) -> list[Processo]:
        consulta = select(Processo).where(Processo.responsavel_id == usuario_id).order_by(Processo.criado_em.desc())
        return list(self.sessao.scalars(consulta).all())
