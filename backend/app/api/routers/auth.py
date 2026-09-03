from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import usuario_atual
from app.api.schemas import LoginEntrada, TokenSaida, UsuarioEntrada, UsuarioSaida
from app.db import obter_sessao
from app.dominio.enums import PapelUsuario
from app.models import Usuario
from app.services.auth_service import AuthService, criar_token

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=TokenSaida)
def login(dados: LoginEntrada, sessao: Session = Depends(obter_sessao)) -> TokenSaida:
    usuario = AuthService(sessao).autenticar(dados.email, dados.senha)
    if usuario is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="E-mail ou senha inválidos")
    return TokenSaida(access_token=criar_token(usuario), usuario=UsuarioSaida.model_validate(usuario))


@router.get("/me", response_model=UsuarioSaida)
def me(usuario: Usuario = Depends(usuario_atual)) -> Usuario:
    return usuario


@router.post("/usuarios", response_model=UsuarioSaida, status_code=status.HTTP_201_CREATED)
def criar_usuario(dados: UsuarioEntrada, usuario: Usuario = Depends(usuario_atual), sessao: Session = Depends(obter_sessao)) -> Usuario:
    if usuario.papel != PapelUsuario.administrador:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Apenas administradores podem cadastrar usuários")
    try:
        return AuthService(sessao).criar_usuario(dados.nome, dados.email, dados.senha, dados.papel, dados.oab)
    except ValueError as erro:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(erro)) from erro
