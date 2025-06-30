#!/usr/bin/env python3
"""
Analizador LR Completo - Orquestador del flujo de análisis
Implementa el flujo: Scraping → Procesamiento → Embeddings → Almacenamiento → Consulta
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import os
from pathlib import Path

# Importaciones de nuestros módulos
from scraper_inteligente import ScraperInteligente
from utils.pinecone_manager import PineconeManager
from utils.chat_gpt_manager import ChatGPTManager
from utils.extract_price import extract_white_label_info, extract_latam_metadata
from modules.sumsub import SumsubScraper

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('analizador_lr.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AnalizadorLRCompleto:
    """
    Orquestador principal que implementa el flujo LR completo:
    A[Scraping] → B[Procesamiento] → C[Embeddings] → D[Almacenamiento] → E[Consulta]
    """
    
    def __init__(self):
        """Inicializa todos los componentes del flujo LR"""
        self.scraper = ScraperInteligente()
        self.pinecone_manager = PineconeManager()
        self.chat_manager = ChatGPTManager()
        self.sumsub_scraper = SumsubScraper()
        
        # Configuración del flujo
        self.config = {
            'batch_size': 10,
            'max_retries': 3,
            'delay_between_batches': 2,
            'enable_validation': True,
            'enable_metadata_enrichment': True,
            'target_regions': ['LATAM', 'México', 'Brasil', 'Argentina', 'Colombia', 'Chile']
        }
        
        logger.info("Analizador LR Completo inicializado")
    
    async def ejecutar_flujo_completo(self, proveedores: List[str]) -> Dict[str, Any]:
        """
        Ejecuta el flujo LR completo para una lista de proveedores
        
        Args:
            proveedores: Lista de nombres de proveedores a analizar
            
        Returns:
            Dict con resultados del flujo completo
        """
        logger.info(f"Iniciando flujo LR completo para {len(proveedores)} proveedores")
        
        resultados = {
            'timestamp': datetime.now().isoformat(),
            'proveedores_analizados': len(proveedores),
            'etapas': {},
            'estadisticas': {},
            'errores': []
        }
        
        try:
            # ETAPA A: Scraping con Playwright/Apify
            logger.info("=== ETAPA A: Scraping ===")
            datos_scraping = await self._etapa_scraping(proveedores)
            resultados['etapas']['scraping'] = datos_scraping
            
            # ETAPA B: Procesamiento con LangChain
            logger.info("=== ETAPA B: Procesamiento ===")
            datos_procesados = await self._etapa_procesamiento(datos_scraping['datos'])
            resultados['etapas']['procesamiento'] = datos_procesados
            
            # ETAPA C: Generación de Embeddings
            logger.info("=== ETAPA C: Embeddings ===")
            embeddings_data = await self._etapa_embeddings(datos_procesados['datos'])
            resultados['etapas']['embeddings'] = embeddings_data
            
            # ETAPA D: Almacenamiento en Pinecone
            logger.info("=== ETAPA D: Almacenamiento ===")
            almacenamiento_data = await self._etapa_almacenamiento(embeddings_data['datos'])
            resultados['etapas']['almacenamiento'] = almacenamiento_data
            
            # ETAPA E: Consulta vía LLM
            logger.info("=== ETAPA E: Consulta ===")
            consulta_data = await self._etapa_consulta(proveedores)
            resultados['etapas']['consulta'] = consulta_data
            
            # Generar estadísticas finales
            resultados['estadisticas'] = await self._generar_estadisticas()
            
            logger.info("Flujo LR completo ejecutado exitosamente")
            
        except Exception as e:
            logger.error(f"Error en flujo LR: {str(e)}")
            resultados['errores'].append(str(e))
        
        return resultados
    
    async def _etapa_scraping(self, proveedores: List[str]) -> Dict[str, Any]:
        """ETAPA A: Scraping con Playwright/Apify"""
        logger.info(f"Ejecutando scraping para {len(proveedores)} proveedores")
        
        datos_scraping = {
            'total_proveedores': len(proveedores),
            'datos': [],
            'estadisticas': {}
        }
        
        for i, proveedor in enumerate(proveedores):
            try:
                logger.info(f"Scraping proveedor {i+1}/{len(proveedores)}: {proveedor}")
                
                # Usar scraper inteligente con búsqueda semi-dirigida
                # Buscar URLs relacionadas con el proveedor
                query = f"{proveedor} pricing LATAM Mexico"
                urls = self.scraper.buscar_urls_google(query, limit=3)
                
                datos_proveedor = []
                for url in urls:
                    contenido = self.scraper.scrape_url(url)
                    if contenido:
                        metadata = self.scraper.extraer_metadata_latam(contenido)
                        datos_proveedor.append({
                            'url': url,
                            'contenido': contenido,
                            'metadata': metadata
                        })
                
                if datos_proveedor:
                    datos_scraping['datos'].append({
                        'proveedor': proveedor,
                        'datos_raw': datos_proveedor,
                        'timestamp': datetime.now().isoformat()
                    })
                
                # Pausa entre proveedores
                if i < len(proveedores) - 1:
                    await asyncio.sleep(self.config['delay_between_batches'])
                    
            except Exception as e:
                logger.error(f"Error scraping {proveedor}: {str(e)}")
                datos_scraping['datos'].append({
                    'proveedor': proveedor,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        datos_scraping['estadisticas'] = {
            'exitosos': len([d for d in datos_scraping['datos'] if 'datos_raw' in d]),
            'fallidos': len([d for d in datos_scraping['datos'] if 'error' in d]),
            'total_datos': sum(len(d.get('datos_raw', [])) for d in datos_scraping['datos'])
        }
        
        logger.info(f"Scraping completado: {datos_scraping['estadisticas']}")
        return datos_scraping
    
    async def _etapa_procesamiento(self, datos_scraping: List[Dict]) -> Dict[str, Any]:
        """ETAPA B: Procesamiento con LangChain"""
        logger.info("Procesando datos con LangChain")
        
        datos_procesados = {
            'total_items': 0,
            'datos': [],
            'metadata_enriquecida': []
        }
        
        for item in datos_scraping:
            if 'datos_raw' not in item:
                continue
                
            proveedor = item['proveedor']
            datos_raw = item['datos_raw']
            
            for dato in datos_raw:
                try:
                    # Procesar con LangChain para extraer información estructurada
                    datos_procesados_item = await self._procesar_con_langchain(dato, proveedor)
                    
                    if datos_procesados_item:
                        datos_procesados['datos'].append(datos_procesados_item)
                        datos_procesados['total_items'] += 1
                        
                        # Enriquecer metadata automáticamente
                        if self.config['enable_metadata_enrichment']:
                            metadata_enriquecida = await self._enriquecer_metadata(datos_procesados_item)
                            datos_procesados['metadata_enriquecida'].append(metadata_enriquecida)
                
                except Exception as e:
                    logger.error(f"Error procesando dato de {proveedor}: {str(e)}")
        
        logger.info(f"Procesamiento completado: {datos_procesados['total_items']} items procesados")
        return datos_procesados
    
    async def _procesar_con_langchain(self, dato: Dict, proveedor: str) -> Optional[Dict]:
        """Procesa un dato individual con LangChain"""
        try:
            # Extraer información estructurada usando LangChain
            prompt = f"""
            Analiza la siguiente información del proveedor {proveedor} y extrae:
            1. Nombre del proveedor
            2. Tipo de servicio/producto
            3. Precios y tarifas
            4. Región/país de operación
            5. Características principales
            6. Información de contacto
            
            Información: {json.dumps(dato, ensure_ascii=False)}
            
            Responde en formato JSON estructurado.
            """
            
            # Usar el chat manager para procesar
            respuesta = await self.chat_manager.chat_with_context(
                query=prompt,
                pinecone_manager=self.pinecone_manager
            )
            
            if respuesta and respuesta.get('success'):
                return {
                    'proveedor': proveedor,
                    'datos_originales': dato,
                    'datos_procesados': respuesta['response'],
                    'timestamp_procesamiento': datetime.now().isoformat()
                }
        
        except Exception as e:
            logger.error(f"Error en procesamiento LangChain: {str(e)}")
        
        return None
    
    async def _enriquecer_metadata(self, datos_procesados: Dict) -> Dict:
        """Enriquece automáticamente la metadata"""
        try:
            datos = datos_procesados['datos_procesados']
            
            # Extraer metadata LATAM
            metadata_latam = extract_latam_metadata(datos)
            
            # Validar datos cruzados con GPT
            if self.config['enable_validation']:
                # Usar el método de validación del scraper
                validacion = self.scraper.validar_con_gpt(
                    text1=datos,
                    text2=datos,  # Auto-validación
                    module='general'
                )
                metadata_latam['validacion_cruzada'] = validacion
            
            return {
                'id': f"{datos_procesados['proveedor']}_{datetime.now().timestamp()}",
                'metadata': metadata_latam,
                'timestamp_enriquecimiento': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error enriquecimiento metadata: {str(e)}")
            return {}
    
    async def _etapa_embeddings(self, datos_procesados: List[Dict]) -> Dict[str, Any]:
        """ETAPA C: Generación de Embeddings con OpenAI"""
        logger.info("Generando embeddings con OpenAI")
        
        embeddings_data = {
            'total_embeddings': 0,
            'datos': [],
            'estadisticas': {}
        }
        
        for item in datos_procesados:
            try:
                # Crear embedding del texto procesado
                texto_para_embedding = json.dumps(item['datos_procesados'], ensure_ascii=False)
                
                embedding = self.pinecone_manager.create_embedding(texto_para_embedding)
                
                if embedding:
                    embeddings_data['datos'].append({
                        'id': item.get('id', f"item_{embeddings_data['total_embeddings']}"),
                        'embedding': embedding,
                        'metadata': item.get('metadata', {}),
                        'datos_originales': item,
                        'timestamp_embedding': datetime.now().isoformat()
                    })
                    embeddings_data['total_embeddings'] += 1
            
            except Exception as e:
                logger.error(f"Error generando embedding: {str(e)}")
        
        embeddings_data['estadisticas'] = {
            'embeddings_generados': embeddings_data['total_embeddings'],
            'dimension_embedding': len(embeddings_data['datos'][0]['embedding']) if embeddings_data['datos'] else 0
        }
        
        logger.info(f"Embeddings generados: {embeddings_data['estadisticas']}")
        return embeddings_data
    
    async def _etapa_almacenamiento(self, embeddings_data: List[Dict]) -> Dict[str, Any]:
        """ETAPA D: Almacenamiento en Pinecone"""
        logger.info("Almacenando datos en Pinecone")
        
        almacenamiento_data = {
            'total_almacenados': 0,
            'ids_almacenados': [],
            'estadisticas': {}
        }
        
        for item in embeddings_data:
            try:
                # Almacenar en Pinecone
                texto_original = json.dumps(item['datos_originales'], ensure_ascii=False)
                metadata = item.get('metadata', {})
                
                success = self.pinecone_manager.store_data(
                    text=texto_original,
                    metadata=metadata,
                    vector_id=item['id']
                )
                
                if success:
                    almacenamiento_data['ids_almacenados'].append(item['id'])
                    almacenamiento_data['total_almacenados'] += 1
            
            except Exception as e:
                logger.error(f"Error almacenando en Pinecone: {str(e)}")
        
        almacenamiento_data['estadisticas'] = {
            'almacenados_exitosamente': almacenamiento_data['total_almacenados'],
            'tasa_exito': almacenamiento_data['total_almacenados'] / len(embeddings_data) if embeddings_data else 0
        }
        
        logger.info(f"Almacenamiento completado: {almacenamiento_data['estadisticas']}")
        return almacenamiento_data
    
    async def _etapa_consulta(self, proveedores: List[str]) -> Dict[str, Any]:
        """ETAPA E: Consulta vía LLM"""
        logger.info("Ejecutando consultas vía LLM")
        
        consulta_data = {
            'consultas_ejecutadas': 0,
            'resultados': [],
            'insights': {}
        }
        
        # Consultas predefinidas para análisis
        consultas = [
            f"¿Cuáles son los mejores proveedores en LATAM para servicios financieros?",
            f"Compara los precios y características de los proveedores analizados",
            f"¿Qué tendencias observas en el mercado LATAM?",
            f"Recomienda proveedores específicos para México y Brasil"
        ]
        
        for consulta in consultas:
            try:
                logger.info(f"Ejecutando consulta: {consulta}")
                
                # Usar el chat manager para consultas inteligentes
                resultado = await self.chat_manager.chat_with_context(
                    query=consulta,
                    pinecone_manager=self.pinecone_manager
                )
                
                if resultado and resultado.get('success'):
                    consulta_data['resultados'].append({
                        'consulta': consulta,
                        'respuesta': resultado['response'],
                        'timestamp': datetime.now().isoformat()
                    })
                    consulta_data['consultas_ejecutadas'] += 1
            
            except Exception as e:
                logger.error(f"Error en consulta: {str(e)}")
        
        # Generar insights generales
        consulta_data['insights'] = await self._generar_insights_generales(proveedores)
        
        logger.info(f"Consultas completadas: {consulta_data['consultas_ejecutadas']} consultas")
        return consulta_data
    
    async def _generar_insights_generales(self, proveedores: List[str]) -> Dict[str, Any]:
        """Genera insights generales del análisis"""
        try:
            prompt = f"""
            Basándote en el análisis de los proveedores {', '.join(proveedores)}, genera insights sobre:
            1. Tendencias del mercado LATAM
            2. Oportunidades de negocio
            3. Proveedores más competitivos
            4. Recomendaciones estratégicas
            
            Responde en formato JSON estructurado.
            """
            
            resultado = await self.chat_manager.chat_with_context(
                query=prompt,
                pinecone_manager=self.pinecone_manager
            )
            
            if resultado and resultado.get('success'):
                return {'insights': resultado['response']}
            return {}
        
        except Exception as e:
            logger.error(f"Error generando insights: {str(e)}")
            return {}
    
    async def _generar_estadisticas(self) -> Dict[str, Any]:
        """Genera estadísticas finales del flujo"""
        try:
            stats = self.pinecone_manager.get_statistics()
            return {
                'total_datos_pinecone': stats.get('total_vectors', 0),
                'dimension_embeddings': stats.get('dimension', 0),
                'metadata_fields': stats.get('metadata_fields', []),
                'timestamp_estadisticas': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {str(e)}")
            return {}
    
    async def consulta_interactiva(self, pregunta: str) -> str:
        """
        Permite consultas interactivas usando el contexto almacenado
        
        Args:
            pregunta: Pregunta del usuario
            
        Returns:
            Respuesta basada en el contexto almacenado
        """
        try:
            resultado = await self.chat_manager.chat_with_context(
                query=pregunta,
                pinecone_manager=self.pinecone_manager
            )
            
            if resultado and resultado.get('success'):
                return resultado['response']
            else:
                return "No se pudo procesar la consulta. Intenta reformular tu pregunta."
                
        except Exception as e:
            logger.error(f"Error en consulta interactiva: {str(e)}")
            return f"Error procesando la consulta: {str(e)}"
    
    def guardar_resultados(self, resultados: Dict[str, Any], filename: Optional[str] = None):
        """Guarda los resultados del flujo en un archivo JSON"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"resultados_lr_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(resultados, f, ensure_ascii=False, indent=2)
            logger.info(f"Resultados guardados en {filename}")
        except Exception as e:
            logger.error(f"Error guardando resultados: {str(e)}")

