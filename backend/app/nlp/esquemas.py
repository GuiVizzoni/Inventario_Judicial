from pydantic import BaseModel, Field

from app.dominio.enums import CategoriaEntidade, TipoDocumento


class CertidaoObitoExtraida(BaseModel):
    nome_completo: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.pessoa, "sinonimos": ["nome", "nome do falecido", "falecido", "nome completo"]})
    cpf: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.pessoa, "sinonimos": ["cpf", "cpf do falecido"]})
    data_nascimento: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.data, "sinonimos": ["data de nascimento", "nascimento"]})
    data_obito: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.data, "sinonimos": ["data do óbito", "data do obito", "data do falecimento", "falecimento", "óbito", "obito"]})
    naturalidade: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.local, "sinonimos": ["naturalidade", "natural de"]})
    estado_civil: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.pessoa, "sinonimos": ["estado civil"]})
    nome_conjuge: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.pessoa, "sinonimos": ["cônjuge", "conjuge", "nome do cônjuge", "casado com", "casada com"]})
    cartorio_registro: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.registro, "sinonimos": ["cartório", "cartorio", "cartório de registro", "serventia", "ofício de registro civil"]})


class CertidaoNegativaDebitoExtraida(BaseModel):
    tipo_certidao: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.fiscal, "sinonimos": ["tipo de certidão", "tipo", "esfera"]})
    orgao_emissor: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.fiscal, "sinonimos": ["órgão emissor", "orgao emissor", "emitida por", "emissor"]})
    nome_titular: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.pessoa, "sinonimos": ["nome", "contribuinte", "titular", "nome do contribuinte"]})
    cpf_titular: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.pessoa, "sinonimos": ["cpf", "cpf do contribuinte"]})
    data_emissao: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.data, "sinonimos": ["data de emissão", "data de emissao", "emitida em", "emissão"]})
    data_validade: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.data, "sinonimos": ["válida até", "valida ate", "validade", "data de validade"]})
    resultado: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.fiscal, "sinonimos": ["resultado", "situação", "situacao"]})


class CertidaoMatriculaExtraida(BaseModel):
    numero_matricula: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.registro, "sinonimos": ["matrícula", "matricula", "número da matrícula", "matrícula nº"]})
    cartorio: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.registro, "sinonimos": ["cartório", "cartorio", "registro de imóveis", "oficial de registro de imóveis"]})
    descricao_imovel: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.patrimonio, "sinonimos": ["imóvel", "imovel", "descrição", "descricao", "descrição do imóvel"]})
    area_m2: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.patrimonio, "sinonimos": ["área", "area", "área total", "metragem"]})
    localizacao: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.local, "sinonimos": ["localização", "localizacao", "endereço", "endereco", "situado"]})
    titulares: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.pessoa, "sinonimos": ["proprietário", "proprietario", "proprietários", "titulares", "titular", "em nome de"]})
    onus: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.patrimonio, "sinonimos": ["ônus", "onus", "gravames", "averbações"]})


class CertidaoCasamentoExtraida(BaseModel):
    nome_conjuge_1: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.pessoa, "sinonimos": ["nome do cônjuge 1", "contraente 1", "nubente 1", "cônjuge 1", "marido", "esposo"]})
    nome_conjuge_2: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.pessoa, "sinonimos": ["nome do cônjuge 2", "contraente 2", "nubente 2", "cônjuge 2", "mulher", "esposa"]})
    data_casamento: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.data, "sinonimos": ["data do casamento", "casamento", "celebrado em"]})
    regime_bens: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.registro, "sinonimos": ["regime de bens", "regime"]})
    cartorio: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.registro, "sinonimos": ["cartório", "cartorio", "serventia"]})


class CertidaoNascimentoExtraida(BaseModel):
    nome: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.pessoa, "sinonimos": ["nome", "nome completo", "registrando"]})
    cpf: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.pessoa, "sinonimos": ["cpf"]})
    data_nascimento: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.data, "sinonimos": ["data de nascimento", "nascimento", "nascido em", "nascida em"]})
    nome_pai: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.pessoa, "sinonimos": ["pai", "nome do pai", "filiação paterna"]})
    nome_mae: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.pessoa, "sinonimos": ["mãe", "mae", "nome da mãe", "filiação materna"]})
    cartorio: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.registro, "sinonimos": ["cartório", "cartorio", "serventia"]})


class DocumentoIdentidadeExtraido(BaseModel):
    nome: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.pessoa, "sinonimos": ["nome", "nome completo"]})
    cpf: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.pessoa, "sinonimos": ["cpf"]})
    rg: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.pessoa, "sinonimos": ["rg", "registro geral", "identidade"]})
    orgao_emissor: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.registro, "sinonimos": ["órgão expedidor", "orgao expedidor", "órgão emissor", "expedidor"]})
    data_nascimento: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.data, "sinonimos": ["data de nascimento", "nascimento"]})


