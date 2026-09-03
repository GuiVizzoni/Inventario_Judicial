import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.api.schemas import (
    BemAtualizar,
    BemEntrada,
    HerdeiroAtualizar,
    HerdeiroEntrada,
    ProcessoAtualizar,
    ProcessoEntrada,
)
from app.dominio.catalogo_documentos import CATALOGO
from app.dominio.enums import CategoriaPendencia, OrigemBem, StatusItem, StatusProcesso, TipoEvento
from app.models import Bem, Evento, Herdeiro, Pendencia, Processo, Usuario
from app.models.base import agora
from app.repositories import (
    BemRepositorio,
    DocumentoRepositorio,
    EventoRepositorio,
    HerdeiroRepositorio,
    PendenciaRepositorio,
    ProcessoRepositorio,
)
from app.services.excecoes import AcessoNegado, NaoEncontrado, RegraDeNegocio

FASES = {
    StatusProcesso.bloqueado: "Aguardando certidão de óbito",
    StatusProcesso.aberto: "Instrução documental",
    StatusProcesso.concluido: "Pronto para partilha",
}


class ProcessoService:
    def __init__(self, sessao: Session):
        self.sessao = sessao
        self.processos = ProcessoRepositorio(sessao)
        self.documentos = DocumentoRepositorio(sessao)
        self.herdeiros = HerdeiroRepositorio(sessao)
        self.bens = BemRepositorio(sessao)
        self.pendencias = PendenciaRepositorio(sessao)
        self.eventos = EventoRepositorio(sessao)

    def registrar_evento(self, processo_id: uuid.UUID, tipo: TipoEvento, descricao: str, status: StatusItem = StatusItem.concluido, referencia_id: uuid.UUID | None = None, ator: str = "sistema") -> Evento:
        evento = Evento(processo_id=processo_id, tipo=tipo, descricao=descricao, status=status, referencia_id=referencia_id, ator=ator)
        return self.eventos.adicionar(evento)

    def criar(self, dados: ProcessoEntrada, usuario: Usuario) -> Processo:
        processo = Processo(
            nome_de_cujus=dados.nome_de_cujus.strip(),
            cpf_de_cujus=dados.cpf_de_cujus.strip(),
            data_obito=dados.data_obito,
            ultimo_domicilio=dados.ultimo_domicilio,
            numero_processo=dados.numero_processo,
            regime_bens=dados.regime_bens,
            status=StatusProcesso.bloqueado,
            responsavel_id=usuario.id,
        )
        self.processos.adicionar(processo)
        for item in CATALOGO:
            if not item.obrigatorio:
                continue
            self.pendencias.adicionar(
                Pendencia(
                    processo_id=processo.id,
                    categoria=CategoriaPendencia.documento_ausente,
                    tipo_documento=item.tipo,
                    titulo=item.nome,
                    descricao=item.tutorial,
                    bloqueante=item.bloqueante,
                    link_portal=item.link_portal,
                )
            )
        for herdeiro in dados.herdeiros:
            self._novo_herdeiro(processo, herdeiro)
        for bem in dados.bens:
            self._novo_bem(processo, bem)
        self.registrar_evento(processo.id, TipoEvento.processo_criado, f"Inventário de {processo.nome_de_cujus} cadastrado", ator=usuario.nome)
        self.sessao.commit()
        self.sessao.refresh(processo)
        return processo

    def listar(self, usuario: Usuario) -> list[Processo]:
        return self.processos.listar_por_responsavel(usuario.id)

    def obter(self, processo_id: uuid.UUID, usuario: Usuario) -> Processo:
        processo = self.processos.obter(processo_id)
        if processo is None:
            raise NaoEncontrado("Processo não encontrado")
        if processo.responsavel_id != usuario.id:
            raise AcessoNegado("Este processo pertence a outro responsável")
        return processo

    def atualizar(self, processo: Processo, dados: ProcessoAtualizar) -> Processo:
        for campo, valor in dados.model_dump(exclude_unset=True).items():
            setattr(processo, campo, valor)
        self.sessao.commit()
        self.sessao.refresh(processo)
        return processo

    def remover(self, processo: Processo) -> None:
        self.processos.remover(processo)
        self.sessao.commit()

    def desbloquear(self, processo: Processo) -> None:
        if processo.status != StatusProcesso.bloqueado:
            return
        processo.status = StatusProcesso.aberto
        processo.data_abertura = date.today()
        self.registrar_evento(processo.id, TipoEvento.processo_desbloqueado, "Certidão de óbito validada. Protocolo desbloqueado e instrução documental iniciada")
        self.sessao.flush()

    def fase(self, processo: Processo) -> str:
        return FASES[processo.status]

    def checklist(self, processo: Processo) -> dict:
        documentos = self.documentos.listar_por_processo(processo.id)
        itens: list[dict] = []
        concluidos = 0
        for item in CATALOGO:
            do_tipo = [d for d in documentos if d.tipo == item.tipo]
            status = StatusItem.nao_iniciado
            if any(d.status_validacao == StatusItem.concluido for d in do_tipo):
                status = StatusItem.concluido
            elif any(d.status_validacao == StatusItem.em_analise for d in do_tipo):
                status = StatusItem.em_analise
            elif any(d.status_validacao == StatusItem.pendente for d in do_tipo):
                status = StatusItem.pendente
            elif any(d.status_validacao == StatusItem.rejeitado for d in do_tipo):
                status = StatusItem.rejeitado
            if status == StatusItem.concluido:
                concluidos += 1
            itens.append(
                {
                    "tipo": item.tipo,
                    "nome": item.nome,
                    "categoria": item.categoria,
                    "status": status,
                    "bloqueante": item.bloqueante,
                    "obrigatorio": item.obrigatorio,
                    "origem": item.origem,
                    "link_portal": item.link_portal,
                    "tutorial": item.tutorial,
                    "documentos": [d.id for d in do_tipo],
                }
            )
        total = len(itens)
        return {"itens": itens, "total": total, "concluidos": concluidos, "percentual": round(concluidos * 100 / total) if total else 0}

    def resumo(self, processo: Processo) -> dict:
        documentos = self.documentos.listar_por_processo(processo.id)
        herdeiros = self.herdeiros.listar_por_processo(processo.id)
        bens = self.bens.listar_por_processo(processo.id)
        abertas = self.pendencias.listar_por_processo(processo.id, apenas_abertas=True)
        eventos = self.eventos.listar_recentes(processo.id, limite=8)
        checklist = self.checklist(processo)
        pendencias_documentos = [p for p in abertas if p.categoria in (CategoriaPendencia.documento_ausente, CategoriaPendencia.documento_invalido)]
        inconsistencias = [p for p in abertas if p.categoria == CategoriaPendencia.inconsistencia]
        return {
            "processo": processo,
            "fase": self.fase(processo),
            "progresso_documental": checklist["percentual"],
            "documentos_enviados": len(documentos),
            "pendencias_ativas": len(abertas),
            "herdeiros_cadastrados": len(herdeiros),
            "bens_declarados": len(bens),
            "patrimonio_total": sum((b.valor_estimado for b in bens), Decimal("0")),
            "ultima_movimentacao": eventos[0].criado_em if eventos else processo.criado_em,
            "modulos": {
                "documentos": len(pendencias_documentos),
                "herdeiros": len([h for h in herdeiros if h.status in (StatusItem.pendente, StatusItem.rejeitado)]),
                "patrimonio": len([b for b in bens if b.status in (StatusItem.pendente, StatusItem.rejeitado)]),
                "arvore": len([h for h in herdeiros if h.pre_morto and not any(x.representa_herdeiro_id == h.id for x in herdeiros)]),
                "analise": len(inconsistencias),
            },
            "atividades": eventos,
        }

    def _novo_herdeiro(self, processo: Processo, dados: HerdeiroEntrada) -> Herdeiro:
        if dados.representa_herdeiro_id is not None:
            representado = self.herdeiros.obter(dados.representa_herdeiro_id)
            if representado is None or representado.processo_id != processo.id:
                raise RegraDeNegocio("Herdeiro representado não pertence a este processo")
        herdeiro = Herdeiro(
            processo_id=processo.id,
            nome=dados.nome.strip(),
            cpf=dados.cpf,
            parentesco=dados.parentesco.strip(),
            pre_morto=dados.pre_morto,
            conjuge=dados.conjuge or dados.parentesco.strip().lower() in ("cônjuge", "conjuge", "companheiro", "companheira", "esposa", "esposo"),
            representa_herdeiro_id=dados.representa_herdeiro_id,
            status=StatusItem.pendente,
        )
        self.herdeiros.adicionar(herdeiro)
        self.registrar_evento(processo.id, TipoEvento.herdeiro_cadastrado, f"Herdeiro(a) {herdeiro.nome} cadastrado(a) como {herdeiro.parentesco}", referencia_id=herdeiro.id)
        return herdeiro

    def adicionar_herdeiro(self, processo: Processo, dados: HerdeiroEntrada) -> Herdeiro:
        herdeiro = self._novo_herdeiro(processo, dados)
        self.sessao.commit()
        self.sessao.refresh(herdeiro)
        return herdeiro

    def obter_herdeiro(self, processo: Processo, herdeiro_id: uuid.UUID) -> Herdeiro:
        herdeiro = self.herdeiros.obter(herdeiro_id)
        if herdeiro is None or herdeiro.processo_id != processo.id:
            raise NaoEncontrado("Herdeiro não encontrado")
        return herdeiro

    def atualizar_herdeiro(self, herdeiro: Herdeiro, dados: HerdeiroAtualizar) -> Herdeiro:
        alteracoes = dados.model_dump(exclude_unset=True)
        if alteracoes.get("representa_herdeiro_id") == herdeiro.id:
            raise RegraDeNegocio("Um herdeiro não pode representar a si mesmo")
        for campo, valor in alteracoes.items():
            setattr(herdeiro, campo, valor)
        self.sessao.commit()
        self.sessao.refresh(herdeiro)
        return herdeiro

    def remover_herdeiro(self, herdeiro: Herdeiro) -> None:
        self.herdeiros.remover(herdeiro)
        self.sessao.commit()

    def _novo_bem(self, processo: Processo, dados: BemEntrada) -> Bem:
        bem = Bem(
            processo_id=processo.id,
            descricao=dados.descricao.strip(),
            categoria=dados.categoria,
            valor_estimado=dados.valor_estimado,
            identificador=dados.identificador,
            origem=OrigemBem.formulario,
            status=StatusItem.pendente,
        )
        self.bens.adicionar(bem)
        self.registrar_evento(processo.id, TipoEvento.bem_declarado, f"Bem declarado: {bem.descricao}", referencia_id=bem.id)
        return bem

    def adicionar_bem(self, processo: Processo, dados: BemEntrada) -> Bem:
        bem = self._novo_bem(processo, dados)
        self.sessao.commit()
        self.sessao.refresh(bem)
        return bem

    def obter_bem(self, processo: Processo, bem_id: uuid.UUID) -> Bem:
        bem = self.bens.obter(bem_id)
        if bem is None or bem.processo_id != processo.id:
            raise NaoEncontrado("Bem não encontrado")
        return bem

    def atualizar_bem(self, bem: Bem, dados: BemAtualizar) -> Bem:
        for campo, valor in dados.model_dump(exclude_unset=True).items():
            setattr(bem, campo, valor)
        self.sessao.commit()
        self.sessao.refresh(bem)
        return bem

    def remover_bem(self, bem: Bem) -> None:
        self.bens.remover(bem)
        self.sessao.commit()

    def obter_pendencia(self, processo: Processo, pendencia_id: uuid.UUID) -> Pendencia:
        pendencia = self.pendencias.obter(pendencia_id)
        if pendencia is None or pendencia.processo_id != processo.id:
            raise NaoEncontrado("Pendência não encontrada")
        return pendencia

    def resolver_pendencia(self, pendencia: Pendencia, ator: str) -> Pendencia:
        if pendencia.bloqueante and pendencia.categoria == CategoriaPendencia.documento_ausente:
            raise RegraDeNegocio("Pendência bloqueante só é resolvida com a validação do documento")
        pendencia.resolvida = True
        pendencia.resolvida_em = agora()
        self.registrar_evento(pendencia.processo_id, TipoEvento.pendencia_resolvida, f"Pendência resolvida manualmente: {pendencia.titulo}", referencia_id=pendencia.id, ator=ator)
        self.sessao.commit()
        self.sessao.refresh(pendencia)
        return pendencia
