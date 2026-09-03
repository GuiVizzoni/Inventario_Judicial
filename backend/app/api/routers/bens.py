import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import processo_atual
from app.api.schemas import BemAtualizar, BemEntrada, BemSaida
from app.db import obter_sessao
from app.models import Bem, Processo
from app.repositories import BemRepositorio
from app.services.processo_service import ProcessoService

router = APIRouter(prefix="/processos/{processo_id}/bens", tags=["Patrimônio"])


@router.get("", response_model=list[BemSaida])
def listar(processo: Processo = Depends(processo_atual), sessao: Session = Depends(obter_sessao)) -> list[Bem]:
    return BemRepositorio(sessao).listar_por_processo(processo.id)


@router.post("", response_model=BemSaida, status_code=status.HTTP_201_CREATED)
def criar(dados: BemEntrada, processo: Processo = Depends(processo_atual), sessao: Session = Depends(obter_sessao)) -> Bem:
    return ProcessoService(sessao).adicionar_bem(processo, dados)


@router.get("/{bem_id}", response_model=BemSaida)
def obter(bem_id: uuid.UUID, processo: Processo = Depends(processo_atual), sessao: Session = Depends(obter_sessao)) -> Bem:
    return ProcessoService(sessao).obter_bem(processo, bem_id)


@router.patch("/{bem_id}", response_model=BemSaida)
def atualizar(bem_id: uuid.UUID, dados: BemAtualizar, processo: Processo = Depends(processo_atual), sessao: Session = Depends(obter_sessao)) -> Bem:
    servico = ProcessoService(sessao)
    return servico.atualizar_bem(servico.obter_bem(processo, bem_id), dados)


@router.delete("/{bem_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover(bem_id: uuid.UUID, processo: Processo = Depends(processo_atual), sessao: Session = Depends(obter_sessao)) -> None:
    servico = ProcessoService(sessao)
    servico.remover_bem(servico.obter_bem(processo, bem_id))
