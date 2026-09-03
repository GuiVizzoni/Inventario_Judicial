import re
import uuid
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import obter_configuracao
from app.db import SessionLocal
from app.dominio.catalogo_documentos import CATALOGO, obter_item
from app.dominio.enums import CategoriaPendencia, OrigemDocumento, StatusItem, StatusProcesso, TipoDocumento, TipoEvento
from app.integrations.certidao_adapter import CertidaoAdapter
from app.integrations.fabrica import obter_certidao_adapter, obter_llm_adapter
from app.integrations.llm_adapter import LLMAdapter
from app.models import Documento, Pendencia, Processo
from app.models.base import agora
from app.repositories import DocumentoRepositorio, PendenciaRepositorio, ProcessoRepositorio
from app.services import ingestao
from app.services.diagnostico_service import DiagnosticoService
from app.services.excecoes import NaoEncontrado, RegraDeNegocio
from app.services.nlp_service import NLPService
from app.services.processo_service import ProcessoService

EXTENSOES_PERMITIDAS = {".pdf"}
TAMANHO_MAXIMO_BYTES = 25 * 1024 * 1024


def nome_seguro(nome: str) -> str:
    base = Path(nome).name
    base = re.sub(r"[^A-Za-z0-9._-]+", "_", base)
    return base[:120] or "arquivo.pdf"


