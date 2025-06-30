# type: ignore[import]
from fastapi import APIRouter, HTTPException  # type: ignore
from pydantic import BaseModel  # type: ignore
import requests
from bs4 import BeautifulSoup, Tag
from datetime import datetime
import os
import json

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_TABLE = "scraping_resultados"

router = APIRouter()

class ScrapingRequest(BaseModel):
    url: str

class ScrapingResponse(BaseModel):
    contenido: str
    titulo: str
    fecha: str
    fuente: str
    referencia_apa: str


def formatear_apa(titulo, url, fecha=None, autor=None):
    anio = fecha[:4] if fecha else datetime.now().year
    autor_str = autor if autor else "Sin autor"
    return f"{autor_str}. ({anio}). {titulo}. Recuperado de {url}"


def guardar_supabase(data):
    if not SUPABASE_URL or not SUPABASE_KEY:
        return False
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}"
    resp = requests.post(url, headers=headers, data=json.dumps(data))
    return resp.status_code in [200, 201]

@router.post("/scraping/extraer", response_model=ScrapingResponse)
def extraer_info(request: ScrapingRequest):
    try:
        r = requests.get(request.url, timeout=10)
        r.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"No se pudo acceder a la URL: {e}")
    soup = BeautifulSoup(r.text, "html.parser")
    titulo = soup.title.string.strip() if soup.title and soup.title.string else "Sin título"
    # Intentar extraer fecha y autor
    fecha = None
    autor = None
    meta_author = soup.find("meta", {"name": "author"})
    if isinstance(meta_author, Tag) and meta_author.get("content"):
        autor = meta_author.get("content")
    meta_fecha = soup.find("meta", {"property": "article:published_time"})
    if isinstance(meta_fecha, Tag):
        fecha_content = meta_fecha.get("content")
        if fecha_content:
            fecha = fecha_content[:10]
    contenido = " ".join([p.get_text() for p in soup.find_all("p")])[:3000]
    referencia_apa = formatear_apa(titulo, request.url, fecha, autor)
    resultado = {
        "contenido": contenido,
        "titulo": titulo,
        "fecha": fecha or str(datetime.now().date()),
        "fuente": request.url,
        "referencia_apa": referencia_apa
    }
    guardar_supabase(resultado)
    return resultado 