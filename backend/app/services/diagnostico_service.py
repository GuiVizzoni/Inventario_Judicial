import re
import unicodedata
import uuid
from datetime import date, datetime

from sqlalchemy.orm import Session

from app.dominio.catalogo_documentos import CATALOGO, obter_item
from app.dominio.enums import CategoriaBem, CategoriaPendencia, StatusItem, StatusProcesso, TipoDocumento, TipoEvento
from app.models import Documento, Evento, Herdeiro, Pendencia, Processo
from app.models.base import agora
from app.repositories import (
    BemRepositorio,
    DocumentoRepositorio,
    EntidadeExtraidaRepositorio,
    EventoRepositorio,
    HerdeiroRepositorio,
    PendenciaRepositorio,
)

PRAZO_ABERTURA_DIAS = 60


def somente_digitos(valor: str | None) -> str:
    return re.sub(r"\D", "", valor or "")


def normalizar_nome(valor: str | None) -> str:
    sem_acento = unicodedata.normalize("NFKD", valor or "").encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", sem_acento).strip().lower()


def interpretar_data(valor: str | None) -> date | None:
    if not valor:
        return None
    for formato in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(valor.strip(), formato).date()
        except ValueError:
            continue
    return None


class DiagnosticoService:
    def __init__(self, sessao: Session):
        self.sessao = sessao
        self.documentos = DocumentoRepositorio(sessao)
        self.entidades = EntidadeExtraidaRepositorio(sessao)
        self.herdeiros = HerdeiroRepositorio(sessao)
        self.bens = BemRepositorio(sessao)
        self.pendencias = PendenciaRepositorio(sessao)
        self.eventos = EventoRepositorio(sessao)

    def executar(self, processo: Processo) -> list[Pendencia]:
        encontradas: list[tuple[str, str, uuid.UUID | None]] = []
        herdeiros = self.herdeiros.listar_por_processo(processo.id)
        bens = self.bens.listar_por_processo(processo.id)

        for documento in self.documentos.listar_validados_por_tipo(processo.id, TipoDocumento.certidao_obito)[:1]:
            dados = self.entidades.como_dicionario(documento.id)
            self._verificar_certidao_obito(processo, dados, documento, herdeiros, encontradas)

        for tipo in (TipoDocumento.cnd_federal, TipoDocumento.cnd_estadual, TipoDocumento.cnd_municipal):
            for documento in self.documentos.listar_validados_por_tipo(processo.id, tipo):
                dados = self.entidades.como_dicionario(documento.id)
                self._verificar_cnd(processo, dados, documento, encontradas)

        for documento in self.documentos.listar_validados_por_tipo(processo.id, TipoDocumento.certidao_matricula):
            dados = self.entidades.como_dicionario(documento.id)
            self._verificar_matricula(processo, dados, documento, bens, encontradas)

        for documento in self.documentos.listar_validados_por_tipo(processo.id, TipoDocumento.declaracao_irpf):
            dados = self.entidades.como_dicionario(documento.id)
            self._verificar_irpf(processo, dados, documento, encontradas)

        for documento in self.documentos.listar_validados_por_tipo(processo.id, TipoDocumento.certidao_censec):
            dados = self.entidades.como_dicionario(documento.id)
            self._verificar_censec(dados, documento, encontradas)

        for documento in self.documentos.listar_validados_por_tipo(processo.id, TipoDocumento.certidao_casamento)[:1]:
            dados = self.entidades.como_dicionario(documento.id)
            self._verificar_casamento(processo, dados, documento, encontradas)

        for documento in self.documentos.listar_validados_por_tipo(processo.id, TipoDocumento.certidao_nascimento):
            dados = self.entidades.como_dicionario(documento.id)
            self._verificar_nascimento(processo, dados, documento, herdeiros, encontradas)

        for documento in self.documentos.listar_validados_por_tipo(processo.id, TipoDocumento.documento_identidade):
            dados = self.entidades.como_dicionario(documento.id)
            self._verificar_identidade(dados, documento, herdeiros, encontradas)

        self._verificar_prazo(processo, encontradas)
        return self._sincronizar_pendencias(processo, encontradas)

    def _verificar_certidao_obito(self, processo: Processo, dados: dict[str, str], documento: Documento, herdeiros: list[Herdeiro], encontradas: list) -> None:
        cpf_certidao = somente_digitos(dados.get("cpf"))
        if cpf_certidao and cpf_certidao != somente_digitos(processo.cpf_de_cujus):
            encontradas.append(("CPF do de cujus divergente", f"O CPF informado no cadastro ({processo.cpf_de_cujus}) difere do constante na certidão de óbito ({dados.get('cpf')}).", documento.id))
        nome_certidao = normalizar_nome(dados.get("nome_completo"))
        if nome_certidao and nome_certidao != normalizar_nome(processo.nome_de_cujus):
            encontradas.append(("Nome do de cujus divergente", f"O nome informado no cadastro ({processo.nome_de_cujus}) difere do constante na certidão de óbito ({dados.get('nome_completo')}).", documento.id))
        data_certidao = interpretar_data(dados.get("data_obito"))
        if data_certidao and processo.data_obito and data_certidao != processo.data_obito:
            encontradas.append(("Data do óbito divergente", f"A data informada no cadastro ({processo.data_obito.strftime('%d/%m/%Y')}) difere da constante na certidão ({dados.get('data_obito')}).", documento.id))
        if data_certidao and not processo.data_obito:
            processo.data_obito = data_certidao
        estado_civil = normalizar_nome(dados.get("estado_civil"))
        tem_conjuge = any(h.conjuge for h in herdeiros)
        if estado_civil.startswith("casad") and not tem_conjuge:
            encontradas.append(("Cônjuge não cadastrado", "A certidão de óbito indica que o de cujus era casado, mas nenhum cônjuge foi cadastrado entre os herdeiros.", documento.id))
        nome_conjuge = normalizar_nome(dados.get("nome_conjuge"))
        if nome_conjuge and tem_conjuge:
            conjuges = [normalizar_nome(h.nome) for h in herdeiros if h.conjuge]
            if nome_conjuge not in conjuges:
                encontradas.append(("Nome do cônjuge divergente", f"A certidão de óbito indica o cônjuge {dados.get('nome_conjuge')}, que não corresponde ao cônjuge cadastrado.", documento.id))

    def _verificar_cnd(self, processo: Processo, dados: dict[str, str], documento: Documento, encontradas: list) -> None:
        resultado = normalizar_nome(dados.get("resultado"))
        item = obter_item(documento.tipo)
        nome_certidao = item.nome if item else documento.tipo.value
        if resultado and "positiva" in resultado and "efeito" not in resultado:
            encontradas.append((f"Débitos apontados na {nome_certidao.lower()}", "A certidão retornou resultado positivo. Os débitos do espólio precisam ser quitados ou garantidos antes da partilha.", documento.id))
        cpf_certidao = somente_digitos(dados.get("cpf_titular"))
        if cpf_certidao and cpf_certidao != somente_digitos(processo.cpf_de_cujus):
            encontradas.append((f"CPF divergente na {nome_certidao.lower()}", f"A certidão foi emitida para o CPF {dados.get('cpf_titular')}, diferente do CPF do de cujus.", documento.id))
        validade = interpretar_data(dados.get("data_validade"))
        if validade and validade < date.today():
            encontradas.append((f"{nome_certidao} vencida", f"A certidão venceu em {dados.get('data_validade')} e precisa ser reemitida.", documento.id))

    def _verificar_matricula(self, processo: Processo, dados: dict[str, str], documento: Documento, bens, encontradas: list) -> None:
        titulares = normalizar_nome(dados.get("titulares"))
        nome = normalizar_nome(processo.nome_de_cujus)
        if titulares and nome not in titulares:
            encontradas.append(("Imóvel não registrado em nome do de cujus", f"A matrícula {dados.get('numero_matricula') or documento.nome_arquivo} aponta como titular(es) {dados.get('titulares')}, sem menção ao de cujus.", documento.id))
        numero = somente_digitos(dados.get("numero_matricula"))
        imoveis = [b for b in bens if b.categoria in (CategoriaBem.imovel, CategoriaBem.imovel_rural)]
        if numero:
            declarado = any(somente_digitos(b.identificador) == numero or numero in somente_digitos(b.descricao) for b in imoveis)
            if not declarado:
                encontradas.append(("Imóvel não declarado no patrimônio", f"A matrícula {dados.get('numero_matricula')} foi recebida, mas nenhum bem imóvel com esse identificador consta na declaração de bens.", documento.id))
        onus = normalizar_nome(dados.get("onus"))
        if onus and onus not in ("nenhum", "nao constam", "nao consta", "sem onus", "nada consta"):
            encontradas.append(("Ônus registrado sobre imóvel", f"A matrícula {dados.get('numero_matricula') or documento.nome_arquivo} registra ônus: {dados.get('onus')}.", documento.id))

    def _verificar_irpf(self, processo: Processo, dados: dict[str, str], documento: Documento, encontradas: list) -> None:
        doacoes = (dados.get("doacoes_realizadas") or "").strip()
        if doacoes and normalizar_nome(doacoes) not in ("nenhuma", "nao", "nao ha", "nao constam"):
            encontradas.append(("Possível necessidade de colação", f"A declaração de imposto de renda registra doações em vida: {doacoes}. Verifique a aplicação do art. 2.002 do Código Civil.", documento.id))
        cpf_declarante = somente_digitos(dados.get("cpf"))
        if cpf_declarante and cpf_declarante != somente_digitos(processo.cpf_de_cujus):
            encontradas.append(("Declaração de IR de outro contribuinte", f"A declaração enviada pertence ao CPF {dados.get('cpf')}, diferente do CPF do de cujus.", documento.id))

    def _verificar_censec(self, dados: dict[str, str], documento: Documento, encontradas: list) -> None:
        resultado = normalizar_nome(dados.get("resultado"))
        if resultado and "inexist" not in resultado and ("exist" in resultado or "positiv" in resultado or "consta" in resultado and "nao consta" not in resultado):
            encontradas.append(("Testamento registrado", "A certidão do CENSEC indica a existência de testamento em nome do de cujus. O inventário deve observar as disposições testamentárias.", documento.id))

    def _verificar_casamento(self, processo: Processo, dados: dict[str, str], documento: Documento, encontradas: list) -> None:
        regime = (dados.get("regime_bens") or "").strip()
        if regime and not processo.regime_bens:
            processo.regime_bens = regime
        elif regime and normalizar_nome(regime) != normalizar_nome(processo.regime_bens):
            encontradas.append(("Regime de bens divergente", f"O cadastro indica regime {processo.regime_bens}, mas a certidão de casamento registra {regime}.", documento.id))

    def _verificar_nascimento(self, processo: Processo, dados: dict[str, str], documento: Documento, herdeiros: list[Herdeiro], encontradas: list) -> None:
        nome = normalizar_nome(dados.get("nome"))
        if not nome:
            return
        herdeiro = next((h for h in herdeiros if normalizar_nome(h.nome) == nome), None)
        if herdeiro is None:
            encontradas.append(("Certidão de nascimento sem herdeiro correspondente", f"A certidão de {dados.get('nome')} foi recebida, mas não há herdeiro cadastrado com esse nome.", documento.id))
            return
        de_cujus = normalizar_nome(processo.nome_de_cujus)
        pais = [normalizar_nome(dados.get("nome_pai")), normalizar_nome(dados.get("nome_mae"))]
        if any(pais) and de_cujus not in pais:
            encontradas.append(("Filiação não confirmada", f"A certidão de nascimento de {herdeiro.nome} não menciona o de cujus como pai ou mãe.", documento.id))
            herdeiro.status = StatusItem.pendente
        else:
            herdeiro.status = StatusItem.concluido

    def _verificar_identidade(self, dados: dict[str, str], documento: Documento, herdeiros: list[Herdeiro], encontradas: list) -> None:
        nome = normalizar_nome(dados.get("nome"))
        if not nome:
            return
        herdeiro = next((h for h in herdeiros if normalizar_nome(h.nome) == nome), None)
        if herdeiro is None:
            return
        cpf_documento = somente_digitos(dados.get("cpf"))
        if cpf_documento and herdeiro.cpf and cpf_documento != somente_digitos(herdeiro.cpf):
            encontradas.append((f"CPF divergente do herdeiro {herdeiro.nome}", f"O documento de identidade informa o CPF {dados.get('cpf')}, diferente do cadastrado ({herdeiro.cpf}).", documento.id))
        elif herdeiro.status != StatusItem.concluido:
            herdeiro.status = StatusItem.concluido

    def _verificar_prazo(self, processo: Processo, encontradas: list) -> None:
        if processo.status != StatusProcesso.bloqueado or not processo.data_obito:
            return
        dias = (date.today() - processo.data_obito).days
        if dias > PRAZO_ABERTURA_DIAS:
            encontradas.append(("Prazo legal de abertura excedido", f"Já se passaram {dias} dias desde o óbito e o protocolo continua bloqueado. O art. 611 do CPC prevê abertura em até {PRAZO_ABERTURA_DIAS} dias.", None))

    def _sincronizar_pendencias(self, processo: Processo, encontradas: list[tuple[str, str, uuid.UUID | None]]) -> list[Pendencia]:
        abertas = self.pendencias.listar_por_categoria(processo.id, CategoriaPendencia.inconsistencia, apenas_abertas=True)
        por_titulo = {p.titulo: p for p in abertas}
        titulos_atuais = {titulo for titulo, _, _ in encontradas}
        for pendencia in abertas:
            if pendencia.titulo not in titulos_atuais:
                pendencia.resolvida = True
                pendencia.resolvida_em = agora()
                self.eventos.adicionar(Evento(processo_id=processo.id, tipo=TipoEvento.pendencia_resolvida, descricao=f"Inconsistência sanada: {pendencia.titulo}", status=StatusItem.concluido, referencia_id=pendencia.id))
        resultado: list[Pendencia] = []
        for titulo, descricao, documento_id in encontradas:
            existente = por_titulo.get(titulo)
            if existente is not None:
                existente.descricao = descricao
                resultado.append(existente)
                continue
            nova = Pendencia(
                processo_id=processo.id,
                categoria=CategoriaPendencia.inconsistencia,
                tipo_documento=None,
                documento_id=documento_id,
                titulo=titulo,
                descricao=descricao,
                bloqueante=False,
            )
            self.pendencias.adicionar(nova)
            self.eventos.adicionar(Evento(processo_id=processo.id, tipo=TipoEvento.inconsistencia_detectada, descricao=f"Inconsistência identificada: {titulo}", status=StatusItem.pendente, referencia_id=nova.id))
            resultado.append(nova)
        self.sessao.flush()
        return resultado

    def arvore_genealogica(self, processo: Processo) -> dict:
        herdeiros = self.herdeiros.listar_por_processo(processo.id)
        por_id = {h.id: h for h in herdeiros}
        conjuges = [h for h in herdeiros if h.conjuge]
        representantes: dict[uuid.UUID, list[Herdeiro]] = {}
        for h in herdeiros:
            if h.representa_herdeiro_id:
                representantes.setdefault(h.representa_herdeiro_id, []).append(h)

        def no(h: Herdeiro) -> dict:
            return {
                "id": str(h.id),
                "nome": h.nome,
                "cpf": h.cpf,
                "parentesco": h.parentesco,
                "pre_morto": h.pre_morto,
                "status": h.status.value,
                "representantes": [no(r) for r in representantes.get(h.id, [])],
            }

        diretos = [h for h in herdeiros if not h.conjuge and not h.representa_herdeiro_id]
        observacoes: list[str] = []
        confirmados = [h for h in diretos if h.status == StatusItem.concluido]
        if diretos:
            observacoes.append(f"Filiação confirmada por documentos para {len(confirmados)} de {len(diretos)} herdeiro(s) direto(s).")
        pre_mortos = [h for h in herdeiros if h.pre_morto]
        for h in pre_mortos:
            quantidade = len(representantes.get(h.id, []))
            if quantidade:
                observacoes.append(f"{h.nome} é pré-morto(a) e será representado(a) por {quantidade} descendente(s), conforme o art. 1.851 do Código Civil.")
            else:
                observacoes.append(f"{h.nome} é pré-morto(a) e não possui representantes cadastrados. Verifique a existência de descendentes.")
        if processo.regime_bens:
            observacoes.append(f"Regime de bens do casamento: {processo.regime_bens}.")
        elif conjuges:
            observacoes.append("Regime de bens ainda não confirmado. Envie a certidão de casamento.")
        inconsistencias = self.pendencias.listar_por_categoria(processo.id, CategoriaPendencia.inconsistencia, apenas_abertas=True)
        if not inconsistencias:
            observacoes.append("Não foram identificados indícios de outros herdeiros necessários.")
        return {
            "de_cujus": {"nome": processo.nome_de_cujus, "cpf": processo.cpf_de_cujus, "data_obito": processo.data_obito.isoformat() if processo.data_obito else None},
            "conjuges": [no(h) for h in conjuges],
            "herdeiros": [no(h) for h in diretos],
            "observacoes": observacoes,
        }

    def resumo_analise(self, processo: Processo) -> dict:
        documentos = self.documentos.listar_por_processo(processo.id)
        analisados = [d for d in documentos if d.status_validacao in (StatusItem.concluido, StatusItem.rejeitado)]
        validados = [d for d in analisados if d.status_validacao == StatusItem.concluido]
        inconsistencias = self.pendencias.listar_por_categoria(processo.id, CategoriaPendencia.inconsistencia, apenas_abertas=True)
        resultados: list[dict] = []
        for d in documentos:
            item = obter_item(d.tipo)
            titulo = f"{item.nome if item else d.tipo.value} — {d.nome_arquivo}"
            if d.status_validacao == StatusItem.concluido:
                texto = d.motivo_status or "Documento validado e entidades extraídas com sucesso"
            elif d.status_validacao == StatusItem.rejeitado:
                texto = d.motivo_status or "Documento rejeitado"
            elif d.status_validacao == StatusItem.em_analise:
                texto = "Em processamento pelo pipeline de NLP"
            else:
                texto = d.erro_processamento or "Aguardando processamento"
            resultados.append({"titulo": titulo, "resultado": texto, "status": d.status_validacao.value, "documento_id": str(d.id)})
        for p in inconsistencias:
            resultados.append({"titulo": p.titulo, "resultado": p.descricao or "", "status": StatusItem.pendente.value, "documento_id": str(p.documento_id) if p.documento_id else None})
        return {
            "itens_analisados": len(analisados) + len(inconsistencias),
            "validados": len(validados),
            "inconsistencias": len(inconsistencias) + len([d for d in analisados if d.status_validacao == StatusItem.rejeitado]),
            "resultados": resultados,
            "recomendacao": self.recomendacao(processo),
        }

    def recomendacao(self, processo: Processo) -> str:
        abertas = self.pendencias.listar_por_processo(processo.id, apenas_abertas=True)
        bloqueantes = [p for p in abertas if p.bloqueante]
        if bloqueantes:
            return f"Envie a {bloqueantes[0].titulo.lower()} para desbloquear o protocolo. Sem ela o inventário não pode ser aberto."
        invalidos = [p for p in abertas if p.categoria == CategoriaPendencia.documento_invalido]
        inconsistencias = [p for p in abertas if p.categoria == CategoriaPendencia.inconsistencia]
        ausentes = [p for p in abertas if p.categoria == CategoriaPendencia.documento_ausente]
        partes: list[str] = []
        if invalidos:
            partes.append(f"reenviar {len(invalidos)} documento(s) rejeitado(s) ({invalidos[0].titulo.lower()})")
        if inconsistencias:
            partes.append(f"sanar {len(inconsistencias)} inconsistência(s), começando por: {inconsistencias[0].titulo.lower()}")
        if ausentes:
            nomes = ", ".join(p.titulo.lower() for p in ausentes[:3])
            partes.append(f"providenciar {len(ausentes)} documento(s) obrigatório(s) ainda ausente(s) ({nomes})")
        if not partes:
            return "Documentação mínima validada sem ressalvas. O processo pode avançar para a fase de partilha, a critério do profissional responsável."
        return "Antes de prosseguir para a partilha, recomenda-se " + "; ".join(partes) + "."
