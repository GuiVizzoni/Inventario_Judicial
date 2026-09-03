from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuracao(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_nome: str = "Plataforma de Inventário Judicial - Backend"
    database_url: str = "sqlite:///./inventario.db"
    jwt_secret: str = "troque-esta-chave-em-producao"
    jwt_algoritmo: str = "HS256"
    jwt_expiracao_minutos: int = 480
    upload_dir: Path = Path("uploads")
    cors_origins: str = "http://localhost:3000"
    llm_provider: str = "mock"
    llm_modelo: str = "gpt-4o"
    openai_api_key: str = ""
    ocr_limiar_caracteres: int = 200
    ocr_idioma: str = "por"
    certidao_provider: str = "mock"

    @property
    def origens_cors(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def obter_configuracao() -> Configuracao:
    return Configuracao()
