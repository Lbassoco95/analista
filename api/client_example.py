"""
Ejemplo de cliente para usar la API FastAPI.
Demuestra cómo invocar las funciones desde Python.
"""

import asyncio
import json
import aiohttp
from typing import Dict, List, Any
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIClient:
    """
    Cliente de ejemplo para la API FastAPI.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Inicializar cliente.
        
        Args:
            base_url: URL base de la API
        """
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        """Context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.session:
            await self.session.close()
    
    async def health_check(self) -> Dict[str, Any]:
        """Verificar estado de salud de la API."""
        async with self.session.get(f"{self.base_url}/health") as response:
            return await response.json()
    
    async def analyze_text(self, text: str, source: str, use_local_models: bool = True, use_gpt_backup: bool = True) -> Dict[str, Any]:
        """Analizar un texto."""
        data = {
            "text": text,
            "source": source,
            "use_local_models": use_local_models,
            "use_gpt_backup": use_gpt_backup
        }
        
        async with self.session.post(f"{self.base_url}/analyze", json=data) as response:
            return await response.json()
    
    async def analyze_batch(self, texts: List[Dict[str, str]], use_local_models: bool = True, use_gpt_backup: bool = True) -> Dict[str, Any]:
        """Analizar múltiples textos en lote."""
        data = {
            "texts": texts,
            "use_local_models": use_local_models,
            "use_gpt_backup": use_gpt_backup
        }
        
        async with self.session.post(f"{self.base_url}/analyze-batch", json=data) as response:
            return await response.json()
    
    async def scrape_providers(self, providers: List[str], use_sample_data: bool = False) -> Dict[str, Any]:
        """Realizar scraping de proveedores."""
        data = {
            "providers": providers,
            "use_sample_data": use_sample_data
        }
        
        async with self.session.post(f"{self.base_url}/scrape", json=data) as response:
            return await response.json()
    
    async def extract_price(self, text: str, currency: str = None) -> Dict[str, Any]:
        """Extraer precio de un texto."""
        data = {"text": text}
        if currency:
            data["currency"] = currency
        
        async with self.session.post(f"{self.base_url}/extract-price", json=data) as response:
            return await response.json()
    
    async def get_model_info(self) -> Dict[str, Any]:
        """Obtener información de modelos."""
        async with self.session.get(f"{self.base_url}/model-info") as response:
            return await response.json()
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del sistema."""
        async with self.session.get(f"{self.base_url}/stats") as response:
            return await response.json()
    
    async def get_function_definitions(self) -> Dict[str, Any]:
        """Obtener definiciones de funciones para GPT."""
        async with self.session.get(f"{self.base_url}/function-definitions") as response:
            return await response.json()

