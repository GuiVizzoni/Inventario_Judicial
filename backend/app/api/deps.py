import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db import obter_sessao
from app.models import Processo, Usuario
from app.repositories import UsuarioRepositorio
from app.services.auth_service import decodificar_token
from app.services.processo_service import ProcessoService

seguranca = HTTPBearer(auto_error=False)


def usuario_atual(
    credenciais: HTTPAuthorizationCredentials | None = Depends(seguranca),
    sessao: Session = Depends(obter_sessao),
) -> Usuario:
    if credenciais is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de acesso ausente")
    usuario_id = decodificar_token(credenciais.credentials)
    if usuario_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido ou expirado")
    usuario = UsuarioRepositorio(sessao).obter(usuario_id)
    if usuario is None or not usuario.ativo:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário inativo ou inexistente")
    return usuario


def processo_atual(
    processo_id: uuid.UUID,
    usuario: Usuario = Depends(usuario_atual),
    sessao: Session = Depends(obter_sessao),
) -> Processo:
    return ProcessoService(sessao).obter(processo_id, usuario)