class ExtratoBancarioExtraido(BaseModel):
    instituicao: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.patrimonio, "sinonimos": ["banco", "instituição", "instituicao", "instituição financeira"]})
    agencia: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.patrimonio, "sinonimos": ["agência", "agencia"]})
    conta: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.patrimonio, "sinonimos": ["conta", "conta corrente", "número da conta"]})
    titular: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.pessoa, "sinonimos": ["titular", "nome", "cliente"]})
    saldo: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.patrimonio, "sinonimos": ["saldo", "saldo total", "saldo em"]})
    data_referencia: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.data, "sinonimos": ["data de referência", "data de referencia", "posição em", "data base"]})


class DocumentoVeiculoExtraido(BaseModel):
    placa: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.patrimonio, "sinonimos": ["placa"]})
    renavam: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.registro, "sinonimos": ["renavam", "código renavam"]})
    marca_modelo: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.patrimonio, "sinonimos": ["marca/modelo", "marca modelo", "modelo", "veículo", "veiculo"]})
    ano: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.patrimonio, "sinonimos": ["ano", "ano fabricação/modelo", "ano modelo"]})
    proprietario: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.pessoa, "sinonimos": ["proprietário", "proprietario", "nome"]})


class DeclaracaoIrpfExtraida(BaseModel):
    nome_declarante: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.pessoa, "sinonimos": ["nome", "declarante", "nome do declarante", "contribuinte"]})
    cpf: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.pessoa, "sinonimos": ["cpf"]})
    ano_exercicio: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.fiscal, "sinonimos": ["exercício", "exercicio", "ano-calendário", "ano calendário", "ano"]})
    bens_declarados: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.patrimonio, "sinonimos": ["bens e direitos", "bens declarados", "bens"]})
    doacoes_realizadas: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.patrimonio, "sinonimos": ["doações efetuadas", "doacoes efetuadas", "doações", "doacoes", "doações realizadas"]})


class CertidaoCensecExtraida(BaseModel):
    nome_pesquisado: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.pessoa, "sinonimos": ["nome", "nome pesquisado", "pesquisado"]})
    cpf: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.pessoa, "sinonimos": ["cpf"]})
    resultado: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.registro, "sinonimos": ["resultado", "testamento", "situação", "situacao"]})
    data_emissao: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.data, "sinonimos": ["data de emissão", "data de emissao", "emitida em"]})


class DocumentoGenericoExtraido(BaseModel):
    titulo: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.outro, "sinonimos": ["título", "titulo", "assunto"]})
    pessoas_mencionadas: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.pessoa, "sinonimos": ["nome", "pessoas", "partes"]})
    datas_mencionadas: str | None = Field(default=None, json_schema_extra={"categoria": CategoriaEntidade.data, "sinonimos": ["data", "datas"]})


ESQUEMAS: dict[TipoDocumento, type[BaseModel]] = {
    TipoDocumento.certidao_obito: CertidaoObitoExtraida,
    TipoDocumento.cnd_federal: CertidaoNegativaDebitoExtraida,
    TipoDocumento.cnd_estadual: CertidaoNegativaDebitoExtraida,
    TipoDocumento.cnd_municipal: CertidaoNegativaDebitoExtraida,
    TipoDocumento.certidao_censec: CertidaoCensecExtraida,
    TipoDocumento.certidao_matricula: CertidaoMatriculaExtraida,
    TipoDocumento.certidao_casamento: CertidaoCasamentoExtraida,
    TipoDocumento.certidao_nascimento: CertidaoNascimentoExtraida,
    TipoDocumento.documento_identidade: DocumentoIdentidadeExtraido,
    TipoDocumento.extrato_bancario: ExtratoBancarioExtraido,
    TipoDocumento.documento_veiculo: DocumentoVeiculoExtraido,
    TipoDocumento.declaracao_irpf: DeclaracaoIrpfExtraida,
    TipoDocumento.outro: DocumentoGenericoExtraido,
}


def obter_esquema(tipo: TipoDocumento) -> type[BaseModel]:
    return ESQUEMAS.get(tipo, DocumentoGenericoExtraido)


def categoria_do_campo(esquema: type[BaseModel], campo: str) -> CategoriaEntidade:
    info = esquema.model_fields.get(campo)
    if info is None or not info.json_schema_extra:
        return CategoriaEntidade.outro
    return info.json_schema_extra.get("categoria", CategoriaEntidade.outro)


def sinonimos_do_campo(esquema: type[BaseModel], campo: str) -> list[str]:
    info = esquema.model_fields.get(campo)
    if info is None or not info.json_schema_extra:
        return []
    return list(info.json_schema_extra.get("sinonimos", []))
