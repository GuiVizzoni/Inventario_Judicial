import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import processo_atual, usuario_atual
from app.api.schemas import PendenciaSaida
from app.db import obter_sessao
from app.models import Pendencia, Processo, Usuario
from app.repositories import PendenciaRepositorio
from app.services.processo_service import ProcessoService

router = APIRouter(prefix="/processos/{processo_id}/pendencias", tags=["Pendências"])


@router.get("", response_model=list[PendenciaSaida])
def listar(apenas_abertas: bool = True, processo: Processo = Depends(processo_atual), sessao: Session = Depends(obter_sessao)) -> list[Pendencia]:
    return PendenciaRepositorio(sessao).listar_por_processo(processo.id, apenas_abertas=apenas_abertas)


@router.post("/{pendencia_id}/resolver", response_model=PendenciaSaida)
def resolver(pendencia_id: uuid.UUID, processo: Processo = Depends(processo_atual), usuario: Usuario = Depends(usuario_atual), sessao: Session = Depends(obter_sessao)) -> Pendencia:
    servico = ProcessoService(sessao)
    return servico.resolver_pendencia(servico.obter_pendencia(processo, pendencia_id), ator=usuario.nome)
