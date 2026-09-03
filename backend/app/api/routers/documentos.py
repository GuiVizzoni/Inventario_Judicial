import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from fastapi import UploadFile

from app.api.deps import processo_atual, usuario_atual
from app.api.schemas import DocumentoDetalheSaida, DocumentoSaida, EntidadeSaida
from app.db import obter_sessao
from app.dominio.catalogo_documentos import obter_item
from app.dominio.enums import TipoDocumento
from app.models import Documento, Processo, Usuario
from app.repositories import EntidadeExtraidaRepositorio
from app.services.documento_service import DocumentoService, processar_em_segundo_plano

router = APIRouter(prefix="/processos/{processo_id}/documentos", tags=["Documentos"])


def documento_para_saida(documento: Documento, sessao: Session, detalhe: bool = False) -> DocumentoSaida:
    item = obter_item(documento.tipo)
    entidades = EntidadeExtraidaRepositorio(sessao).listar_por_documento(documento.id)
    base = {
        "id": documento.id,
        "processo_id": documento.processo_id,
        "tipo": documento.tipo,
        "tipo_nome": item.nome if item else documento.tipo.value,
        "categoria": item.categoria if item else "Outros",
        "tipo_detectado": documento.tipo_detectado,
        "nome_arquivo": documento.nome_arquivo,
        "tamanho_bytes": documento.tamanho_bytes,
        "status_validacao": documento.status_validacao,
        "motivo_status": documento.motivo_status,
        "origem": documento.origem,
        "metodo_extracao": documento.metodo_extracao,
        "recebido_em": documento.recebido_em,
        "processamento_iniciado_em": documento.processamento_iniciado_em,
        "processamento_concluido_em": documento.processamento_concluido_em,
        "erro_processamento": documento.erro_processamento,
        "entidades": [EntidadeSaida.model_validate(e) for e in entidades],
    }
    if detalhe:
        return DocumentoDetalheSaida(**base, texto_extraido=documento.texto_extraido)
    return DocumentoSaida(**base)


@router.get("", response_model=list[DocumentoSaida])
def listar(processo: Processo = Depends(processo_atual), sessao: Session = Depends(obter_sessao)) -> list[DocumentoSaida]:
    servico = DocumentoService(sessao)
    return [documento_para_saida(d, sessao) for d in servico.listar(processo)]


@router.post("", response_model=DocumentoSaida, status_code=status.HTTP_202_ACCEPTED)
async def enviar(
    tarefas: BackgroundTasks,
    tipo: TipoDocumento = Form(...),
    arquivo: UploadFile = File(...),
    processo: Processo = Depends(processo_atual),
    usuario: Usuario = Depends(usuario_atual),
    sessao: Session = Depends(obter_sessao),
) -> DocumentoSaida:
    conteudo = await arquivo.read()
    documento = DocumentoService(sessao).receber_upload(processo, tipo, arquivo.filename or "arquivo.pdf", conteudo, ator=usuario.nome)
    tarefas.add_task(processar_em_segundo_plano, documento.id)
    return documento_para_saida(documento, sessao)


@router.post("/busca-automatica", response_model=list[DocumentoSaida])
def busca_automatica(processo: Processo = Depends(processo_atual), sessao: Session = Depends(obter_sessao)) -> list[DocumentoSaida]:
    emitidos = DocumentoService(sessao).buscar_certidoes_automaticas(processo)
    return [documento_para_saida(d, sessao) for d in emitidos]


@router.get("/{documento_id}", response_model=DocumentoDetalheSaida)
def obter(documento_id: uuid.UUID, processo: Processo = Depends(processo_atual), sessao: Session = Depends(obter_sessao)) -> DocumentoSaida:
    documento = DocumentoService(sessao).obter(processo, documento_id)
    return documento_para_saida(documento, sessao, detalhe=True)


@router.get("/{documento_id}/arquivo")
def baixar(documento_id: uuid.UUID, processo: Processo = Depends(processo_atual), sessao: Session = Depends(obter_sessao)) -> FileResponse:
    documento = DocumentoService(sessao).obter(processo, documento_id)
    if not documento.caminho_arquivo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Arquivo não disponível")
    return FileResponse(documento.caminho_arquivo, media_type="application/pdf", filename=documento.nome_arquivo)


@router.post("/{documento_id}/reprocessar", response_model=DocumentoSaida)
def reprocessar(documento_id: uuid.UUID, processo: Processo = Depends(processo_atual), sessao: Session = Depends(obter_sessao)) -> DocumentoSaida:
    servico = DocumentoService(sessao)
    documento = servico.reprocessar(servico.obter(processo, documento_id))
    return documento_para_saida(documento, sessao)


@router.delete("/{documento_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover(documento_id: uuid.UUID, processo: Processo = Depends(processo_atual), sessao: Session = Depends(obter_sessao)) -> None:
    servico = DocumentoService(sessao)
    servico.remover(servico.obter(processo, documento_id))
