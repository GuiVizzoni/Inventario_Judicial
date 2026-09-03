from app.repositories.bem import BemRepositorio
from app.repositories.documento import DocumentoRepositorio
from app.repositories.entidade_extraida import EntidadeExtraidaRepositorio
from app.repositories.evento import EventoRepositorio
from app.repositories.herdeiro import HerdeiroRepositorio
from app.repositories.pendencia import PendenciaRepositorio
from app.repositories.processo import ProcessoRepositorio
from app.repositories.usuario import UsuarioRepositorio

__all__ = [
    "BemRepositorio",
    "DocumentoRepositorio",
    "EntidadeExtraidaRepositorio",
    "EventoRepositorio",
    "HerdeiroRepositorio",
    "PendenciaRepositorio",
    "ProcessoRepositorio",
    "UsuarioRepositorio",
]
