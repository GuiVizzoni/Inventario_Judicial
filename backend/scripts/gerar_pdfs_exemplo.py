import sys
from pathlib import Path

import pymupdf

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))


def gerar_pdf(titulo: str, linhas: list[str], rodape: str = "Documento fictício gerado para fins acadêmicos.") -> bytes:
    documento = pymupdf.open()
    pagina = documento.new_page()
    pagina.insert_text((50, 60), titulo, fontsize=13, fontname="helv")
    pagina.insert_text((50, 95), "\n".join(linhas), fontsize=10, fontname="helv")
    pagina.insert_text((50, 780), rodape, fontsize=8, fontname="helv")
    conteudo = documento.tobytes()
    documento.close()
    return conteudo


def certidao_obito(nome: str, cpf: str, data_nascimento: str, data_obito: str, naturalidade: str, estado_civil: str, conjuge: str | None, cartorio: str) -> bytes:
    linhas = [
        "REGISTRO CIVIL DAS PESSOAS NATURAIS",
        f"Cartório: {cartorio}",
        "",
        f"Nome do falecido: {nome}",
        f"CPF: {cpf}",
        f"Data de nascimento: {data_nascimento}",
        f"Naturalidade: {naturalidade}",
        f"Estado civil: {estado_civil}",
    ]
    if conjuge:
        linhas.append(f"Cônjuge: {conjuge}")
    linhas += [
        f"Data do óbito: {data_obito}",
        "Causa: natural",
        "",
        "Certifico que o assento de óbito acima foi lavrado nesta serventia.",
    ]
    return gerar_pdf("CERTIDÃO DE ÓBITO", linhas)


def certidao_casamento(conjuge_1: str, conjuge_2: str, data_casamento: str, regime_bens: str, cartorio: str) -> bytes:
    linhas = [
        "REGISTRO CIVIL DAS PESSOAS NATURAIS",
        f"Cartório: {cartorio}",
        "",
        f"Cônjuge 1: {conjuge_1}",
        f"Cônjuge 2: {conjuge_2}",
        f"Data do casamento: {data_casamento}",
        f"Regime de bens: {regime_bens}",
        "",
        "Certifico que os nubentes acima contraíram matrimônio perante esta serventia.",
    ]
    return gerar_pdf("CERTIDÃO DE CASAMENTO", linhas)


def certidao_nascimento(nome: str, cpf: str | None, data_nascimento: str, pai: str, mae: str, cartorio: str) -> bytes:
    linhas = [
        "REGISTRO CIVIL DAS PESSOAS NATURAIS",
        f"Cartório: {cartorio}",
        "",
        f"Nome: {nome}",
        f"Data de nascimento: {data_nascimento}",
        f"Pai: {pai}",
        f"Mãe: {mae}",
    ]
    if cpf:
        linhas.append(f"CPF: {cpf}")
    linhas += ["", "Certifico que o assento de nascimento do registrando acima consta desta serventia."]
    return gerar_pdf("CERTIDÃO DE NASCIMENTO", linhas)


def documento_identidade(nome: str, cpf: str, rg: str, orgao: str, data_nascimento: str) -> bytes:
    linhas = [
        "REPÚBLICA FEDERATIVA DO BRASIL",
        "",
        f"Nome: {nome}",
        f"Registro Geral: {rg}",
        f"Órgão expedidor: {orgao}",
        f"CPF: {cpf}",
        f"Data de nascimento: {data_nascimento}",
    ]
    return gerar_pdf("CARTEIRA DE IDENTIDADE", linhas)


def certidao_matricula(numero: str, cartorio: str, descricao: str, area: str, localizacao: str, titulares: str, onus: str) -> bytes:
    linhas = [
        f"Cartório: {cartorio}",
        f"Matrícula: {numero}",
        "",
        f"Imóvel: {descricao}",
        f"Área: {area}",
        f"Localização: {localizacao}",
        f"Proprietários: {titulares}",
        f"Ônus: {onus}",
        "",
        "Certifico que a presente é cópia fiel da matrícula constante do Registro de Imóveis.",
    ]
    return gerar_pdf("CERTIDÃO DE MATRÍCULA DE IMÓVEL", linhas)


def declaracao_irpf(nome: str, cpf: str, exercicio: str, bens: str, doacoes: str) -> bytes:
    linhas = [
        "DECLARAÇÃO DE AJUSTE ANUAL - IMPOSTO DE RENDA PESSOA FÍSICA",
        "",
        f"Nome: {nome}",
        f"CPF: {cpf}",
        f"Exercício: {exercicio}",
        f"Bens e direitos: {bens}",
        f"Doações efetuadas: {doacoes}",
    ]
    return gerar_pdf("RECIBO DE ENTREGA - IMPOSTO DE RENDA", linhas)


