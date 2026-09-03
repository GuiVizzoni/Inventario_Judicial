import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import app.models
from app.api.schemas import BemEntrada, HerdeiroEntrada, ProcessoEntrada
from app.db import Base, SessionLocal, engine
from app.dominio.enums import CategoriaBem, PapelUsuario, TipoDocumento
from app.repositories import UsuarioRepositorio
from app.services.auth_service import AuthService
from app.services.documento_service import DocumentoService
from app.services.processo_service import ProcessoService
from scripts.gerar_pdfs_exemplo import EXEMPLOS

EMAIL_ADMIN = "ana.ramos@escritorio.com.br"
SENHA_ADMIN = "inventario123"


def executar(reset: bool = False) -> None:
    if reset:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    sessao = SessionLocal()
    try:
        if UsuarioRepositorio(sessao).obter_por_email(EMAIL_ADMIN) is not None:
            print("Seed já aplicado. Use --reset para recriar o banco.")
            return
        auth = AuthService(sessao)
        ana = auth.criar_usuario("Ana Beatriz Ramos", EMAIL_ADMIN, SENHA_ADMIN, PapelUsuario.administrador, "SP 123.456")
        auth.criar_usuario("Guilherme Vizzoni", "guilherme@escritorio.com.br", SENHA_ADMIN, PapelUsuario.advogado, "ES 98.765")

        processos = ProcessoService(sessao)
        processo = processos.criar(
            ProcessoEntrada(
                nome_de_cujus="Roberto Mendes da Silva",
                cpf_de_cujus="321.654.987-00",
                data_obito=date(2026, 7, 10),
                ultimo_domicilio="São Paulo/SP",
                numero_processo="0004521-89.2026.8.26.0100",
                herdeiros=[
                    HerdeiroEntrada(nome="Carlos Mendes da Silva", cpf="123.456.789-00", parentesco="Filho"),
                    HerdeiroEntrada(nome="Juliana Mendes Ribeiro", cpf="234.567.890-11", parentesco="Filha"),
                    HerdeiroEntrada(nome="Marta Aparecida Silva", cpf="345.678.901-22", parentesco="Cônjuge", conjuge=True),
                    HerdeiroEntrada(nome="Pedro Henrique Mendes", cpf="456.789.012-33", parentesco="Filho"),
                ],
                bens=[
                    BemEntrada(descricao="Apartamento - Jardins, São Paulo/SP", categoria=CategoriaBem.imovel, valor_estimado=Decimal("1250000.00"), identificador="45.678"),
                    BemEntrada(descricao="Veículo Honda Civic 2022", categoria=CategoriaBem.movel, valor_estimado=Decimal("118000.00"), identificador="ABC1D23"),
                    BemEntrada(descricao="Conta corrente - Banco Itaú", categoria=CategoriaBem.financeiro, valor_estimado=Decimal("87400.00"), identificador="0912 / 45871-3"),
                    BemEntrada(descricao="Carteira de investimentos", categoria=CategoriaBem.financeiro, valor_estimado=Decimal("340200.00")),
                    BemEntrada(descricao="Sítio - Atibaia/SP", categoria=CategoriaBem.imovel_rural, valor_estimado=Decimal("620000.00")),
                ],
            ),
            ana,
        )

        documentos = DocumentoService(sessao)
        envios = [
            (TipoDocumento.certidao_obito, "certidao_obito_roberto.pdf"),
            (TipoDocumento.certidao_casamento, "certidao_casamento.pdf"),
            (TipoDocumento.certidao_nascimento, "certidao_nascimento_juliana.pdf"),
            (TipoDocumento.documento_identidade, "certidao_nascimento_carlos.pdf"),
            (TipoDocumento.certidao_matricula, "matricula_apartamento_jardins.pdf"),
            (TipoDocumento.certidao_matricula, "matricula_sitio_atibaia.pdf"),
            (TipoDocumento.declaracao_irpf, "irpf_2025_roberto.pdf"),
            (TipoDocumento.extrato_bancario, "extrato_itau.pdf"),
        ]
        for tipo, nome in envios:
            documento = documentos.receber_upload(processo, tipo, nome, EXEMPLOS[nome], ator=ana.nome)
            documentos.processar(documento.id)

        sessao.refresh(processo)
        print(f"Usuário: {EMAIL_ADMIN} / senha: {SENHA_ADMIN}")
        print(f"Processo criado: {processo.id} ({processo.nome_de_cujus}) - status {processo.status.value}")
        print(f"Documentos: {len(documentos.listar(processo))}")
    finally:
        sessao.close()


if __name__ == "__main__":
    executar(reset="--reset" in sys.argv)
