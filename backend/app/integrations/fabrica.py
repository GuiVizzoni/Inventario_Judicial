from app.config import Configuracao, obter_configuracao
from app.integrations.certidao_adapter import CertidaoAdapter, MockCertidaoAdapter
from app.integrations.llm_adapter import LLMAdapter
from app.integrations.llm_mock import MockLLMAdapter
from app.integrations.llm_openai import OpenAILLMAdapter


def obter_llm_adapter(config: Configuracao | None = None) -> LLMAdapter:
    config = config or obter_configuracao()
    if config.llm_provider == "openai":
        return OpenAILLMAdapter(modelo=config.llm_modelo, api_key=config.openai_api_key)
    return MockLLMAdapter()


def obter_certidao_adapter(config: Configuracao | None = None) -> CertidaoAdapter:
    config = config or obter_configuracao()
    return MockCertidaoAdapter()
