from dataclasses import dataclass
from datetime import date, timedelta
from typing import Protocol

import pymupdf

from app.dominio.enums import TipoDocumento


@dataclass
class ResultadoCertidao:
    sucesso: bool
    nome_arquivo: str | None = None
    conteudo: bytes | None = None
    mensagem: str = ""


class CertidaoAdapter(Protocol):
    def emitir(self, tipo: TipoDocumento, nome: str, cpf: str, domicilio: str | None) -> ResultadoCertidao: ...


ORGAOS = {
    TipoDocumento.cnd_federal: ("Federal", "Secretaria da Receita Federal do Brasil - Procuradoria-Geral da Fazenda Nacional", "tributos federais"),
    TipoDocumento.cnd_estadual: ("Estadual", "Secretaria da Fazenda Estadual", "tributos estaduais"),
    TipoDocumento.cnd_municipal: ("Municipal", "Prefeitura Municipal - Secretaria de Finanças", "tributos municipais"),
}


class MockCertidaoAdapter:
    def emitir(self, tipo: TipoDocumento, nome: str, cpf: str, domicilio: str | None) -> ResultadoCertidao:
        if tipo not in ORGAOS:
            return ResultadoCertidao(sucesso=False, mensagem="Tipo de certidão não suportado pela busca automática")
        esfera, orgao, tributos = ORGAOS[tipo]
        emissao = date.today()
        validade = emissao + timedelta(days=180)
        linhas = [
            f"CERTIDÃO NEGATIVA DE DÉBITOS RELATIVOS A {tributos.upper()}",
            f"Tipo de certidão: {esfera}",
            f"Órgão emissor: {orgao}",
            f"Nome: {nome}",
            f"CPF: {cpf}",
            f"Domicílio: {domicilio or 'não informado'}",
            f"Data de emissão: {emissao.strftime('%d/%m/%Y')}",
            f"Válida até: {validade.strftime('%d/%m/%Y')}",
            "Resultado: NEGATIVA",
            "",
            "Certifica-se que não constam pendências em nome do contribuinte acima identificado.",
            "Documento gerado em ambiente de simulação para fins acadêmicos.",
        ]
        documento = pymupdf.open()
        pagina = documento.new_page()
        pagina.insert_text((50, 72), "\n".join(linhas), fontsize=10, fontname="helv")
        conteudo = documento.tobytes()
        documento.close()
        nome_arquivo = f"{tipo.value}_{cpf.replace('.', '').replace('-', '')}.pdf"
        return ResultadoCertidao(sucesso=True, nome_arquivo=nome_arquivo, conteudo=conteudo, mensagem="Certidão simulada emitida")
