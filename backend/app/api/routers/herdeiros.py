import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import processo_atual
from app.api.schemas import HerdeiroAtualizar, HerdeiroEntrada, HerdeiroSaida
from app.db import obter_sessao
from app.models import Herdeiro, Processo
from app.repositories import HerdeiroRepositorio
from app.services.processo_service import ProcessoService

router = APIRouter(prefix="/processos/{processo_id}/herdeiros", tags=["Herdeiros"])


@router.get("", response_model=list[HerdeiroSaida])
def listar(processo: Processo = Depends(processo_atual), sessao: Session = Depends(obter_sessao)) -> list[Herdeiro]:
    return HerdeiroRepositorio(sessao).listar_por_processo(processo.id)


@router.post("", response_model=HerdeiroSaida, status_code=status.HTTP_201_CREATED)
def criar(dados: HerdeiroEntrada, processo: Processo = Depends(processo_atual), sessao: Session = Depends(obter_sessao)) -> Herdeiro:
    return ProcessoService(sessao).adicionar_herdeiro(processo, dados)


@router.get("/{herdeiro_id}", response_model=HerdeiroSaida)
def obter(herdeiro_id: uuid.UUID, processo: Processo = Depends(processo_atual), sessao: Session = Depends(obter_sessao)) -> Herdeiro:
    return ProcessoService(sessao).obter_herdeiro(processo, herdeiro_id)


@router.patch("/{herdeiro_id}", response_model=HerdeiroSaida)
def atualizar(herdeiro_id: uuid.UUID, dados: HerdeiroAtualizar, processo: Processo = Depends(processo_atual), sessao: Session = Depends(obter_sessao)) -> Herdeiro:
    servico = ProcessoService(sessao)
    return servico.atualizar_herdeiro(servico.obter_herdeiro(processo, herdeiro_id), dados)


@router.delete("/{herdeiro_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover(herdeiro_id: uuid.UUID, processo: Processo = Depends(processo_atual), sessao: Session = Depends(obter_sessao)) -> None:
    servico = ProcessoService(sessao)
    servico.remover_herdeiro(servico.obter_herdeiro(processo, herdeiro_id))
