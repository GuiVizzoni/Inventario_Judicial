from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routers import auth, bens, catalogo, diagnostico, documentos, herdeiros, pendencias, processos
from app.config import obter_configuracao
from app.db import Base, engine
from app.services.excecoes import ErroServico

config = obter_configuracao()


@asynccontextmanager
async def ciclo_de_vida(app: FastAPI):
    import app.models

    Base.metadata.create_all(bind=engine)
    config.upload_dir.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title=config.app_nome,
    version="0.1.0",
    description="Camada de backend para suporte a IA em processos de inventário judicial: ingestão documental, pipeline de NLP, diagnóstico e exposição via API REST.",
    lifespan=ciclo_de_vida,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.origens_cors,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ErroServico)
async def tratar_erro_servico(request: Request, erro: ErroServico) -> JSONResponse:
    return JSONResponse(status_code=erro.status_http, content={"detail": str(erro)})


@app.get("/", tags=["Saúde"])
def raiz() -> dict:
    return {"aplicacao": config.app_nome, "status": "ok", "llm_provider": config.llm_provider}


app.include_router(auth.router)
app.include_router(catalogo.router)
app.include_router(processos.router)
app.include_router(documentos.router)
app.include_router(herdeiros.router)
app.include_router(bens.router)
app.include_router(pendencias.router)
app.include_router(diagnostico.router)
