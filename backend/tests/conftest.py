import os
import sys
import tempfile
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

PASTA_TEMP = Path(tempfile.mkdtemp(prefix="inventario_teste_"))
os.environ["DATABASE_URL"] = f"sqlite:///{(PASTA_TEMP / 'teste.db').as_posix()}"
os.environ["UPLOAD_DIR"] = (PASTA_TEMP / "uploads").as_posix()
os.environ["LLM_PROVIDER"] = "mock"
os.environ["JWT_SECRET"] = "segredo-de-teste"

from fastapi.testclient import TestClient

import app.models
from app.db import Base, SessionLocal, engine
from app.dominio.enums import PapelUsuario
from app.main import app as aplicacao
from app.services.auth_service import AuthService


@pytest.fixture(scope="session")
def cliente():
    Base.metadata.create_all(bind=engine)
    sessao = SessionLocal()
    try:
        auth = AuthService(sessao)
        auth.criar_usuario("Ana Beatriz Ramos", "ana@teste.com", "senha123", PapelUsuario.administrador)
        auth.criar_usuario("Outro Advogado", "outro@teste.com", "senha123", PapelUsuario.advogado)
    finally:
        sessao.close()
    with TestClient(aplicacao) as c:
        yield c


def _token(cliente: TestClient, email: str) -> str:
    resposta = cliente.post("/auth/login", json={"email": email, "senha": "senha123"})
    assert resposta.status_code == 200, resposta.text
    return resposta.json()["access_token"]


@pytest.fixture(scope="session")
def cabecalhos(cliente):
    return {"Authorization": f"Bearer {_token(cliente, 'ana@teste.com')}"}


@pytest.fixture(scope="session")
def cabecalhos_outro(cliente):
    return {"Authorization": f"Bearer {_token(cliente, 'outro@teste.com')}"}
