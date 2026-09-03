import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from datetime import timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.dominio.enums import (
    CategoriaBem,
    CategoriaEntidade,
    CategoriaPendencia,
    OrigemBem,
    OrigemDocumento,
    PapelUsuario,
    StatusItem,
    StatusProcesso,
    TipoDocumento,
    TipoEvento,
)


class Saida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="after")
    def fixar_fuso_utc(self):
        for nome in self.model_fields:
            valor = getattr(self, nome, None)
            if isinstance(valor, datetime) and valor.tzinfo is None:
                object.__setattr__(self, nome, valor.replace(tzinfo=timezone.utc))
        return self


class LoginEntrada(BaseModel):
    email: str
    senha: str


class UsuarioSaida(Saida):
    id: uuid.UUID
    nome: str
    email: str
    papel: PapelUsuario
    oab: str | None = None

    @property
    def iniciais(self) -> str:
        partes = [p for p in self.nome.split() if p]
        return "".join(p[0] for p in partes[:2]).upper()


class UsuarioEntrada(BaseModel):
    nome: str = Field(min_length=3, max_length=160)
    email: str = Field(min_length=5, max_length=160)
    senha: str = Field(min_length=6, max_length=72)
    papel: PapelUsuario = PapelUsuario.advogado
    oab: str | None = None


