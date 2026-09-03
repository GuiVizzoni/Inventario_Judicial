import re
from pathlib import Path

import pymupdf

from app.config import obter_configuracao


def normalizar_texto(texto: str) -> str:
    texto = texto.replace("\x00", "").replace("\r\n", "\n").replace("\r", "\n")
    texto = re.sub(r"[ \t]+", " ", texto)
    linhas = [linha.strip() for linha in texto.split("\n")]
    resultado: list[str] = []
    vazias = 0
    for linha in linhas:
        if linha:
            resultado.append(linha)
            vazias = 0
        else:
            vazias += 1
            if vazias == 1:
                resultado.append("")
    return "\n".join(resultado).strip()


def _texto_nativo(documento: pymupdf.Document) -> str:
    paginas = [pagina.get_text() for pagina in documento]
    return "\n\f\n".join(paginas)


def _texto_ocr(documento: pymupdf.Document, idioma: str) -> str | None:
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        return None
    try:
        paginas: list[str] = []
        for pagina in documento:
            pix = pagina.get_pixmap(dpi=200)
            imagem = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            paginas.append(pytesseract.image_to_string(imagem, lang=idioma))
        return "\n\f\n".join(paginas)
    except Exception:
        return None


def extrair_texto(caminho: Path) -> tuple[str, str]:
    config = obter_configuracao()
    documento = pymupdf.open(caminho)
    try:
        nativo = _texto_nativo(documento)
        if len(nativo.strip()) >= config.ocr_limiar_caracteres:
            return normalizar_texto(nativo), "nativo"
        ocr = _texto_ocr(documento, config.ocr_idioma)
        if ocr and len(ocr.strip()) > len(nativo.strip()):
            return normalizar_texto(ocr), "ocr"
        return normalizar_texto(nativo), "nativo_insuficiente"
    finally:
        documento.close()


def extrair_texto_de_bytes(conteudo: bytes) -> tuple[str, str]:
    config = obter_configuracao()
    documento = pymupdf.open(stream=conteudo, filetype="pdf")
    try:
        nativo = _texto_nativo(documento)
        if len(nativo.strip()) >= config.ocr_limiar_caracteres:
            return normalizar_texto(nativo), "nativo"
        ocr = _texto_ocr(documento, config.ocr_idioma)
        if ocr and len(ocr.strip()) > len(nativo.strip()):
            return normalizar_texto(ocr), "ocr"
        return normalizar_texto(nativo), "nativo_insuficiente"
    finally:
        documento.close()
