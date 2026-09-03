import uuid

from sqlalchemy import select

from app.dominio.enums import CategoriaPendencia, TipoDocumento
from app.models import Pendencia
from app.repositories.base import RepositorioBase


class PendenciaRepositorio(RepositorioBase[Pendencia]):
    modelo = Pendencia

    def listar_por_processo(self, processo_id: uuid.UUID, apenas_abertas: bool = False) -> list[Pendencia]:
        consulta = select(Pendencia).where(Pendencia.processo_id == processo_id)
        if apenas_abertas:
            consulta = consulta.where(Pendencia.resolvida.is_(False))
        return list(self.sessao.scalars(consulta.order_by(Pendencia.criado_em)).all())

    def listar_por_categoria(self, processo_id: uuid.UUID, categoria: CategoriaPendencia, apenas_abertas: bool = True) -> list[Pendencia]:
        consulta = select(Pendencia).where(Pendencia.processo_id == processo_id, Pendencia.categoria == categoria)
        if apenas_abertas:
            consulta = consulta.where(Pendencia.resolvida.is_(False))
        return list(self.sessao.scalars(consulta.order_by(Pendencia.criado_em)).all())

    def obter_ausente(self, processo_id: uuid.UUID, tipo: TipoDocumento) -> Pendencia | None:
        consulta = select(Pendencia).where(
            Pendencia.processo_id == processo_id,
            Pendencia.categoria == CategoriaPendencia.documento_ausente,
            Pendencia.tipo_documento == tipo,
        )
        return self.sessao.scalar(consulta)
