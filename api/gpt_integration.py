"""
Módulo de integración para GPT Function Calling.
Proporciona funciones que GPT puede invocar automáticamente.
"""

import os
import json
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class GPTFunctionCaller:
    """
    Cliente para invocar funciones de la API desde GPT.
    """
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        """
        Inicializar el cliente de función calling.
        
        Args:
            api_base_url: URL base de la API
        """
        self.api_base_url = api_base_url
        self.session = None
    
    async def __aenter__(self):
        """Context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.session:
            await self.session.close()
    
    async def call_function(self, function_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invocar una función específica de la API.
        
        Args:
            function_name: Nombre de la función a invocar
            parameters: Parámetros de la función
            
        Returns:
            Resultado de la función
        """
        if not self.session:
            raise RuntimeError("Session no inicializada. Usa 'async with GPTFunctionCaller() as caller:'")
        
        # Mapeo de funciones a endpoints
        function_endpoints = {
            "analyze_text": "/analyze",
            "analyze_batch": "/analyze-batch",
            "scrape_providers": "/scrape",
            "extract_price": "/extract-price",
            "get_model_info": "/model-info",
            "get_system_stats": "/stats"
        }
        
        if function_name not in function_endpoints:
            raise ValueError(f"Función no soportada: {function_name}")
        
        endpoint = function_endpoints[function_name]
        url = f"{self.api_base_url}{endpoint}"
        
        try:
            if function_name in ["get_model_info", "get_system_stats"]:
                # GET requests
                async with self.session.get(url) as response:
                    return await response.json()
            else:
                # POST requests
                async with self.session.post(url, json=parameters) as response:
                    return await response.json()
                    
        except Exception as e:
            logger.error(f"Error invocando función {function_name}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "function": function_name
            }
    
    async def analyze_text(self, text: str, source: str, use_local_models: bool = True, use_gpt_backup: bool = True) -> Dict[str, Any]:
        """
        Analizar un texto usando la API.
        
        Args:
            text: Texto a analizar
            source: Fuente del texto
            use_local_models: Usar modelos locales
            use_gpt_backup: Usar GPT como respaldo
            
        Returns:
            Resultado del análisis
        """
        parameters = {
            "text": text,
            "source": source,
            "use_local_models": use_local_models,
            "use_gpt_backup": use_gpt_backup
        }
        
        return await self.call_function("analyze_text", parameters)
    
    async def analyze_batch(self, texts: List[Dict[str, str]], use_local_models: bool = True, use_gpt_backup: bool = True) -> Dict[str, Any]:
        """
        Analizar múltiples textos en lote.
        
        Args:
            texts: Lista de textos a analizar
            use_local_models: Usar modelos locales
            use_gpt_backup: Usar GPT como respaldo
            
        Returns:
            Resultado del análisis en lote
        """
        parameters = {
            "texts": texts,
            "use_local_models": use_local_models,
            "use_gpt_backup": use_gpt_backup
        }
        
        return await self.call_function("analyze_batch", parameters)
    
    async def scrape_providers(self, providers: List[str], use_sample_data: bool = False) -> Dict[str, Any]:
        """
        Realizar scraping de proveedores.
        
        Args:
            providers: Lista de proveedores a scrapear
            use_sample_data: Usar datos de muestra
            
        Returns:
            Resultado del scraping
        """
        parameters = {
            "providers": providers,
            "use_sample_data": use_sample_data
        }
        
        return await self.call_function("scrape_providers", parameters)
    
    async def extract_price(self, text: str, currency: Optional[str] = None) -> Dict[str, Any]:
        """
        Extraer precio de un texto.
        
        Args:
            text: Texto del que extraer precio
            currency: Moneda específica a buscar
            
        Returns:
            Precio extraído
        """
        parameters = {
            "text": text
        }
        
        if currency:
            parameters["currency"] = currency
        
        return await self.call_function("extract_price", parameters)
    
    async def get_model_info(self, model_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtener información de modelos.
        
        Args:
            model_type: Tipo específico de modelo
            
        Returns:
            Información de modelos
        """
        return await self.call_function("get_model_info", {})
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """
        Obtener estadísticas del sistema.
        
        Returns:
            Estadísticas del sistema
        """
        return await self.call_function("get_system_stats", {})

class GPTIntegrationHelper:
    """
    Helper para facilitar la integración con GPT Function Calling.
    """
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        """
        Inicializar el helper de integración.
        
        Args:
            api_base_url: URL base de la API
        """
        self.api_base_url = api_base_url
    
    def get_function_definitions(self) -> List[Dict[str, Any]]:
        """
        Obtener definiciones de funciones para GPT.
        
        Returns:
            Lista de definiciones de funciones
        """
        return [
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
    
    def create_gpt_tools_config(self) -> Dict[str, Any]:
        """
        Crear configuración de herramientas para GPT.
        
        Returns:
            Configuración de herramientas
        """
        return {
            "type": "function",
            "function": {
                "name": "web_scraper_api",
                "description": "API para análisis de proveedores de marca blanca con modelos locales y GPT",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "function_name": {
                            "type": "string",
                            "description": "Nombre de la función a invocar",
                            "enum": ["analyze_text", "analyze_batch", "scrape_providers", "extract_price", "get_model_info", "get_system_stats"]
                        },
                        "parameters": {
                            "type": "object",
                            "description": "Parámetros específicos de la función"
                        }
                    },
                    "required": ["function_name", "parameters"]
                }
            }
        }
    
    async def execute_gpt_function_call(self, function_call: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecutar una llamada de función de GPT.
        
        Args:
            function_call: Llamada de función de GPT
            
        Returns:
            Resultado de la ejecución
        """
        try:
            function_name = function_call.get("name")
            arguments = function_call.get("arguments", {})
            
            if isinstance(arguments, str):
                arguments = json.loads(arguments)
            
            async with GPTFunctionCaller(self.api_base_url) as caller:
                return await caller.call_function(function_name, arguments)
                
        except Exception as e:
            logger.error(f"Error ejecutando función de GPT: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "function_call": function_call
            }

# Ejemplo de uso
async def example_usage():
    """Ejemplo de cómo usar la integración con GPT."""
    
    # Crear helper
    helper = GPTIntegrationHelper()
    
    # Obtener definiciones de funciones
    functions = helper.get_function_definitions()
    print("Funciones disponibles:", [f["name"] for f in functions])
    
    # Ejecutar análisis de texto
    async with GPTFunctionCaller() as caller:
        result = await caller.analyze_text(
            text="B2Broker offers comprehensive white label solutions for crypto exchanges. Setup fee starts at $50,000 with monthly maintenance costs of $5,000.",
            source="B2Broker",
            use_local_models=True,
            use_gpt_backup=True
        )
        
        print("Resultado del análisis:", json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(example_usage()) 