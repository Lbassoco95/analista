"""
Analizador optimizado que combina Hugging Face Transformers con análisis GPT.
Implementa principios de desarrollo robusto y eficiente.
"""

import os
import json
import time
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio
import aiohttp

# Imports locales
from .model_manager import ModelManager
from .extract_price import extract_price_from_text, clean_text

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptimizedAnalyzer:
    """
    Analizador optimizado que combina modelos locales (Hugging Face) 
    con análisis GPT para máxima eficiencia y precisión.
    """
    
    def __init__(self, use_local_models: bool = True, use_gpt: bool = True):
        """
        Inicializar el analizador optimizado.
        
        Args:
            use_local_models: Si usar modelos locales de Hugging Face
            use_gpt: Si usar análisis GPT como respaldo
        """
        self.use_local_models = use_local_models
        self.use_gpt = use_gpt
        
        # Inicializar gestor de modelos locales
        if use_local_models:
            try:
                self.model_manager = ModelManager()
                logger.info("Local models initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize local models: {str(e)}")
                self.use_local_models = False
                self.model_manager = None
        
        # Configurar OpenAI si está disponible
        if use_gpt:
            try:
                import openai
                self.openai_available = True
                logger.info("OpenAI GPT available for backup analysis")
            except ImportError:
                self.openai_available = False
                logger.warning("OpenAI not available, using local models only")
        
        # Cache para resultados
        self.analysis_cache = {}
        self.cache_ttl = 3600  # 1 hora
        
        # Configurar procesamiento paralelo
        self.max_workers = min(4, os.cpu_count() or 1)
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
    
    async def analyze_text_optimized(self, text: str, source: str = "unknown") -> Dict[str, Any]:
        """
        Analizar texto usando estrategia optimizada.
        
        Args:
            text: Texto a analizar
            source: Fuente del texto para logging
            
        Returns:
            Resultado del análisis optimizado
        """
        # Verificar cache primero
        cache_key = f"{hash(text)}_{source}"
        if cache_key in self.analysis_cache:
            cached_result = self.analysis_cache[cache_key]
            if time.time() - cached_result.get("timestamp", 0) < self.cache_ttl:
                logger.info(f"Using cached analysis for {source}")
                return cached_result["result"]
        
        # Limpiar texto
        cleaned_text = clean_text(text)
        
        # Estrategia de análisis en cascada
        analysis_result = await self._cascade_analysis(cleaned_text, source)
        
        # Guardar en cache
        self.analysis_cache[cache_key] = {
            "result": analysis_result,
            "timestamp": time.time()
        }
        
        return analysis_result
    
    async def _cascade_analysis(self, text: str, source: str) -> Dict[str, Any]:
        """
        Análisis en cascada: modelos locales primero, GPT como respaldo.
        
        Args:
            text: Texto limpio a analizar
            source: Fuente del texto
            
        Returns:
            Resultado del análisis
        """
        result = {
            "fuente": source,
            "timestamp": datetime.now().isoformat(),
            "analysis_method": "unknown",
            "precio_estimado": "No especificado",
            "clasificacion_modulo": "No clasificado",
            "condiciones_comerciales": {},
            "confianza_analisis": "baja"
        }
        
        # Paso 1: Análisis con modelos locales (más rápido)
        if self.use_local_models and self.model_manager:
            try:
                local_result = await self._analyze_with_local_models(text)
                if local_result and local_result.get("confianza_analisis") != "baja":
                    result.update(local_result)
                    result["analysis_method"] = "local_models"
                    logger.info(f"Local analysis successful for {source}")
                    return result
            except Exception as e:
                logger.warning(f"Local analysis failed for {source}: {str(e)}")
        
        # Paso 2: Análisis con GPT (más preciso, pero más lento)
        if self.use_gpt and self.openai_available:
            try:
                gpt_result = await self._analyze_with_gpt(text)
                if gpt_result:
                    result.update(gpt_result)
                    result["analysis_method"] = "gpt"
                    logger.info(f"GPT analysis successful for {source}")
                    return result
            except Exception as e:
                logger.warning(f"GPT analysis failed for {source}: {str(e)}")
        
        # Paso 3: Análisis básico como último recurso
        basic_result = self._basic_analysis(text)
        result.update(basic_result)
        result["analysis_method"] = "basic"
        logger.info(f"Basic analysis used for {source}")
        
        return result
    
    async def _analyze_with_local_models(self, text: str) -> Optional[Dict[str, Any]]:
        """Análisis usando modelos locales de Hugging Face."""
        try:
            # Análisis de clasificación
            classification_result = self.model_manager.analyze_text_with_local_model(
                text, task="classification"
            )
            
            # Extracción de precios con BERT
            price_result = self.model_manager.extract_price_with_bert(text)
            
            # Análisis de embeddings para similitud
            embedding_result = self.model_manager.analyze_text_with_local_model(
                text, task="embedding"
            )
            
            # Combinar resultados
            result = {
                "clasificacion_modulo": classification_result.get("clasificacion_modulo"),
                "confianza_analisis": classification_result.get("confianza_analisis"),
                "precio_estimado": price_result if price_result else "No especificado",
                "embedding_info": embedding_result.get("embedding_dim"),
                "scores": classification_result.get("scores", {})
            }
            
            # Extraer condiciones comerciales básicas
            result["condiciones_comerciales"] = self._extract_basic_conditions(text)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in local model analysis: {str(e)}")
            return None
    
    async def _analyze_with_gpt(self, text: str) -> Optional[Dict[str, Any]]:
        """Análisis usando GPT como respaldo."""
        try:
            import openai
            
            # Prompt optimizado para GPT
            prompt = self._create_optimized_gpt_prompt(text)
            
            # Llamada a GPT con timeout
            async with aiohttp.ClientSession() as session:
                response = await asyncio.wait_for(
                    self._call_gpt_async(session, prompt),
                    timeout=30.0
                )
            
            if response:
                return self._parse_gpt_response(response)
            
        except Exception as e:
            logger.error(f"Error in GPT analysis: {str(e)}")
        
        return None
    
    async def _call_gpt_async(self, session: aiohttp.ClientSession, prompt: str) -> Optional[str]:
        """Llamada asíncrona a GPT."""
        try:
            import openai
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un analista experto en servicios financieros y tecnología blockchain."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error calling GPT: {str(e)}")
            return None
    
    def _create_optimized_gpt_prompt(self, text: str) -> str:
        """Crear prompt optimizado para GPT."""
        return f"""
        Analiza el siguiente texto de un proveedor de servicios de marca blanca y proporciona:

        1. **Precio estimado**: Formato "$X,XXX" o "No especificado"
        2. **Clasificación del módulo**: Una de estas categorías:
           - Wallet Base, Wallet Avanzado, KYC/KYB, Tarjeta, Trading Platform
           - Payment Gateway, Liquidity Provider, Compliance, API Integration
           - White Label Solution, Otro (especificar)
        3. **Condiciones comerciales**: JSON con setup_fee, monthly_cost, transaction_fees, etc.

        Texto: {text[:1000]}...

        Responde en formato JSON:
        {{
            "precio_estimado": "string",
            "clasificacion_modulo": "string",
            "condiciones_comerciales": {{
                "setup_fee": "string",
                "monthly_cost": "string",
                "transaction_fees": "string",
                "minimum_requirements": "string",
                "contract_terms": "string"
            }},
            "confianza_analisis": "alta|media|baja"
        }}
        """
    
    def _parse_gpt_response(self, response: str) -> Dict[str, Any]:
        """Parsear respuesta de GPT."""
        try:
            # Limpiar respuesta si tiene markdown
            if response.startswith('```json'):
                response = response.replace('```json', '').replace('```', '').strip()
            
            return json.loads(response)
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing GPT response: {str(e)}")
            return self._get_fallback_analysis()
    
    def _basic_analysis(self, text: str) -> Dict[str, Any]:
        """Análisis básico como último recurso."""
        # Extraer precio usando regex
        price = extract_price_from_text(text)
        
        # Clasificación básica por palabras clave
        text_lower = text.lower()
        module = "General Service"
        
        if any(keyword in text_lower for keyword in ["wallet", "crypto"]):
            module = "Wallet Base"
        elif any(keyword in text_lower for keyword in ["kyc", "kyb", "verification"]):
            module = "KYC/KYB"
        elif any(keyword in text_lower for keyword in ["trading", "exchange"]):
            module = "Trading Platform"
        elif any(keyword in text_lower for keyword in ["payment", "gateway"]):
            module = "Payment Gateway"
        elif any(keyword in text_lower for keyword in ["white label", "whitelabel"]):
            module = "White Label Solution"
        
        return {
            "precio_estimado": price if price else "No especificado",
            "clasificacion_modulo": module,
            "confianza_analisis": "baja",
            "condiciones_comerciales": self._extract_basic_conditions(text)
        }
    
    def _extract_basic_conditions(self, text: str) -> Dict[str, str]:
        """Extraer condiciones comerciales básicas."""
        text_lower = text.lower()
        conditions = {
            "setup_fee": "No especificado",
            "monthly_cost": "No especificado",
            "transaction_fees": "No especificado",
            "minimum_requirements": "No especificado",
            "contract_terms": "No especificado"
        }
        
        # Buscar patrones básicos
        if "setup" in text_lower and "fee" in text_lower:
            conditions["setup_fee"] = "Mencionado"
        if "monthly" in text_lower and "cost" in text_lower:
            conditions["monthly_cost"] = "Mencionado"
        if "transaction" in text_lower and "fee" in text_lower:
            conditions["transaction_fees"] = "Mencionado"
        
        return conditions
    
    def _get_fallback_analysis(self) -> Dict[str, Any]:
        """Análisis de respaldo cuando todo falla."""
        return {
            "precio_estimado": "No especificado",
            "clasificacion_modulo": "No clasificado",
            "confianza_analisis": "baja",
            "condiciones_comerciales": {
                "setup_fee": "No especificado",
                "monthly_cost": "No especificado",
                "transaction_fees": "No especificado",
                "minimum_requirements": "No especificado",
                "contract_terms": "No especificado"
            }
        }
    
    async def analyze_batch_optimized(self, texts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analizar lote de textos de forma optimizada y paralela.
        
        Args:
            texts: Lista de diccionarios con 'text' y 'source'
            
        Returns:
            Lista de resultados de análisis
        """
        logger.info(f"Starting batch analysis of {len(texts)} texts")
        
        # Procesar en paralelo
        tasks = []
        for text_data in texts:
            task = self.analyze_text_optimized(
                text_data.get('text', ''),
                text_data.get('source', 'unknown')
            )
            task = asyncio.create_task(task)
            tasks.append(task)
        
        # Ejecutar todas las tareas
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Procesar resultados
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error analyzing text {i}: {str(result)}")
                processed_results.append(self._get_fallback_analysis())
            else:
                processed_results.append(result)
        
        logger.info(f"Batch analysis completed: {len(processed_results)} results")
        return processed_results
    
    def get_analysis_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del análisis."""
        stats = {
            "cache_size": len(self.analysis_cache),
            "cache_hit_rate": 0.0,
            "analysis_methods": {},
            "performance_metrics": {}
        }
        
        # Calcular estadísticas de métodos de análisis
        method_counts = {}
        for cached_result in self.analysis_cache.values():
            method = cached_result["result"].get("analysis_method", "unknown")
            method_counts[method] = method_counts.get(method, 0) + 1
        
        stats["analysis_methods"] = method_counts
        
        # Información de modelos locales si están disponibles
        if self.model_manager:
            stats["local_models"] = self.model_manager.get_model_info()
        
        return stats
    
    def clear_cache(self):
        """Limpiar cache de análisis."""
        self.analysis_cache.clear()
        logger.info("Analysis cache cleared")
    
    def optimize_cache(self, max_size: int = 1000):
        """Optimizar cache eliminando entradas antiguas."""
        if len(self.analysis_cache) > max_size:
            # Eliminar entradas más antiguas
            current_time = time.time()
            old_entries = [
                key for key, value in self.analysis_cache.items()
                if current_time - value.get("timestamp", 0) > self.cache_ttl
            ]
            
            for key in old_entries:
                del self.analysis_cache[key]
            
            logger.info(f"Cache optimized: removed {len(old_entries)} old entries") 