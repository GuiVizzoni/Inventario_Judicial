from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import obter_configuracao

config = obter_configuracao()

argumentos = {"check_same_thread": False} if config.database_url.startswith("sqlite") else {}
engine = create_engine(config.database_url, connect_args=argumentos, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def obter_sessao() -> Generator[Session, None, None]:
    sessao = SessionLocal()
    try:
        yield sessao
    finally:
        sessao.close()
