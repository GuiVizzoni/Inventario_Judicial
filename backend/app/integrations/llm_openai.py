from pydantic import BaseModel

from app.dominio.enums import TipoDocumento
from app.integrations.llm_adapter import ResultadoClassificacao, ResultadoExtracao

MENSAGEM = (
    "O adaptador OpenAI ainda não foi implementado. O módulo de IA deve implementar "
    "classificar() e extrair() usando LangChain, respeitando os esquemas Pydantic de app/nlp/esquemas.py. "
    "Enquanto isso, use LLM_PROVIDER=mock."
)


class OpenAILLMAdapter:
    def __init__(self, modelo: str, api_key: str):
        self.nome_modelo = modelo
        self.api_key = api_key

    def classificar(self, texto: str, tipo_esperado: TipoDocumento) -> ResultadoClassificacao:
        raise NotImplementedError(MENSAGEM)

    def extrair(self, texto: str, tipo: TipoDocumento, esquema: type[BaseModel]) -> ResultadoExtracao:
        raise NotImplementedError(MENSAGEM)
