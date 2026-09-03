from dataclasses import dataclass

from app.dominio.enums import OrigemDocumento, TipoDocumento


@dataclass(frozen=True)
class ItemCatalogo:
    tipo: TipoDocumento
    nome: str
    categoria: str
    bloqueante: bool
    obrigatorio: bool
    origem: OrigemDocumento
    link_portal: str | None
    tutorial: str


CATALOGO: list[ItemCatalogo] = [
    ItemCatalogo(
        tipo=TipoDocumento.certidao_obito,
        nome="Certidão de óbito",
        categoria="Certidões",
        bloqueante=True,
        obrigatorio=True,
        origem=OrigemDocumento.upload_manual,
        link_portal="https://www.registrocivil.org.br/",
        tutorial="Solicite a segunda via no cartório de registro civil onde o óbito foi lavrado ou pelo portal Registro Civil. O prazo legal para abertura do inventário é de 60 dias a contar do óbito (art. 611 do CPC).",
    ),
    ItemCatalogo(
        tipo=TipoDocumento.cnd_federal,
        nome="Certidão negativa de débitos federais",
        categoria="Certidões fiscais",
        bloqueante=False,
        obrigatorio=True,
        origem=OrigemDocumento.busca_automatica,
        link_portal="https://servicos.receita.fazenda.gov.br/Servicos/certidaointernet/PF/Emitir",
        tutorial="Emitida automaticamente pelo sistema junto à Receita Federal a partir do CPF do de cujus. Caso a emissão automática falhe, emita manualmente no portal e envie o arquivo.",
    ),
    ItemCatalogo(
        tipo=TipoDocumento.cnd_estadual,
        nome="Certidão negativa de débitos estaduais",
        categoria="Certidões fiscais",
        bloqueante=False,
        obrigatorio=True,
        origem=OrigemDocumento.busca_automatica,
        link_portal=None,
        tutorial="Emitida automaticamente pelo sistema junto à Secretaria da Fazenda do estado do último domicílio do de cujus.",
    ),
    ItemCatalogo(
        tipo=TipoDocumento.cnd_municipal,
        nome="Certidão negativa de débitos municipais",
        categoria="Certidões fiscais",
        bloqueante=False,
        obrigatorio=True,
        origem=OrigemDocumento.busca_automatica,
        link_portal=None,
        tutorial="Emitida automaticamente pelo sistema junto à prefeitura do último domicílio do de cujus.",
    ),
    ItemCatalogo(
        tipo=TipoDocumento.certidao_censec,
        nome="Certidão do CENSEC (testamento)",
        categoria="Certidões",
        bloqueante=False,
        obrigatorio=True,
        origem=OrigemDocumento.upload_manual,
        link_portal="https://censec.org.br/",
        tutorial="Acesse o portal da Central Notarial de Serviços Eletrônicos Compartilhados com seu certificado digital, solicite a certidão de existência ou inexistência de testamento em nome do de cujus e envie o PDF recebido.",
    ),
    ItemCatalogo(
        tipo=TipoDocumento.certidao_matricula,
        nome="Certidão de matrícula atualizada dos imóveis",
        categoria="Bens imóveis",
        bloqueante=False,
        obrigatorio=True,
        origem=OrigemDocumento.upload_manual,
        link_portal="https://www.registradores.org.br/",
        tutorial="Solicite a matrícula atualizada de cada imóvel no portal e-Registradores ou diretamente no cartório de registro de imóveis competente. Envie uma certidão por imóvel.",
    ),
    ItemCatalogo(
        tipo=TipoDocumento.certidao_casamento,
        nome="Certidão de casamento do de cujus",
        categoria="Certidões",
        bloqueante=False,
        obrigatorio=False,
        origem=OrigemDocumento.upload_manual,
        link_portal="https://www.registrocivil.org.br/",
        tutorial="Necessária quando o de cujus era casado ou vivia em união estável. Define o regime de bens e a meação do cônjuge.",
    ),
    ItemCatalogo(
        tipo=TipoDocumento.certidao_nascimento,
        nome="Certidão de nascimento dos herdeiros",
        categoria="Certidões",
        bloqueante=False,
        obrigatorio=False,
        origem=OrigemDocumento.upload_manual,
        link_portal="https://www.registrocivil.org.br/",
        tutorial="Envie a certidão de nascimento ou casamento de cada herdeiro para comprovar a filiação e o estado civil.",
    ),
    ItemCatalogo(
        tipo=TipoDocumento.documento_identidade,
        nome="RG e CPF dos herdeiros",
        categoria="Documentos pessoais",
        bloqueante=False,
        obrigatorio=False,
        origem=OrigemDocumento.upload_manual,
        link_portal=None,
        tutorial="Digitalize frente e verso do documento de identidade de cada herdeiro em um único PDF legível.",
    ),
    ItemCatalogo(
        tipo=TipoDocumento.extrato_bancario,
        nome="Extratos bancários e de investimentos",
        categoria="Bens financeiros",
        bloqueante=False,
        obrigatorio=False,
        origem=OrigemDocumento.upload_manual,
        link_portal=None,
        tutorial="Solicite às instituições financeiras o extrato com o saldo na data do óbito. Consultas ao SisbaJud são feitas pelo juízo, não pelo sistema.",
    ),
    ItemCatalogo(
        tipo=TipoDocumento.documento_veiculo,
        nome="Documento de veículos (CRLV)",
        categoria="Bens móveis",
        bloqueante=False,
        obrigatorio=False,
        origem=OrigemDocumento.upload_manual,
        link_portal="https://www.gov.br/pt-br/servicos/obter-crlv-digital",
        tutorial="Obtenha o CRLV digital de cada veículo no aplicativo Carteira Digital de Trânsito e envie o PDF.",
    ),
    ItemCatalogo(
        tipo=TipoDocumento.declaracao_irpf,
        nome="Declaração de Imposto de Renda do de cujus",
        categoria="Documentos fiscais",
        bloqueante=False,
        obrigatorio=False,
        origem=OrigemDocumento.upload_manual,
        link_portal="https://www.gov.br/receitafederal/pt-br/servicos/meu-imposto-de-renda",
        tutorial="A última declaração entregue relaciona bens, direitos e doações feitas em vida, usados para verificar a necessidade de colação.",
    ),
]

POR_TIPO: dict[TipoDocumento, ItemCatalogo] = {item.tipo: item for item in CATALOGO}


def obter_item(tipo: TipoDocumento) -> ItemCatalogo | None:
    return POR_TIPO.get(tipo)