class DocumentoService:
    def __init__(self, sessao: Session, llm: LLMAdapter | None = None, certidoes: CertidaoAdapter | None = None):
        self.sessao = sessao
        self.config = obter_configuracao()
        self.documentos = DocumentoRepositorio(sessao)
        self.pendencias = PendenciaRepositorio(sessao)
        self.processos = ProcessoRepositorio(sessao)
        self.processo_service = ProcessoService(sessao)
        self.nlp = NLPService(sessao, llm or obter_llm_adapter())
        self.diagnostico = DiagnosticoService(sessao)
        self.certidoes = certidoes or obter_certidao_adapter()

    def listar(self, processo: Processo) -> list[Documento]:
        return self.documentos.listar_por_processo(processo.id)

    def obter(self, processo: Processo, documento_id: uuid.UUID) -> Documento:
        documento = self.documentos.obter(documento_id)
        if documento is None or documento.processo_id != processo.id:
            raise NaoEncontrado("Documento não encontrado")
        return documento

    def receber_upload(self, processo: Processo, tipo: TipoDocumento, nome_arquivo: str, conteudo: bytes, ator: str, origem: OrigemDocumento = OrigemDocumento.upload_manual) -> Documento:
        extensao = Path(nome_arquivo).suffix.lower()
        if extensao not in EXTENSOES_PERMITIDAS:
            raise RegraDeNegocio("Apenas arquivos PDF são aceitos")
        if not conteudo:
            raise RegraDeNegocio("Arquivo vazio")
        if len(conteudo) > TAMANHO_MAXIMO_BYTES:
            raise RegraDeNegocio("Arquivo excede o limite de 25 MB")
        pasta = self.config.upload_dir / str(processo.id)
        pasta.mkdir(parents=True, exist_ok=True)
        nome = nome_seguro(nome_arquivo)
        caminho = pasta / f"{uuid.uuid4().hex}_{nome}"
        caminho.write_bytes(conteudo)
        documento = Documento(
            processo_id=processo.id,
            tipo=tipo,
            nome_arquivo=nome,
            caminho_arquivo=str(caminho),
            tamanho_bytes=len(conteudo),
            status_validacao=StatusItem.pendente,
            origem=origem,
        )
        self.documentos.adicionar(documento)
        item = obter_item(tipo)
        rotulo = item.nome if item else tipo.value
        self.processo_service.registrar_evento(processo.id, TipoEvento.documento_recebido, f"{rotulo} recebida: {nome}", status=StatusItem.pendente, referencia_id=documento.id, ator=ator)
        self.sessao.commit()
        self.sessao.refresh(documento)
        return documento

    def processar(self, documento_id: uuid.UUID) -> Documento:
        documento = self.documentos.obter(documento_id)
        if documento is None:
            raise NaoEncontrado("Documento não encontrado")
        processo = self.processos.obter(documento.processo_id)
        documento.status_validacao = StatusItem.em_analise
        documento.processamento_iniciado_em = agora()
        documento.processamento_concluido_em = None
        documento.erro_processamento = None
        self.sessao.commit()
        try:
            self._executar_pipeline(processo, documento)
            documento.processamento_concluido_em = agora()
            self.sessao.commit()
        except Exception as erro:
            self.sessao.rollback()
            documento = self.documentos.obter(documento_id)
            documento.status_validacao = StatusItem.pendente
            documento.erro_processamento = str(erro)[:2000]
            documento.processamento_concluido_em = agora()
            self.processo_service.registrar_evento(documento.processo_id, TipoEvento.documento_erro, f"Falha ao processar {documento.nome_arquivo}: {str(erro)[:200]}", status=StatusItem.rejeitado, referencia_id=documento.id)
            self.sessao.commit()
        self.sessao.refresh(documento)
        return documento

    def _executar_pipeline(self, processo: Processo, documento: Documento) -> None:
        texto, metodo = ingestao.extrair_texto(Path(documento.caminho_arquivo))
        documento.texto_extraido = texto
        documento.metodo_extracao = metodo
        item = obter_item(documento.tipo)
        rotulo = item.nome if item else documento.tipo.value

        if not texto.strip():
            documento.status_validacao = StatusItem.rejeitado
            documento.motivo_status = "Não foi possível extrair texto do arquivo. Verifique a legibilidade e reenvie."
            self._registrar_documento_invalido(processo, documento, rotulo)
            return

        classificacao = self.nlp.classificar(texto, documento.tipo)
        documento.tipo_detectado = classificacao.tipo
        if classificacao.tipo != documento.tipo:
            esperado = rotulo
            detectado_item = obter_item(classificacao.tipo)
            detectado = detectado_item.nome if detectado_item else classificacao.tipo.value
            documento.status_validacao = StatusItem.rejeitado
            documento.motivo_status = f"O arquivo foi enviado como '{esperado}', mas o conteúdo corresponde a '{detectado}' (confiança {classificacao.confianca:.0%})."
            self._registrar_documento_invalido(processo, documento, rotulo)
            return

        self.nlp.extrair_e_persistir(documento)
        documento.status_validacao = StatusItem.concluido
        documento.motivo_status = f"Tipo confirmado ({classificacao.confianca:.0%}) e entidades extraídas pelo modelo {self.nlp.adapter.nome_modelo}."
        self._resolver_pendencias_do_tipo(processo, documento)
        self.processo_service.registrar_evento(processo.id, TipoEvento.documento_validado, f"{rotulo} validada automaticamente", status=StatusItem.concluido, referencia_id=documento.id)

        if documento.tipo == TipoDocumento.certidao_obito and processo.status == StatusProcesso.bloqueado:
            self.processo_service.desbloquear(processo)
            self.sessao.commit()
            self.buscar_certidoes_automaticas(processo)

        self.diagnostico.executar(processo)

    def _registrar_documento_invalido(self, processo: Processo, documento: Documento, rotulo: str) -> None:
        pendencia = Pendencia(
            processo_id=processo.id,
            categoria=CategoriaPendencia.documento_invalido,
            tipo_documento=documento.tipo,
            documento_id=documento.id,
            titulo=f"{rotulo} rejeitada",
            descricao=documento.motivo_status,
            bloqueante=False,
            link_portal=obter_item(documento.tipo).link_portal if obter_item(documento.tipo) else None,
        )
        self.pendencias.adicionar(pendencia)
        self.processo_service.registrar_evento(processo.id, TipoEvento.documento_rejeitado, f"{rotulo} rejeitada: {documento.nome_arquivo}", status=StatusItem.rejeitado, referencia_id=documento.id)

    def _resolver_pendencias_do_tipo(self, processo: Processo, documento: Documento) -> None:
        ausente = self.pendencias.obter_ausente(processo.id, documento.tipo)
        if ausente is not None and not ausente.resolvida:
            ausente.resolvida = True
            ausente.resolvida_em = agora()
            ausente.documento_id = documento.id
            self.processo_service.registrar_evento(processo.id, TipoEvento.pendencia_resolvida, f"Pendência resolvida: {ausente.titulo}", referencia_id=ausente.id)
        for invalida in self.pendencias.listar_por_categoria(processo.id, CategoriaPendencia.documento_invalido, apenas_abertas=True):
            if invalida.tipo_documento == documento.tipo:
                invalida.resolvida = True
                invalida.resolvida_em = agora()

    def reprocessar(self, documento: Documento) -> Documento:
        if not documento.caminho_arquivo or not Path(documento.caminho_arquivo).exists():
            raise RegraDeNegocio("Arquivo original não está mais disponível")
        return self.processar(documento.id)

    def remover(self, documento: Documento) -> None:
        if documento.caminho_arquivo:
            caminho = Path(documento.caminho_arquivo)
            if caminho.exists():
                caminho.unlink()
        for pendencia in self.pendencias.listar_por_processo(documento.processo_id):
            if pendencia.documento_id == documento.id and pendencia.categoria == CategoriaPendencia.documento_invalido:
                pendencia.resolvida = True
                pendencia.resolvida_em = agora()
        self.documentos.remover(documento)
        self.sessao.commit()

    def buscar_certidoes_automaticas(self, processo: Processo) -> list[Documento]:
        if processo.status == StatusProcesso.bloqueado:
            raise RegraDeNegocio("A busca automática só é executada após a validação da certidão de óbito")
        emitidos: list[Documento] = []
        for item in CATALOGO:
            if item.origem != OrigemDocumento.busca_automatica:
                continue
            if self.documentos.listar_validados_por_tipo(processo.id, item.tipo):
                continue
            resultado = self.certidoes.emitir(item.tipo, processo.nome_de_cujus, processo.cpf_de_cujus, processo.ultimo_domicilio)
            if not resultado.sucesso or not resultado.conteudo:
                continue
            documento = self.receber_upload(processo, item.tipo, resultado.nome_arquivo or f"{item.tipo.value}.pdf", resultado.conteudo, ator="busca automática", origem=OrigemDocumento.busca_automatica)
            emitidos.append(documento)
        for documento in emitidos:
            self.processar(documento.id)
        return emitidos


def processar_em_segundo_plano(documento_id: uuid.UUID) -> None:
    sessao = SessionLocal()
    try:
        DocumentoService(sessao).processar(documento_id)
    finally:
        sessao.close()
