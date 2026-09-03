from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import processo_atual, usuario_atual
from app.api.schemas import ChecklistSaida, EventoSaida, ProcessoAtualizar, ProcessoEntrada, ProcessoSaida, ResumoSaida
from app.db import obter_sessao
from app.models import Processo, Usuario
from app.repositories import EventoRepositorio
from app.services.processo_service import ProcessoService

router = APIRouter(prefix="/processos", tags=["Processos"])


@router.get("", response_model=list[ProcessoSaida])
def listar(usuario: Usuario = Depends(usuario_atual), sessao: Session = Depends(obter_sessao)) -> list[Processo]:
    return ProcessoService(sessao).listar(usuario)


@router.post("", response_model=ProcessoSaida, status_code=status.HTTP_201_CREATED)
def criar(dados: ProcessoEntrada, usuario: Usuario = Depends(usuario_atual), sessao: Session = Depends(obter_sessao)) -> Processo:
    return ProcessoService(sessao).criar(dados, usuario)


@router.get("/{processo_id}", response_model=ProcessoSaida)
def obter(processo: Processo = Depends(processo_atual)) -> Processo:
    return processo


@router.patch("/{processo_id}", response_model=ProcessoSaida)
def atualizar(dados: ProcessoAtualizar, processo: Processo = Depends(processo_atual), sessao: Session = Depends(obter_sessao)) -> Processo:
    return ProcessoService(sessao).atualizar(processo, dados)


@router.delete("/{processo_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover(processo: Processo = Depends(processo_atual), sessao: Session = Depends(obter_sessao)) -> None:
    ProcessoService(sessao).remover(processo)


@router.get("/{processo_id}/resumo", response_model=ResumoSaida)
def resumo(processo: Processo = Depends(processo_atual), sessao: Session = Depends(obter_sessao)) -> dict:
    return ProcessoService(sessao).resumo(processo)


@router.get("/{processo_id}/checklist", response_model=ChecklistSaida)
def checklist(processo: Processo = Depends(processo_atual), sessao: Session = Depends(obter_sessao)) -> dict:
    return ProcessoService(sessao).checklist(processo)


@router.get("/{processo_id}/eventos", response_model=list[EventoSaida])
def eventos(limite: int = 50, processo: Processo = Depends(processo_atual), sessao: Session = Depends(obter_sessao)) -> list:
    return EventoRepositorio(sessao).listar_recentes(processo.id, limite=limite)
