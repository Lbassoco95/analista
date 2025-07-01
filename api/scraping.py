# type: ignore[import]
from fastapi import APIRouter, HTTPException  # type: ignore
from pydantic import BaseModel  # type: ignore
import requests
from bs4 import BeautifulSoup, Tag
from datetime import datetime
import os
import json
from typing import List, Optional

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

class DocumentoScraping(BaseModel):
    id: Optional[int]
    contenido: str
    titulo: str
    fecha: str
    fuente: str
    referencia_apa: str
    created_at: Optional[str] = None

class DocumentosResponse(BaseModel):
    documentos: List[DocumentoScraping]
    total: int
    pagina: int
    por_pagina: int


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


def obtener_documentos_supabase(limit: int = 50, offset: int = 0, ordenar_por: str = "created_at"):
    """
    Obtener documentos scrapings desde Supabase.
    
    Args:
        limit: Número máximo de documentos a obtener
        offset: Desplazamiento para paginación
        ordenar_por: Campo por el cual ordenar (created_at, fecha, titulo)
    
    Returns:
        Lista de documentos y metadata
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        return {"documentos": [], "total": 0, "error": "Supabase no configurado"}
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        # Construir URL con parámetros
        url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}"
        params = {
            "select": "*",
            "order": f"{ordenar_por}.desc",
            "limit": limit,
            "offset": offset
        }
        
        # Hacer petición GET
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            documentos = response.json()
            
            # Obtener total de registros
            count_url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}"
            count_params = {"select": "count"}
            count_response = requests.get(count_url, headers=headers, params=count_params)
            total = 0
            if count_response.status_code == 200:
                total = count_response.json()[0]["count"]
            
            return {
                "documentos": documentos,
                "total": total,
                "pagina": (offset // limit) + 1,
                "por_pagina": limit
            }
        else:
            return {"documentos": [], "total": 0, "error": f"Error {response.status_code}: {response.text}"}
            
    except Exception as e:
        return {"documentos": [], "total": 0, "error": f"Error de conexión: {str(e)}"}


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


@router.get("/scraping/documentos", response_model=DocumentosResponse)
def obtener_documentos(
    limit: int = 50, 
    offset: int = 0, 
    ordenar_por: str = "created_at"
):
    """
    Obtener lista de documentos scrapings guardados.
    
    Args:
        limit: Número máximo de documentos (máximo 100)
        offset: Desplazamiento para paginación
        ordenar_por: Campo por el cual ordenar (created_at, fecha, titulo)
    
    Returns:
        Lista de documentos con metadata de paginación
    """
    # Validar parámetros
    if limit > 100:
        limit = 100
    if limit < 1:
        limit = 10
    
    # Obtener documentos desde Supabase
    resultado = obtener_documentos_supabase(limit, offset, ordenar_por)
    
    if "error" in resultado:
        raise HTTPException(status_code=500, detail=resultado["error"])
    
    # Convertir a modelos Pydantic
    documentos = []
    for doc in resultado["documentos"]:
        documentos.append(DocumentoScraping(
            id=doc.get("id"),
            contenido=doc.get("contenido", ""),
            titulo=doc.get("titulo", ""),
            fecha=doc.get("fecha", ""),
            fuente=doc.get("fuente", ""),
            referencia_apa=doc.get("referencia_apa", ""),
            created_at=doc.get("created_at")
        ))
    
    return DocumentosResponse(
        documentos=documentos,
        total=resultado["total"],
        pagina=resultado["pagina"],
        por_pagina=resultado["por_pagina"]
    )


@router.get("/scraping/documentos/{documento_id}")
def obtener_documento_por_id(documento_id: int):
    """
    Obtener un documento específico por su ID.
    
    Args:
        documento_id: ID del documento a obtener
    
    Returns:
        Documento específico
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise HTTPException(status_code=500, detail="Supabase no configurado")
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}?id=eq.{documento_id}"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            documentos = response.json()
            if documentos:
                return documentos[0]
            else:
                raise HTTPException(status_code=404, detail="Documento no encontrado")
        else:
            raise HTTPException(status_code=500, detail=f"Error obteniendo documento: {response.text}")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de conexión: {str(e)}") 