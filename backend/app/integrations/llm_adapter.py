from dataclasses import dataclass, field
from typing import Any, Protocol

from pydantic import BaseModel

from app.dominio.enums import TipoDocumento


@dataclass
class ResultadoClassificacao:
    tipo: TipoDocumento
    confianca: float
    justificativa: str = ""


@dataclass
class ResultadoExtracao:
    dados: dict[str, Any] = field(default_factory=dict)
    confianca: float = 0.0
    modelo: str = ""


class LLMAdapter(Protocol):
    nome_modelo: str

    def classificar(self, texto: str, tipo_esperado: TipoDocumento) -> ResultadoClassificacao: ...

    def extrair(self, texto: str, tipo: TipoDocumento, esquema: type[BaseModel]) -> ResultadoExtracao: ...
