import uuid

from sqlalchemy import select

from app.dominio.enums import StatusItem, TipoDocumento
from app.models import Documento
from app.repositories.base import RepositorioBase


class DocumentoRepositorio(RepositorioBase[Documento]):
    modelo = Documento

    def listar_por_processo(self, processo_id: uuid.UUID) -> list[Documento]:
        consulta = select(Documento).where(Documento.processo_id == processo_id).order_by(Documento.recebido_em.desc())
        return list(self.sessao.scalars(consulta).all())

    def listar_por_tipo(self, processo_id: uuid.UUID, tipo: TipoDocumento) -> list[Documento]:
        consulta = (
            select(Documento)
            .where(Documento.processo_id == processo_id, Documento.tipo == tipo)
            .order_by(Documento.recebido_em.desc())
        )
        return list(self.sessao.scalars(consulta).all())

    def listar_validados_por_tipo(self, processo_id: uuid.UUID, tipo: TipoDocumento) -> list[Documento]:
        consulta = (
            select(Documento)
            .where(
                Documento.processo_id == processo_id,
                Documento.tipo == tipo,
                Documento.status_validacao == StatusItem.concluido,
            )
            .order_by(Documento.recebido_em.desc())
        )
        return list(self.sessao.scalars(consulta).all())