async def example_usage():
    """Ejemplo de uso del cliente API."""
    
    logger.info("🚀 Ejemplo de uso del cliente API")
    
    async with APIClient() as client:
        try:
            # 1. Verificar estado de salud
            logger.info("📊 Verificando estado de salud...")
            health = await client.health_check()
            logger.info(f"Estado de salud: {health['api']}")
            
            # 2. Analizar texto
            logger.info("🔍 Analizando texto...")
            analysis_result = await client.analyze_text(
                text="B2Broker offers comprehensive white label solutions for crypto exchanges. Setup fee starts at $50,000 with monthly maintenance costs of $5,000.",
                source="B2Broker",
                use_local_models=True,
                use_gpt_backup=True
            )
            
            if analysis_result.get("success"):
                data = analysis_result["data"]
                logger.info(f"✅ Análisis exitoso:")
                logger.info(f"   - Clasificación: {data.get('clasificacion_modulo')}")
                logger.info(f"   - Precio: {data.get('precio_estimado')}")
                logger.info(f"   - Método: {data.get('analysis_method')}")
                logger.info(f"   - Tiempo: {analysis_result.get('processing_time', 0):.2f}s")
            else:
                logger.error(f"❌ Error en análisis: {analysis_result}")
            
            # 3. Extraer precio específico
            logger.info("💰 Extrayendo precio...")
            price_result = await client.extract_price(
                text="The monthly subscription costs $2,500 with a one-time setup fee of $10,000.",
                currency="USD"
            )
            
            if price_result.get("success"):
                data = price_result["data"]
                logger.info(f"✅ Precio extraído: {data.get('extracted_price')}")
                logger.info(f"   - Términos: {data.get('pricing_terms')}")
            else:
                logger.error(f"❌ Error extrayendo precio: {price_result}")
            
            # 4. Análisis en lote
            logger.info("📦 Analizando en lote...")
            batch_texts = [
                {"text": "Sumsub provides KYC verification services with AI-powered identity verification. Pricing starts at $0.50 per verification.", "source": "Sumsub"},
                {"text": "Wallester offers secure digital wallet solution with advanced encryption. Monthly subscription costs $2,500.", "source": "Wallester"}
            ]
            
            batch_result = await client.analyze_batch(batch_texts)
            
            if batch_result.get("success"):
                data = batch_result["data"]
                logger.info(f"✅ Análisis en lote exitoso:")
                logger.info(f"   - Procesados: {data.get('total_processed')}")
                logger.info(f"   - Tiempo: {batch_result.get('processing_time', 0):.2f}s")
                
                for i, result in enumerate(data.get("results", [])):
                    logger.info(f"   Resultado {i+1}: {result.get('clasificacion_modulo')} - {result.get('precio_estimado')}")
            else:
                logger.error(f"❌ Error en análisis en lote: {batch_result}")
            
            # 5. Obtener información de modelos
            logger.info("🧠 Obteniendo información de modelos...")
            model_info = await client.get_model_info()
            
            if model_info.get("success"):
                data = model_info["data"]
                if "local_models" in data:
                    models = data["local_models"]
                    logger.info(f"✅ Modelos locales:")
                    logger.info(f"   - Cargados: {models.get('models_loaded', [])}")
                    logger.info(f"   - Device: {models.get('device')}")
            else:
                logger.error(f"❌ Error obteniendo información de modelos: {model_info}")
            
            # 6. Obtener estadísticas del sistema
            logger.info("📈 Obteniendo estadísticas del sistema...")
            stats = await client.get_system_stats()
            logger.info(f"✅ Estadísticas obtenidas: {len(stats)} componentes")
            
            # 7. Obtener definiciones de funciones
            logger.info("🔧 Obteniendo definiciones de funciones...")
            functions = await client.get_function_definitions()
            
            if "functions" in functions:
                function_names = [f["name"] for f in functions["functions"]]
                logger.info(f"✅ Funciones disponibles: {function_names}")
            
        except Exception as e:
            logger.error(f"❌ Error en ejemplo: {str(e)}")

async def gpt_function_calling_example():
    """Ejemplo de cómo usar la API con GPT Function Calling."""
    
    logger.info("🤖 Ejemplo de GPT Function Calling")
    
    async with APIClient() as client:
        try:
            # Obtener definiciones de funciones
            functions = await client.get_function_definitions()
            
            # Simular llamada de función de GPT
            gpt_function_call = {
                "name": "analyze_text",
                "arguments": {
                    "text": "B2Broker offers white label crypto exchange solutions with setup fees starting at $50,000 and monthly maintenance of $5,000.",
                    "source": "B2Broker",
                    "use_local_models": True,
                    "use_gpt_backup": True
                }
            }
            
            # Ejecutar función
            logger.info(f"🔧 Ejecutando función GPT: {gpt_function_call['name']}")
            
            if gpt_function_call["name"] == "analyze_text":
                result = await client.analyze_text(**gpt_function_call["arguments"])
            elif gpt_function_call["name"] == "extract_price":
                result = await client.extract_price(**gpt_function_call["arguments"])
            elif gpt_function_call["name"] == "scrape_providers":
                result = await client.scrape_providers(**gpt_function_call["arguments"])
            else:
                result = {"success": False, "error": "Función no implementada"}
            
            # Mostrar resultado
            if result.get("success"):
                logger.info("✅ Función GPT ejecutada exitosamente")
                logger.info(f"   Resultado: {json.dumps(result['data'], indent=2, ensure_ascii=False)}")
            else:
                logger.error(f"❌ Error ejecutando función GPT: {result}")
                
        except Exception as e:
            logger.error(f"❌ Error en ejemplo GPT: {str(e)}")

if __name__ == "__main__":
    logger.info("🎯 Ejecutando ejemplos del cliente API...")
    
    # Ejecutar ejemplos
    asyncio.run(example_usage())
    print("\n" + "="*50 + "\n")
    asyncio.run(gpt_function_calling_example())
    
    logger.info("✅ Ejemplos completados") 