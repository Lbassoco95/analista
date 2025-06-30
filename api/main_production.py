import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Importar el router de feedback
from api.feedback import router as feedback_router
from api.scraping import router as scraping_router
from api.analisis_estrategico import router as analisis_router
from api.consulta_inteligente import router as consulta_router

load_dotenv()

# Crear aplicación FastAPI
app = FastAPI(
    title="Kawii Feedback API",
    description="API para retroalimentación automática desde GPT personalizado",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    servers=[
        {"url": "https://kawii-feedback-api-948d78bdec19.herokuapp.com", "description": "Heroku deployment"}
    ]
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(feedback_router, prefix="/feedback", tags=["feedback"])
app.include_router(scraping_router, prefix="", tags=["scraping"])
app.include_router(analisis_router, prefix="", tags=["analisis"])
app.include_router(consulta_router, prefix="", tags=["consulta"])

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Kawii Feedback API is running!",
        "version": "1.0.0",
        "status": "healthy",
        "endpoints": {
            "docs": "/docs",
            "feedback": "/feedback/guardar_feedback/"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "service": "kawii-feedback-api"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port) 