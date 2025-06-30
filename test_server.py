import os
import json
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import requests

load_dotenv()

app = FastAPI(title="Test Feedback API", version="1.0.0")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

class FeedbackRequest(BaseModel):
    producto: str
    mercado: str
    observacion: str
    categoria: str = None
    impacto: str = None
    accion_recomendada: str = None
    fuente: str = "gpt_chat"
    metadata: dict = None

class FeedbackResponse(BaseModel):
    id: str
    status: str
    mensaje: str
    timestamp: str

@app.get("/")
async def root():
    return {"message": "Test Feedback API is running!"}

@app.post("/feedback/guardar_feedback/", response_model=FeedbackResponse)
async def guardar_feedback(feedback: FeedbackRequest):
    """
    Guarda feedback en Supabase usando la API REST
    """
    try:
        # Preparar los datos para insertar
        data = {
            "producto": feedback.producto,
            "mercado": feedback.mercado,
            "observacion": feedback.observacion,
            "categoria": feedback.categoria,
            "impacto": feedback.impacto,
            "accion_recomendada": feedback.accion_recomendada,
            "fuente": feedback.fuente,
            "metadata": feedback.metadata,
            "fecha": datetime.now().isoformat(),
            "estado": "activo"
        }
        
        # URL de la API REST de Supabase para la tabla retroalimentacion
        url = f"{SUPABASE_URL}/rest/v1/retroalimentacion"
        
        # Headers necesarios para Supabase
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        
        print(f"Enviando datos a Supabase: {data}")
        print(f"URL: {url}")
        
        # Hacer la petición POST a Supabase
        response = requests.post(url, json=data, headers=headers)
        
        print(f"Respuesta de Supabase: {response.status_code}")
        print(f"Contenido: {response.text}")
        
        if response.status_code == 201:
            # Supabase devuelve el registro insertado
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                inserted_id = result[0].get('id', 'unknown')
            else:
                inserted_id = 'unknown'
                
            return FeedbackResponse(
                id=str(inserted_id),
                status="success",
                mensaje="Feedback guardado exitosamente",
                timestamp=datetime.now().isoformat()
            )
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error al guardar en Supabase: {response.text}"
            )
            
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@app.get("/feedback/obtener_feedback/")
async def obtener_feedback():
    """
    Obtiene todos los registros de feedback desde Supabase
    """
    try:
        url = f"{SUPABASE_URL}/rest/v1/retroalimentacion?select=*&order=fecha.desc"
        
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return {"data": response.json()}
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error al obtener datos: {response.text}"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    import sys
    
    port = 8001  # Puerto por defecto
    if len(sys.argv) > 1 and "--port" in sys.argv:
        try:
            port_index = sys.argv.index("--port")
            if port_index + 1 < len(sys.argv):
                port = int(sys.argv[port_index + 1])
        except (ValueError, IndexError):
            pass
    
    print(f"Iniciando servidor en puerto {port}")
    uvicorn.run(app, host="0.0.0.0", port=port) 