import re
import unicodedata

from pydantic import BaseModel

from app.dominio.enums import TipoDocumento
from app.integrations.llm_adapter import ResultadoClassificacao, ResultadoExtracao
from app.nlp.esquemas import sinonimos_do_campo

PALAVRAS_CHAVE: dict[TipoDocumento, list[tuple[str, int]]] = {
    TipoDocumento.certidao_obito: [("certidao de obito", 4), ("obito", 1), ("falecimento", 1), ("faleceu", 1)],
    TipoDocumento.cnd_federal: [("certidao negativa", 1), ("receita federal", 3), ("fazenda nacional", 2), ("tributos federais", 3), ("debitos federais", 3), ("uniao", 1)],
    TipoDocumento.cnd_estadual: [("certidao negativa", 1), ("secretaria da fazenda", 2), ("tributos estaduais", 3), ("debitos estaduais", 3), ("icms", 1), ("fazenda estadual", 2)],
    TipoDocumento.cnd_municipal: [("certidao negativa", 1), ("prefeitura", 3), ("tributos municipais", 3), ("debitos municipais", 3), ("iptu", 1), ("municipio", 1)],
    TipoDocumento.certidao_censec: [("censec", 4), ("testamento", 2), ("central notarial", 2)],
    TipoDocumento.certidao_matricula: [("matricula", 2), ("registro de imoveis", 3), ("imovel", 1), ("averbacao", 1), ("averbacoes", 1)],
    TipoDocumento.certidao_casamento: [("certidao de casamento", 4), ("casamento", 1), ("regime de bens", 1), ("nubente", 1), ("nubentes", 1)],
    TipoDocumento.certidao_nascimento: [("certidao de nascimento", 4), ("registrando", 2), ("filiacao", 1)],
    TipoDocumento.documento_identidade: [("carteira de identidade", 3), ("registro geral", 2), ("rg", 1), ("orgao expedidor", 2)],
    TipoDocumento.extrato_bancario: [("extrato", 3), ("saldo", 1), ("agencia", 1), ("conta corrente", 1)],
    TipoDocumento.documento_veiculo: [("crlv", 4), ("renavam", 3), ("placa", 1), ("veiculo", 1)],
    TipoDocumento.declaracao_irpf: [("imposto de renda", 3), ("declaracao de ajuste anual", 3), ("bens e direitos", 1), ("doacoes", 1)],
}

PADRAO_CPF = re.compile(r"\d{3}\.?\d{3}\.?\d{3}-?\d{2}")
PADRAO_DATA = re.compile(r"\d{2}/\d{2}/\d{4}")
PADRAO_PAR = re.compile(r"^\s*([^:]{2,60}?)\s*:\s*(.+?)\s*$")


def normalizar(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", sem_acento).strip().lower()


class MockLLMAdapter:
    nome_modelo = "mock-heuristico"

    def classificar(self, texto: str, tipo_esperado: TipoDocumento) -> ResultadoClassificacao:
        normalizado = normalizar(texto)
        pontuacoes: dict[TipoDocumento, int] = {}
        for tipo, palavras in PALAVRAS_CHAVE.items():
            total = 0
            for palavra, peso in palavras:
                if re.search(r"\b" + re.escape(palavra) + r"\b", normalizado):
                    total += peso
            pontuacoes[tipo] = total
        melhor_tipo, melhor_pontuacao = max(pontuacoes.items(), key=lambda item: item[1])
        if melhor_pontuacao == 0:
            return ResultadoClassificacao(tipo=TipoDocumento.outro, confianca=0.2, justificativa="Nenhuma palavra-chave reconhecida")
        empatados = [t for t, p in pontuacoes.items() if p == melhor_pontuacao]
        if tipo_esperado in empatados:
            melhor_tipo = tipo_esperado
        confianca = min(0.95, 0.5 + 0.1 * melhor_pontuacao)
        return ResultadoClassificacao(tipo=melhor_tipo, confianca=confianca, justificativa=f"Pontuação por palavras-chave: {melhor_pontuacao}")

    def extrair(self, texto: str, tipo: TipoDocumento, esquema: type[BaseModel]) -> ResultadoExtracao:
        pares = self._pares_rotulo_valor(texto)
        dados: dict[str, str | None] = {}
        for campo in esquema.model_fields:
            valor = None
            for sinonimo in sinonimos_do_campo(esquema, campo):
                valor = pares.get(normalizar(sinonimo))
                if valor:
                    break
            if not valor and "cpf" in campo:
                encontrado = PADRAO_CPF.search(texto)
                valor = encontrado.group(0) if encontrado else None
            dados[campo] = valor
        preenchidos = sum(1 for v in dados.values() if v)
        total = max(1, len(dados))
        return ResultadoExtracao(dados=dados, confianca=round(preenchidos / total, 2), modelo=self.nome_modelo)

    def _pares_rotulo_valor(self, texto: str) -> dict[str, str]:
        pares: dict[str, str] = {}
        for linha in texto.splitlines():
            encontrado = PADRAO_PAR.match(linha)
            if not encontrado:
                continue
            rotulo = normalizar(encontrado.group(1))
            valor = encontrado.group(2).strip()
            if rotulo and valor and rotulo not in pares:
                pares[rotulo] = valor
        return pares
