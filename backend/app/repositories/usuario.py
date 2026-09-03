from sqlalchemy import select

from app.models import Usuario
from app.repositories.base import RepositorioBase


class UsuarioRepositorio(RepositorioBase[Usuario]):
    modelo = Usuario

    def obter_por_email(self, email: str) -> Usuario | None:
        return self.sessao.scalar(select(Usuario).where(Usuario.email == email.lower().strip()))
