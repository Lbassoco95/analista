# type: ignore[import]
from fastapi import APIRouter, HTTPException  # type: ignore
from pydantic import BaseModel  # type: ignore
import requests
import os
import json
from typing import List, Optional
from openai import OpenAI
from datetime import datetime
from bs4 import BeautifulSoup, Tag

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_TABLE = "consulta_inteligente"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

router = APIRouter()

class ConsultaRequest(BaseModel):
    pregunta: str
    contexto: Optional[str] = None
    max_fuentes: Optional[int] = 3

class FuenteValida(BaseModel):
    url: str
    titulo: str
    referencia_apa: str
    resumen: str

class ConsultaResponse(BaseModel):
    respuesta: str
    fuentes_utilizadas: List[FuenteValida]
    memoria_actualizada: bool


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

def buscar_fuentes_google(pregunta, max_fuentes=3):
    # Búsqueda simple usando DuckDuckGo (sin API Key)
    # Puedes cambiar a SerpAPI si tienes API Key
    query = pregunta.replace(' ', '+')
    url = f"https://duckduckgo.com/html/?q={query}"
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    results = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.startswith('http') and 'duckduckgo.com' not in href:
            results.append(href)
        if len(results) >= max_fuentes:
            break
    return results

def scrapear_y_validar(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        titulo = soup.title.string.strip() if soup.title and soup.title.string else "Sin título"
        # Extraer bibliografía (simple: busca referencias o links al final)
        referencias = []
        for ref in soup.find_all(['a', 'cite']):
            ref_url = ref.get('href')
            if ref_url and ref_url.startswith('http'):
                referencias.append(ref_url)
        # Validar si hay bibliografía real
        es_valido = len(referencias) > 0
        # Generar referencia APA básica
        referencia_apa = f"{titulo}. Recuperado de {url}"
        resumen = " ".join([p.get_text() for p in soup.find_all("p")])[:1000]
        return {
            "url": url,
            "titulo": titulo,
            "referencia_apa": referencia_apa,
            "resumen": resumen,
            "es_valido": es_valido
        }
    except Exception:
        return None

def analizar_con_gpt(pregunta, contexto, fuentes):
    client = OpenAI(api_key=OPENAI_API_KEY)
    prompt = (
        "Responde la siguiente pregunta usando solo la información de las fuentes proporcionadas. "
        "Incluye siempre la bibliografía en formato APA al final.\n"
        f"Pregunta: {pregunta}\n"
        f"Contexto: {contexto or ''}\n"
        f"Fuentes:\n"
    )
    for i, f in enumerate(fuentes):
        prompt += f"[{i+1}] {f['titulo']}\nResumen: {f['resumen']}\nReferencia APA: {f['referencia_apa']}\nURL: {f['url']}\n"
    prompt += "\nRespuesta:"
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=512
    )
    return response.choices[0].message.content

@router.post("/consulta/inteligente", response_model=ConsultaResponse)
def consulta_inteligente(request: ConsultaRequest):
    # 1. Buscar fuentes en la web
    urls = buscar_fuentes_google(request.pregunta, max_fuentes=request.max_fuentes)
    fuentes_validas = []
    for url in urls:
        fuente = scrapear_y_validar(url)
        if fuente and fuente["es_valido"]:
            fuentes_validas.append(fuente)
    if not fuentes_validas:
        raise HTTPException(status_code=404, detail="No se encontraron fuentes válidas con bibliografía real.")
    # 2. Analizar y responder con GPT
    respuesta = analizar_con_gpt(request.pregunta, request.contexto, fuentes_validas)
    # 3. Guardar en Supabase
    memoria_actualizada = guardar_supabase({
        "pregunta": request.pregunta,
        "respuesta": respuesta,
        "fuentes": json.dumps(fuentes_validas),
        "fecha": str(datetime.now())
    })
    return {
        "respuesta": respuesta,
        "fuentes_utilizadas": [
            {
                "url": f["url"],
                "titulo": f["titulo"],
                "referencia_apa": f["referencia_apa"],
                "resumen": f["resumen"]
            } for f in fuentes_validas
        ],
        "memoria_actualizada": memoria_actualizada
    } 