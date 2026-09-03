import enum


class StatusItem(str, enum.Enum):
    nao_iniciado = "nao_iniciado"
    pendente = "pendente"
    em_analise = "em_analise"
    concluido = "concluido"
    rejeitado = "rejeitado"


class StatusProcesso(str, enum.Enum):
    bloqueado = "bloqueado"
    aberto = "aberto"
    concluido = "concluido"


class TipoDocumento(str, enum.Enum):
    certidao_obito = "certidao_obito"
    cnd_federal = "cnd_federal"
    cnd_estadual = "cnd_estadual"
    cnd_municipal = "cnd_municipal"
    certidao_censec = "certidao_censec"
    certidao_matricula = "certidao_matricula"
    certidao_casamento = "certidao_casamento"
    certidao_nascimento = "certidao_nascimento"
    documento_identidade = "documento_identidade"
    extrato_bancario = "extrato_bancario"
    documento_veiculo = "documento_veiculo"
    declaracao_irpf = "declaracao_irpf"
    outro = "outro"


class OrigemDocumento(str, enum.Enum):
    upload_manual = "upload_manual"
    busca_automatica = "busca_automatica"


class CategoriaPendencia(str, enum.Enum):
    documento_ausente = "documento_ausente"
    documento_invalido = "documento_invalido"
    inconsistencia = "inconsistencia"


class CategoriaEntidade(str, enum.Enum):
    pessoa = "pessoa"
    data = "data"
    local = "local"
    patrimonio = "patrimonio"
    fiscal = "fiscal"
    registro = "registro"
    outro = "outro"


class CategoriaBem(str, enum.Enum):
    imovel = "imovel"
    imovel_rural = "imovel_rural"
    movel = "movel"
    financeiro = "financeiro"
    outro = "outro"


class OrigemBem(str, enum.Enum):
    formulario = "formulario"
    documento = "documento"


class PapelUsuario(str, enum.Enum):
    advogado = "advogado"
    administrador = "administrador"


class TipoEvento(str, enum.Enum):
    processo_criado = "processo_criado"
    processo_desbloqueado = "processo_desbloqueado"
    documento_recebido = "documento_recebido"
    documento_validado = "documento_validado"
    documento_rejeitado = "documento_rejeitado"
    documento_erro = "documento_erro"
    herdeiro_cadastrado = "herdeiro_cadastrado"
    bem_declarado = "bem_declarado"
    inconsistencia_detectada = "inconsistencia_detectada"
    pendencia_resolvida = "pendencia_resolvida"