# Función principal para ejecutar el flujo
async def main():
    """Función principal para ejecutar el flujo LR completo"""
    
    # Lista de proveedores a analizar
    proveedores = [
        "Sumsub",
        "Jumio",
        "Onfido",
        "Veriff",
        "IDnow",
        "Acuant",
        "Mitek",
        "iProov"
    ]
    
    # Inicializar analizador
    analizador = AnalizadorLRCompleto()
    
    # Ejecutar flujo completo
    resultados = await analizador.ejecutar_flujo_completo(proveedores)
    
    # Guardar resultados
    analizador.guardar_resultados(resultados)
    
    # Mostrar resumen
    print("\n=== RESUMEN DEL FLUJO LR ===")
    print(f"Proveedores analizados: {resultados['proveedores_analizados']}")
    print(f"Etapas completadas: {len(resultados['etapas'])}")
    print(f"Errores: {len(resultados['errores'])}")
    
    # Ejemplo de consulta interactiva
    print("\n=== CONSULTA INTERACTIVA ===")
    pregunta = "¿Cuáles son los mejores proveedores de KYC en México?"
    respuesta = await analizador.consulta_interactiva(pregunta)
    print(f"Pregunta: {pregunta}")
    print(f"Respuesta: {respuesta}")

if __name__ == "__main__":
    asyncio.run(main())
