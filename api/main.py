"""
API FastAPI para integración con GPT Function Calling.
Expone funciones que GPT puede invocar automáticamente.
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import logging

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar componentes del sistema
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase_client import SupabaseManager
from utils.optimized_analyzer import OptimizedAnalyzer
from utils.model_manager import ModelManager
from utils.extract_price import extract_price_from_text, clean_text, extract_pricing_terms, validate_price_extraction

# Importar router de feedback
try:
    from api.feedback import router as feedback_router
    logger.info("✅ Router de feedback importado correctamente")
except ImportError as e:
    logger.warning(f"⚠️ No se pudo importar router de feedback: {str(e)}")
    feedback_router = None

# Inicializar FastAPI
app = FastAPI(
    title="Web Scraper API con Hugging Face",
    description="API para análisis de proveedores de marca blanca con modelos locales y GPT",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar router de feedback si está disponible
if feedback_router:
    app.include_router(feedback_router)
    logger.info("✅ Router de feedback registrado en la API")
else:
    logger.warning("⚠️ Router de feedback no disponible")

# Inicializar componentes del sistema
try:
    supabase_manager = SupabaseManager()
    optimized_analyzer = OptimizedAnalyzer(use_local_models=True, use_gpt=True)
    model_manager = ModelManager()
    logger.info("✅ Componentes del sistema inicializados correctamente")
except Exception as e:
    logger.error(f"❌ Error inicializando componentes: {str(e)}")
    supabase_manager = None
    optimized_analyzer = None
    model_manager = None

# Modelos Pydantic para requests/responses
class TextAnalysisRequest(BaseModel):
    text: str = Field(..., description="Texto a analizar")
    source: str = Field(..., description="Fuente del texto")
    use_local_models: bool = Field(True, description="Usar modelos locales")
    use_gpt_backup: bool = Field(True, description="Usar GPT como respaldo")

class BatchAnalysisRequest(BaseModel):
    texts: List[Dict[str, str]] = Field(..., description="Lista de textos a analizar")
    use_local_models: bool = Field(True, description="Usar modelos locales")
    use_gpt_backup: bool = Field(True, description="Usar GPT como respaldo")

class ScrapingRequest(BaseModel):
    providers: List[str] = Field(..., description="Proveedores a scrapear")
    use_sample_data: bool = Field(False, description="Usar datos de muestra")

class PriceExtractionRequest(BaseModel):
    text: str = Field(..., description="Texto del que extraer precio")
    currency: Optional[str] = Field(None, description="Moneda específica a buscar")

class ModelInfoRequest(BaseModel):
    model_type: Optional[str] = Field(None, description="Tipo de modelo específico")

class AnalysisResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    timestamp: str
    processing_time: float

class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None
    timestamp: str

# Endpoints principales
@app.get("/")
async def root():
    """Endpoint raíz con información de la API."""
    return {
        "message": "Web Scraper API con Hugging Face",
        "version": "1.0.0",
        "status": "active",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "health": "/health",
            "analyze": "/analyze",
            "analyze-batch": "/analyze-batch",
            "scrape": "/scrape",
            "extract-price": "/extract-price",
            "model-info": "/model-info",
            "stats": "/stats",
            "function-definitions": "/function-definitions"
        }
    }

@app.get("/health")
async def health_check():
    """Verificar estado de salud de la API y componentes."""
    health_status = {
        "api": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {}
    }
    
    # Verificar Supabase
    if supabase_manager:
        try:
            supabase_status = supabase_manager.test_connection()
            health_status["components"]["supabase"] = supabase_status
        except Exception as e:
            health_status["components"]["supabase"] = {"status": "error", "error": str(e)}
    else:
        health_status["components"]["supabase"] = {"status": "not_initialized"}
    
    # Verificar modelos locales
    if model_manager:
        try:
            model_info = model_manager.get_model_info()
            health_status["components"]["local_models"] = {
                "status": "available",
                "models_loaded": model_info.get("models_loaded", []),
                "device": model_info.get("device", "unknown")
            }
        except Exception as e:
            health_status["components"]["local_models"] = {"status": "error", "error": str(e)}
    else:
        health_status["components"]["local_models"] = {"status": "not_initialized"}
    
    return health_status

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_text(request: TextAnalysisRequest):
    """
    Analizar un texto usando modelos locales y/o GPT.
    
    Esta función puede ser invocada por GPT usando Function Calling.
    """
    start_time = datetime.now()
    
    try:
        # Configurar analizador según parámetros
        analyzer = OptimizedAnalyzer(
            use_local_models=request.use_local_models,
            use_gpt=request.use_gpt_backup
        )
        
        # Realizar análisis
        result = await analyzer.analyze_text_optimized(
            text=request.text,
            source=request.source
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return AnalysisResponse(
            success=True,
            data=result,
            timestamp=datetime.now().isoformat(),
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error en análisis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-batch", response_model=AnalysisResponse)
async def analyze_batch(request: BatchAnalysisRequest):
    """
    Analizar múltiples textos en lote.
    
    Esta función puede ser invocada por GPT usando Function Calling.
    """
    start_time = datetime.now()
    
    try:
        # Configurar analizador
        analyzer = OptimizedAnalyzer(
            use_local_models=request.use_local_models,
            use_gpt=request.use_gpt_backup
        )
        
        # Realizar análisis en lote
        results = await analyzer.analyze_batch_optimized(request.texts)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return AnalysisResponse(
            success=True,
            data={
                "results": results,
                "total_processed": len(results),
                "batch_stats": analyzer.get_analysis_stats()
            },
            timestamp=datetime.now().isoformat(),
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error en análisis en lote: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scrape", response_model=AnalysisResponse)
async def scrape_providers(request: ScrapingRequest, background_tasks: BackgroundTasks):
    """
    Realizar scraping de proveedores específicos.
    
    Esta función puede ser invocada por GPT usando Function Calling.
    """
    start_time = datetime.now()
    
    try:
        # Importar scrapers dinámicamente
        scrapers = {}
        for provider in request.providers:
            try:
                module = __import__(f"modules.{provider}", fromlist=[f"{provider.capitalize()}Scraper"])
                scraper_class = getattr(module, f"{provider.capitalize()}Scraper")
                scrapers[provider] = scraper_class()
            except ImportError as e:
                logger.warning(f"No se pudo importar scraper para {provider}: {str(e)}")
        
        if not scrapers:
            raise HTTPException(status_code=400, detail="No se pudieron cargar scrapers")
        
        # Ejecutar scraping en background
        scraping_results = []
        
        for provider_name, scraper in scrapers.items():
            try:
                if request.use_sample_data:
                    data = scraper.get_sample_data()
                else:
                    data = await scraper.scrape_all()
                
                # Guardar en Supabase
                for item in data:
                    record_id = supabase_manager.insert_data(item)
                    if record_id:
                        scraping_results.append({
                            "provider": provider_name,
                            "record_id": record_id,
                            "data": item
                        })
                
            except Exception as e:
                logger.error(f"Error scraping {provider_name}: {str(e)}")
                scraping_results.append({
                    "provider": provider_name,
                    "error": str(e)
                })
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return AnalysisResponse(
            success=True,
            data={
                "scraping_results": scraping_results,
                "total_providers": len(request.providers),
                "successful_scrapes": len([r for r in scraping_results if "error" not in r])
            },
            timestamp=datetime.now().isoformat(),
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error en scraping: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/extract-price", response_model=AnalysisResponse)
async def extract_price(request: PriceExtractionRequest):
    """
    Extraer precio de un texto específico.
    
    Esta función puede ser invocada por GPT usando Function Calling.
    """
    start_time = datetime.now()
    
    try:
        # Limpiar texto
        cleaned_text = clean_text(request.text)
        
        # Extraer precio
        price = extract_price_from_text(cleaned_text)
        
        # Extraer términos de precios
        pricing_terms = extract_pricing_terms(cleaned_text)
        
        # Validar extracción
        validation = validate_price_extraction(cleaned_text, price) if price else {
            "is_valid": False,
            "confidence": 0.0,
            "issues": ["No se encontró precio"],
            "suggestions": []
        }
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return AnalysisResponse(
            success=True,
            data={
                "extracted_price": price,
                "pricing_terms": pricing_terms,
                "validation": validation,
                "original_text": request.text,
                "cleaned_text": cleaned_text
            },
            timestamp=datetime.now().isoformat(),
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error extrayendo precio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/model-info", response_model=AnalysisResponse)
async def get_model_info(request: ModelInfoRequest = None):
    """
    Obtener información de los modelos cargados.
    
    Esta función puede ser invocada por GPT usando Function Calling.
    """
    start_time = datetime.now()
    
    try:
        model_info = {}
        
        if model_manager:
            model_info["local_models"] = model_manager.get_model_info()
        
        if optimized_analyzer:
            model_info["analyzer_stats"] = optimized_analyzer.get_analysis_stats()
        
        if supabase_manager:
            model_info["supabase_stats"] = supabase_manager.get_statistics()
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return AnalysisResponse(
            success=True,
            data=model_info,
            timestamp=datetime.now().isoformat(),
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo información de modelos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_system_stats():
    """
    Obtener estadísticas completas del sistema.
    
    Esta función puede ser invocada por GPT usando Function Calling.
    """
    try:
        stats = {
            "timestamp": datetime.now().isoformat(),
            "api_status": "active"
        }
        
        if supabase_manager:
            stats["supabase"] = supabase_manager.get_statistics()
        
        if optimized_analyzer:
            stats["analyzer"] = optimized_analyzer.get_analysis_stats()
        
        if model_manager:
            stats["models"] = model_manager.get_model_info()
        
        return stats
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/function-definitions")
async def get_function_definitions():
    """
    Obtener definiciones de funciones para GPT Function Calling.
    
    Retorna las definiciones en formato JSON que GPT puede usar.
    """
    function_definitions = [
        {
            "name": "analyze_text",
            "description": "Analizar un texto usando modelos locales y/o GPT para extraer precios, clasificar módulos y obtener condiciones comerciales",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Texto a analizar"
                    },
                    "source": {
                        "type": "string",
                        "description": "Fuente del texto (ej: B2Broker, Wallester, Sumsub)"
                    },
                    "use_local_models": {
                        "type": "boolean",
                        "description": "Usar modelos locales de Hugging Face (más rápido, sin costos)",
                        "default": True
                    },
                    "use_gpt_backup": {
                        "type": "boolean",
                        "description": "Usar GPT como respaldo si los modelos locales fallan",
                        "default": True
                    }
                },
                "required": ["text", "source"]
            }
        },
        {
            "name": "analyze_batch",
            "description": "Analizar múltiples textos en lote para procesamiento eficiente",
            "parameters": {
                "type": "object",
                "properties": {
                    "texts": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "text": {"type": "string"},
                                "source": {"type": "string"}
                            }
                        },
                        "description": "Lista de textos a analizar"
                    },
                    "use_local_models": {
                        "type": "boolean",
                        "description": "Usar modelos locales",
                        "default": True
                    },
                    "use_gpt_backup": {
                        "type": "boolean",
                        "description": "Usar GPT como respaldo",
                        "default": True
                    }
                },
                "required": ["texts"]
            }
        },
        {
            "name": "scrape_providers",
            "description": "Realizar web scraping de proveedores específicos de marca blanca",
            "parameters": {
                "type": "object",
                "properties": {
                    "providers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Lista de proveedores a scrapear (b2broker, wallester, sumsub)",
                        "enum": ["b2broker", "wallester", "sumsub"]
                    },
                    "use_sample_data": {
                        "type": "boolean",
                        "description": "Usar datos de muestra en lugar de hacer scraping real",
                        "default": False
                    }
                },
                "required": ["providers"]
            }
        },
        {
            "name": "extract_price",
            "description": "Extraer precio específico de un texto usando patrones optimizados",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Texto del que extraer precio"
                    },
                    "currency": {
                        "type": "string",
                        "description": "Moneda específica a buscar (USD, EUR, GBP)",
                        "enum": ["USD", "EUR", "GBP"]
                    }
                },
                "required": ["text"]
            }
        },
        {
            "name": "get_model_info",
            "description": "Obtener información sobre los modelos cargados y su estado",
            "parameters": {
                "type": "object",
                "properties": {
                    "model_type": {
                        "type": "string",
                        "description": "Tipo específico de modelo (classification, embedding, summarization)",
                        "enum": ["classification", "embedding", "summarization"]
                    }
                }
            }
        },
        {
            "name": "get_system_stats",
            "description": "Obtener estadísticas completas del sistema y rendimiento",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    ]
    
    return {
        "functions": function_definitions,
        "api_base_url": "http://localhost:8000",
        "endpoints": {
            "analyze": "/analyze",
            "analyze-batch": "/analyze-batch",
            "scrape": "/scrape",
            "extract-price": "/extract-price",
            "model-info": "/model-info",
            "stats": "/stats"
        }
    }

# Endpoints de utilidad
@app.get("/docs/openapi.json")
async def get_openapi_schema():
    """Obtener esquema OpenAPI para integración con herramientas externas."""
    return app.openapi()

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Manejador global de excepciones."""
    logger.error(f"Error no manejado: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            details=str(exc),
            timestamp=datetime.now().isoformat()
        ).dict()
    )

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 