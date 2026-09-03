from fastapi import APIRouter

from app.api.schemas import ItemCatalogoSaida
from app.dominio.catalogo_documentos import CATALOGO

router = APIRouter(prefix="/catalogo", tags=["Catálogo"])


@router.get("/documentos", response_model=list[ItemCatalogoSaida])
def listar_tipos_documentais() -> list[ItemCatalogoSaida]:
    return [ItemCatalogoSaida(**item.__dict__) for item in CATALOGO]