def extrato_bancario(banco: str, agencia: str, conta: str, titular: str, saldo: str, data_referencia: str) -> bytes:
    linhas = [
        f"Banco: {banco}",
        f"Agência: {agencia}",
        f"Conta corrente: {conta}",
        f"Titular: {titular}",
        f"Data de referência: {data_referencia}",
        f"Saldo: {saldo}",
    ]
    return gerar_pdf("EXTRATO DE CONTA CORRENTE", linhas)


def certidao_censec(nome: str, cpf: str, resultado: str, data_emissao: str) -> bytes:
    linhas = [
        "CENSEC - CENTRAL NOTARIAL DE SERVIÇOS ELETRÔNICOS COMPARTILHADOS",
        "",
        f"Nome: {nome}",
        f"CPF: {cpf}",
        f"Resultado: {resultado}",
        f"Data de emissão: {data_emissao}",
    ]
    return gerar_pdf("CERTIDÃO DE TESTAMENTO", linhas)


DE_CUJUS = {"nome": "Roberto Mendes da Silva", "cpf": "321.654.987-00"}

EXEMPLOS: dict[str, bytes] = {
    "certidao_obito_roberto.pdf": certidao_obito(DE_CUJUS["nome"], DE_CUJUS["cpf"], "14/03/1958", "10/07/2026", "São Paulo/SP", "Casado", "Marta Aparecida Silva", "2º Ofício de Registro Civil de São Paulo"),
    "certidao_obito_cpf_divergente.pdf": certidao_obito(DE_CUJUS["nome"], "999.888.777-66", "14/03/1958", "10/07/2026", "São Paulo/SP", "Casado", "Marta Aparecida Silva", "2º Ofício de Registro Civil de São Paulo"),
    "certidao_casamento.pdf": certidao_casamento(DE_CUJUS["nome"], "Marta Aparecida Silva", "22/11/1986", "Comunhão parcial de bens", "2º Ofício de Registro Civil de São Paulo"),
    "certidao_nascimento_juliana.pdf": certidao_nascimento("Juliana Mendes Ribeiro", "234.567.890-11", "05/09/1990", DE_CUJUS["nome"], "Marta Aparecida Silva", "2º Ofício de Registro Civil de São Paulo"),
    "certidao_nascimento_carlos.pdf": certidao_nascimento("Carlos Mendes da Silva", "123.456.789-00", "18/02/1988", DE_CUJUS["nome"], "Marta Aparecida Silva", "2º Ofício de Registro Civil de São Paulo"),
    "rg_pedro_henrique.pdf": documento_identidade("Pedro Henrique Mendes", "456.789.012-33", "44.555.666-7", "SSP/SP", "30/01/1995"),
    "matricula_apartamento_jardins.pdf": certidao_matricula("45.678", "4º Registro de Imóveis de São Paulo", "Apartamento nº 81, Edifício Jardins, com 1 vaga de garagem", "142,00 m2", "Rua Haddock Lobo, 1200, Jardins, São Paulo/SP", "Roberto Mendes da Silva e Marta Aparecida Silva", "Nenhum"),
    "matricula_sitio_atibaia.pdf": certidao_matricula("78.910", "Registro de Imóveis de Atibaia", "Sítio Boa Vista, área rural com casa sede", "24.200,00 m2", "Estrada Municipal da Usina, km 4, Atibaia/SP", "Roberto Mendes da Silva", "Nenhum"),
    "irpf_2025_roberto.pdf": declaracao_irpf(DE_CUJUS["nome"], DE_CUJUS["cpf"], "2025", "Apartamento Jardins matrícula 45.678; Sítio Atibaia matrícula 78.910; Veículo Honda Civic 2022", "Doação em dinheiro de R$ 50.000,00 a Pedro Henrique Mendes em 12/03/2024"),
    "extrato_itau.pdf": extrato_bancario("Banco Itaú", "0912", "45871-3", DE_CUJUS["nome"], "R$ 87.400,00", "10/07/2026"),
    "censec_roberto.pdf": certidao_censec(DE_CUJUS["nome"], DE_CUJUS["cpf"], "Não consta testamento registrado", "01/08/2026"),
}


def salvar_exemplos(destino: Path) -> list[Path]:
    destino.mkdir(parents=True, exist_ok=True)
    gerados: list[Path] = []
    for nome, conteudo in EXEMPLOS.items():
        caminho = destino / nome
        caminho.write_bytes(conteudo)
        gerados.append(caminho)
    return gerados


if __name__ == "__main__":
    pasta = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "exemplos"
    for caminho in salvar_exemplos(pasta):
        print(caminho)
