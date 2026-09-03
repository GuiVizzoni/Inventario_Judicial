import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from sqlalchemy.orm import Session

from app.config import obter_configuracao
from app.dominio.enums import PapelUsuario
from app.models import Usuario
from app.repositories import UsuarioRepositorio


def gerar_hash(senha: str) -> str:
    return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_senha(senha: str, senha_hash: str) -> bool:
    try:
        return bcrypt.checkpw(senha.encode("utf-8"), senha_hash.encode("utf-8"))
    except ValueError:
        return False


def criar_token(usuario: Usuario) -> str:
    config = obter_configuracao()
    expira = datetime.now(timezone.utc) + timedelta(minutes=config.jwt_expiracao_minutos)
    payload = {"sub": str(usuario.id), "email": usuario.email, "papel": usuario.papel.value, "exp": expira}
    return jwt.encode(payload, config.jwt_secret, algorithm=config.jwt_algoritmo)


def decodificar_token(token: str) -> uuid.UUID | None:
    config = obter_configuracao()
    try:
        payload = jwt.decode(token, config.jwt_secret, algorithms=[config.jwt_algoritmo])
        return uuid.UUID(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        return None


class AuthService:
    def __init__(self, sessao: Session):
        self.sessao = sessao
        self.usuarios = UsuarioRepositorio(sessao)

    def autenticar(self, email: str, senha: str) -> Usuario | None:
        usuario = self.usuarios.obter_por_email(email)
        if usuario is None or not usuario.ativo:
            return None
        if not verificar_senha(senha, usuario.senha_hash):
            return None
        return usuario

    def criar_usuario(self, nome: str, email: str, senha: str, papel: PapelUsuario = PapelUsuario.advogado, oab: str | None = None) -> Usuario:
        existente = self.usuarios.obter_por_email(email)
        if existente is not None:
            raise ValueError("E-mail já cadastrado")
        usuario = Usuario(nome=nome, email=email.lower().strip(), senha_hash=gerar_hash(senha), papel=papel, oab=oab)
        self.usuarios.adicionar(usuario)
        self.usuarios.salvar()
        return usuario
