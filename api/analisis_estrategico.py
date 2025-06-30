# type: ignore[import]
from fastapi import APIRouter, HTTPException  # type: ignore
from pydantic import BaseModel  # type: ignore
import requests
import os
import json
from typing import List, Optional
from openai import OpenAI
from datetime import datetime

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_TABLE = "analisis_estrategico"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

router = APIRouter()

class AnalisisRequest(BaseModel):
    texto: str
    fuente: Optional[str] = None
    contexto: Optional[str] = None
    recursivo: Optional[bool] = False

class Bibliografia(BaseModel):
    referencia_apa: str
    url: Optional[str]
    valida: bool

class AnalisisResponse(BaseModel):
    titulo: str
    resumen: str
    kpis: List[str]
    recomendaciones: List[str]
    bibliografia_extraida: List[Bibliografia]
    es_valido: bool
    motivo: str


def validar_url(url):
    try:
        r = requests.head(url, timeout=5, allow_redirects=True)
        return r.status_code < 400
    except Exception:
        return False

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

def analizar_bibliografia_gpt(texto, api_key):
    client = OpenAI(api_key=api_key)
    prompt = (
        "Extrae todas las referencias bibliográficas en formato APA y sus URLs (si existen) del siguiente texto. "
        "Devuelve una lista JSON con los campos: referencia_apa, url. Si no hay URL, pon null.\nTexto:\n" + texto
    )
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=512
    )
    try:
        refs = json.loads(response.choices[0].message.content)
        return refs
    except Exception:
        return []

def analizar_estrategico_gpt(texto, contexto, api_key):
    client = OpenAI(api_key=api_key)
    prompt = (
        "Analiza el siguiente texto como analista estratégico de productos fintech. "
        "Devuelve un resumen, KPIs clave, y recomendaciones accionables en formato JSON.\n"
        f"Contexto: {contexto}\nTexto:\n{texto}"
    )
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=512
    )
    try:
        return json.loads(response.choices[0].message.content)
    except Exception:
        return {"resumen": "", "kpis": [], "recomendaciones": []}

@router.post("/analisis/estrategico", response_model=AnalisisResponse)
def analisis_estrategico(request: AnalisisRequest):
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="No hay API Key de OpenAI configurada")
    # 1. Extraer bibliografía
    refs = analizar_bibliografia_gpt(request.texto, OPENAI_API_KEY)
    bibliografia = []
    for ref in refs:
        url = ref.get("url")
        valida = validar_url(url) if url else False
        bibliografia.append({
            "referencia_apa": ref.get("referencia_apa", ""),
            "url": url,
            "valida": valida
        })
    # 2. Validar si hay bibliografía real
    bibliografia_valida = [b for b in bibliografia if b["valida"]]
    es_valido = len(bibliografia_valida) > 0
    motivo = "Contiene bibliografía real y consultable" if es_valido else "No se encontró bibliografía válida"
    # 3. Análisis estratégico solo si es válido
    if es_valido:
        analisis = analizar_estrategico_gpt(request.texto, request.contexto, OPENAI_API_KEY)
    else:
        analisis = {"resumen": "No se realizó análisis por falta de bibliografía válida.", "kpis": [], "recomendaciones": []}
    # 4. Recursividad: analizar fuentes de bibliografía (primer nivel)
    if request.recursivo and es_valido:
        for b in bibliografia_valida:
            if b["url"]:
                try:
                    r = requests.get(b["url"], timeout=10)
                    if r.status_code < 400:
                        subrefs = analizar_bibliografia_gpt(r.text, OPENAI_API_KEY)
                        # No guardamos sub-análisis, solo mostramos
                        b["sub_bibliografia"] = subrefs
                except Exception:
                    b["sub_bibliografia"] = []
    # 5. Guardar en Supabase si es válido
    if es_valido:
        guardar_supabase({
            "titulo": analisis.get("titulo", ""),
            "resumen": analisis.get("resumen", ""),
            "kpis": json.dumps(analisis.get("kpis", [])),
            "recomendaciones": json.dumps(analisis.get("recomendaciones", [])),
            "bibliografia": json.dumps(bibliografia),
            "fuente": request.fuente,
            "fecha": str(datetime.now())
        })
    return {
        "titulo": analisis.get("titulo", request.fuente or "Sin título"),
        "resumen": analisis.get("resumen", ""),
        "kpis": analisis.get("kpis", []),
        "recomendaciones": analisis.get("recomendaciones", []),
        "bibliografia_extraida": bibliografia,
        "es_valido": es_valido,
        "motivo": motivo
    } 