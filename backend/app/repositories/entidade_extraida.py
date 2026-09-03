import uuid

from sqlalchemy import func, select

from app.dominio.enums import StatusItem, TipoDocumento
from app.models import Documento, EntidadeExtraida
from app.repositories.base import RepositorioBase


class EntidadeExtraidaRepositorio(RepositorioBase[EntidadeExtraida]):
    modelo = EntidadeExtraida

    def listar_por_documento(self, documento_id: uuid.UUID, apenas_ultima_versao: bool = True) -> list[EntidadeExtraida]:
        consulta = select(EntidadeExtraida).where(EntidadeExtraida.documento_id == documento_id)
        if apenas_ultima_versao:
            versao = self.ultima_versao(documento_id)
            consulta = consulta.where(EntidadeExtraida.versao_extracao == versao)
        return list(self.sessao.scalars(consulta.order_by(EntidadeExtraida.chave)).all())

    def ultima_versao(self, documento_id: uuid.UUID) -> int:
        versao = self.sessao.scalar(
            select(func.max(EntidadeExtraida.versao_extracao)).where(EntidadeExtraida.documento_id == documento_id)
        )
        return int(versao or 0)

    def listar_por_processo_e_tipo(self, processo_id: uuid.UUID, tipo: TipoDocumento) -> list[EntidadeExtraida]:
        documentos = self.sessao.scalars(
            select(Documento).where(
                Documento.processo_id == processo_id,
                Documento.tipo == tipo,
                Documento.status_validacao == StatusItem.concluido,
            )
        ).all()
        resultado: list[EntidadeExtraida] = []
        for documento in documentos:
            resultado.extend(self.listar_por_documento(documento.id))
        return resultado

    def como_dicionario(self, documento_id: uuid.UUID) -> dict[str, str]:
        return {e.chave: e.valor for e in self.listar_por_documento(documento_id)}
