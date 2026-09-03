import time

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.dominio.enums import TipoDocumento
from app.integrations.fabrica import obter_llm_adapter
from app.integrations.llm_adapter import LLMAdapter, ResultadoClassificacao
from app.models import Documento, EntidadeExtraida
from app.nlp.esquemas import categoria_do_campo, obter_esquema
from app.repositories import EntidadeExtraidaRepositorio


class NLPService:
    def __init__(self, sessao: Session, adapter: LLMAdapter | None = None):
        self.sessao = sessao
        self.adapter = adapter or obter_llm_adapter()
        self.entidades = EntidadeExtraidaRepositorio(sessao)

    def classificar(self, texto: str, tipo_esperado: TipoDocumento) -> ResultadoClassificacao:
        return self.adapter.classificar(texto, tipo_esperado)

    def extrair_e_persistir(self, documento: Documento) -> list[EntidadeExtraida]:
        esquema = obter_esquema(documento.tipo)
        inicio = time.perf_counter()
        resultado = self.adapter.extrair(documento.texto_extraido or "", documento.tipo, esquema)
        duracao_ms = int((time.perf_counter() - inicio) * 1000)
        try:
            validado = esquema.model_validate(resultado.dados)
        except ValidationError as erro:
            raise ValueError(f"Resposta do modelo inválida para o esquema {esquema.__name__}: {erro}") from erro
        versao = self.entidades.ultima_versao(documento.id) + 1
        criadas: list[EntidadeExtraida] = []
        for campo, valor in validado.model_dump().items():
            if valor is None or valor == "" or valor == []:
                continue
            if isinstance(valor, list):
                valor = "; ".join(str(v) for v in valor)
            entidade = EntidadeExtraida(
                documento_id=documento.id,
                categoria=categoria_do_campo(esquema, campo),
                chave=campo,
                valor=str(valor),
                confianca=resultado.confianca,
                modelo_llm=resultado.modelo or self.adapter.nome_modelo,
                versao_extracao=versao,
                duracao_ms=duracao_ms,
            )
            self.entidades.adicionar(entidade)
            criadas.append(entidade)
        return criadas
