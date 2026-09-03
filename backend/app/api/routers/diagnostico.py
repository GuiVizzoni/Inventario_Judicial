from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import processo_atual
from app.api.schemas import AnaliseSaida
from app.db import obter_sessao
from app.models import Processo
from app.services.diagnostico_service import DiagnosticoService

router = APIRouter(prefix="/processos/{processo_id}", tags=["Diagnóstico"])


@router.get("/analise", response_model=AnaliseSaida)
def analise(processo: Processo = Depends(processo_atual), sessao: Session = Depends(obter_sessao)) -> dict:
    return DiagnosticoService(sessao).resumo_analise(processo)


@router.post("/analise/executar", response_model=AnaliseSaida)
def executar(processo: Processo = Depends(processo_atual), sessao: Session = Depends(obter_sessao)) -> dict:
    servico = DiagnosticoService(sessao)
    servico.executar(processo)
    sessao.commit()
    return servico.resumo_analise(processo)


@router.get("/arvore")
def arvore(processo: Processo = Depends(processo_atual), sessao: Session = Depends(obter_sessao)) -> dict:
    return DiagnosticoService(sessao).arvore_genealogica(processo)