class TokenSaida(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioSaida


class HerdeiroEntrada(BaseModel):
    nome: str = Field(min_length=3, max_length=200)
    cpf: str | None = Field(default=None, max_length=14)
    parentesco: str = Field(min_length=2, max_length=60)
    pre_morto: bool = False
    conjuge: bool = False
    representa_herdeiro_id: uuid.UUID | None = None


class HerdeiroAtualizar(BaseModel):
    nome: str | None = Field(default=None, min_length=3, max_length=200)
    cpf: str | None = Field(default=None, max_length=14)
    parentesco: str | None = Field(default=None, min_length=2, max_length=60)
    pre_morto: bool | None = None
    conjuge: bool | None = None
    representa_herdeiro_id: uuid.UUID | None = None
    status: StatusItem | None = None


class HerdeiroSaida(Saida):
    id: uuid.UUID
    processo_id: uuid.UUID
    nome: str
    cpf: str | None
    parentesco: str
    pre_morto: bool
    conjuge: bool
    representa_herdeiro_id: uuid.UUID | None
    status: StatusItem
    criado_em: datetime


class BemEntrada(BaseModel):
    descricao: str = Field(min_length=3, max_length=300)
    categoria: CategoriaBem = CategoriaBem.outro
    valor_estimado: Decimal = Field(default=Decimal("0"), ge=0)
    identificador: str | None = Field(default=None, max_length=120)

    @field_validator("valor_estimado", mode="before")
    @classmethod
    def normalizar_valor(cls, valor: Any) -> Any:
        if isinstance(valor, str):
            limpo = valor.replace("R$", "").replace(".", "").replace(" ", "").replace(",", ".")
            return limpo or "0"
        return valor


class BemAtualizar(BaseModel):
    descricao: str | None = Field(default=None, min_length=3, max_length=300)
    categoria: CategoriaBem | None = None
    valor_estimado: Decimal | None = Field(default=None, ge=0)
    identificador: str | None = Field(default=None, max_length=120)
    status: StatusItem | None = None


class BemSaida(Saida):
    id: uuid.UUID
    processo_id: uuid.UUID
    descricao: str
    categoria: CategoriaBem
    valor_estimado: Decimal
    identificador: str | None
    origem: OrigemBem
    status: StatusItem
    criado_em: datetime


class ProcessoEntrada(BaseModel):
    nome_de_cujus: str = Field(min_length=3, max_length=200)
    cpf_de_cujus: str = Field(min_length=11, max_length=14)
    data_obito: date | None = None
    ultimo_domicilio: str | None = Field(default=None, max_length=200)
    numero_processo: str | None = Field(default=None, max_length=40)
    regime_bens: str | None = Field(default=None, max_length=80)
    herdeiros: list[HerdeiroEntrada] = Field(default_factory=list)
    bens: list[BemEntrada] = Field(default_factory=list)


class ProcessoAtualizar(BaseModel):
    nome_de_cujus: str | None = Field(default=None, min_length=3, max_length=200)
    cpf_de_cujus: str | None = Field(default=None, min_length=11, max_length=14)
    data_obito: date | None = None
    ultimo_domicilio: str | None = Field(default=None, max_length=200)
    numero_processo: str | None = Field(default=None, max_length=40)
    regime_bens: str | None = Field(default=None, max_length=80)
    status: StatusProcesso | None = None


class ProcessoSaida(Saida):
    id: uuid.UUID
    numero_processo: str | None
    status: StatusProcesso
    data_abertura: date | None
    data_obito: date | None
    nome_de_cujus: str
    cpf_de_cujus: str
    ultimo_domicilio: str | None
    regime_bens: str | None
    responsavel: UsuarioSaida
    criado_em: datetime


class EntidadeSaida(Saida):
    id: uuid.UUID
    chave: str
    valor: str
    categoria: CategoriaEntidade
    confianca: float
    modelo_llm: str
    versao_extracao: int
    duracao_ms: int | None
    extraido_em: datetime


class DocumentoSaida(Saida):
    id: uuid.UUID
    processo_id: uuid.UUID
    tipo: TipoDocumento
    tipo_nome: str
    categoria: str
    tipo_detectado: TipoDocumento | None
    nome_arquivo: str
    tamanho_bytes: int
    status_validacao: StatusItem
    motivo_status: str | None
    origem: OrigemDocumento
    metodo_extracao: str | None
    recebido_em: datetime
    processamento_iniciado_em: datetime | None
    processamento_concluido_em: datetime | None
    erro_processamento: str | None
    entidades: list[EntidadeSaida] = Field(default_factory=list)


class DocumentoDetalheSaida(DocumentoSaida):
    texto_extraido: str | None


class PendenciaSaida(Saida):
    id: uuid.UUID
    processo_id: uuid.UUID
    categoria: CategoriaPendencia
    tipo_documento: TipoDocumento | None
    documento_id: uuid.UUID | None
    titulo: str
    descricao: str | None
    bloqueante: bool
    link_portal: str | None
    resolvida: bool
    resolvida_em: datetime | None
    criado_em: datetime


class ItemChecklistSaida(BaseModel):
    tipo: TipoDocumento
    nome: str
    categoria: str
    status: StatusItem
    bloqueante: bool
    obrigatorio: bool
    origem: OrigemDocumento
    link_portal: str | None
    tutorial: str
    documentos: list[uuid.UUID] = Field(default_factory=list)


class ChecklistSaida(BaseModel):
    itens: list[ItemChecklistSaida]
    total: int
    concluidos: int
    percentual: int


class EventoSaida(Saida):
    id: uuid.UUID
    tipo: TipoEvento
    descricao: str
    status: StatusItem
    ator: str
    criado_em: datetime


class ResumoSaida(Saida):
    processo: ProcessoSaida
    fase: str
    progresso_documental: int
    documentos_enviados: int
    pendencias_ativas: int
    herdeiros_cadastrados: int
    bens_declarados: int
    patrimonio_total: Decimal
    ultima_movimentacao: datetime | None
    modulos: dict[str, int]
    atividades: list[EventoSaida]


class ResultadoAnaliseSaida(BaseModel):
    titulo: str
    resultado: str
    status: StatusItem
    documento_id: uuid.UUID | None = None


class AnaliseSaida(BaseModel):
    itens_analisados: int
    validados: int
    inconsistencias: int
    resultados: list[ResultadoAnaliseSaida]
    recomendacao: str


class ItemCatalogoSaida(BaseModel):
    tipo: TipoDocumento
    nome: str
    categoria: str
    bloqueante: bool
    obrigatorio: bool
    origem: OrigemDocumento
    link_portal: str | None
    tutorial: str


class MensagemSaida(BaseModel):
    mensagem: str
