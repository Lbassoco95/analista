"""
Scraper Inteligente con búsqueda semi-dirigida, validación cruzada y análisis GPT.
Implementa la lógica escalable propuesta para análisis de proveedores LATAM.
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import time
import random

import requests
from bs4 import BeautifulSoup
import openai

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScraperInteligente:
    """
    Scraper inteligente con búsqueda semi-dirigida y validación cruzada.
    """
    
    def __init__(self):
        """Inicializar scraper inteligente."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Configurar OpenAI
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        
        # Templates de búsqueda por módulo
        self.search_templates = {
            'wallet': [
                'white label crypto wallet pricing LATAM',
                'crypto wallet API cost Mexico',
                'digital wallet solution pricing Argentina',
                'white label wallet provider Colombia',
                'crypto wallet development cost Chile'
            ],
            'kyc': [
                'KYC verification pricing LATAM',
                'identity verification cost Mexico',
                'KYC API pricing Argentina',
                'compliance verification Colombia',
                'onboarding verification Chile'
            ],
            'trading': [
                'crypto exchange white label pricing LATAM',
                'trading platform cost Mexico',
                'exchange API pricing Argentina',
                'trading solution Colombia',
                'crypto trading platform Chile'
            ],
            'payment': [
                'payment gateway crypto LATAM',
                'fiat onramp pricing Mexico',
                'payment processing Argentina',
                'gateway solution Colombia',
                'payment API Chile'
            ],
            'signature': [
                'digital signature solution LATAM',
                'e-signature pricing Mexico',
                'digital certificate Argentina',
                'signature API Colombia',
                'electronic signature Chile'
            ],
            'custody': [
                'crypto custody solution LATAM',
                'custodial service pricing Mexico',
                'cold storage Argentina',
                'custody provider Colombia',
                'digital asset custody Chile'
            ]
        }
        
        # Países LATAM
        self.latam_countries = [
            'México', 'Mexico', 'Argentina', 'Colombia', 'Chile', 'Perú', 'Uruguay', 
            'Paraguay', 'Bolivia', 'Ecuador', 'Venezuela', 'Guatemala', 'Honduras', 
            'El Salvador', 'Nicaragua', 'Costa Rica', 'Panamá', 'Cuba', 
            'República Dominicana', 'Puerto Rico'
        ]
        
        logger.info("✅ ScraperInteligente inicializado")
    
    def buscar_urls_google(self, query: str, limit: int = 5) -> List[str]:
        """
        Buscar URLs en Google usando búsqueda web.
        Nota: En producción, usar SerpAPI o similar para resultados más precisos.
        
        Args:
            query: Consulta de búsqueda
            limit: Número máximo de URLs
            
        Returns:
            Lista de URLs encontradas
        """
        try:
            # Simular búsqueda (en producción usar API real)
            logger.info(f"🔍 Buscando: {query}")
            
            # URLs de ejemplo para testing
            sample_urls = [
                'https://sumsub.com/pricing/',
                'https://b2broker.com/white-label/',
                'https://wallester.com/solutions/',
                'https://example-provider.com/latam/',
                'https://crypto-solutions.com/mexico/'
            ]
            
            # Filtrar URLs que contengan palabras clave relevantes
            relevant_urls = []
            for url in sample_urls:
                if any(keyword in query.lower() for keyword in ['pricing', 'cost', 'latam', 'mexico', 'argentina']):
                    relevant_urls.append(url)
            
            return relevant_urls[:limit]
            
        except Exception as e:
            logger.error(f"❌ Error en búsqueda: {str(e)}")
            return []
    
    def scrape_url(self, url: str) -> Optional[str]:
        """
        Scrapear contenido de una URL.
        
        Args:
            url: URL a scrapear
            
        Returns:
            Texto extraído o None
        """
        try:
            logger.info(f"📄 Scrapeando: {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraer texto de elementos principales
            text_content = []
            
            selectors = [
                'main', '.main-content', '.content', '.page-content',
                'article', '.post-content', '.hero-section', '.pricing-section'
            ]
            
            for selector in selectors:
                elements = soup.select(selector)
                for element in elements:
                    text_content.append(element.get_text())
            
            # Si no se encontró contenido, extraer del body
            if not text_content:
                body = soup.find('body')
                if body:
                    text_content.append(body.get_text())
            
            full_text = ' '.join(text_content)
            
            # Limpiar texto
            import re
            full_text = re.sub(r'\s+', ' ', full_text).strip()
            
            logger.info(f"✅ Extraídos {len(full_text)} caracteres de {url}")
            return full_text
            
        except Exception as e:
            logger.error(f"❌ Error scrapeando {url}: {str(e)}")
            return None
    
    def extraer_metadata_latam(self, text: str) -> Dict[str, Any]:
        """
        Extraer metadata específica para LATAM/México.
        
        Args:
            text: Texto a analizar
            
        Returns:
            Metadata extraída
        """
        from utils.extract_price import extract_latam_metadata, extract_price_from_text
        
        metadata = extract_latam_metadata(text)
        
        # Extraer precio
        price = extract_price_from_text(text)
        if price:
            metadata['precio_estimado'] = price
        
        # Detectar proveedor
        providers = ['sumsub', 'b2broker', 'wallester', 'coinfirm', 'jumio']
        for provider in providers:
            if provider.lower() in text.lower():
                metadata['proveedor'] = provider.title()
                break
        
        # Detectar módulo
        modules = {
            'wallet': ['wallet', 'white label'],
            'kyc': ['kyc', 'kyb', 'verification', 'identity'],
            'trading': ['trading', 'exchange'],
            'payment': ['payment', 'gateway'],
            'signature': ['signature', 'certificate'],
            'custody': ['custody', 'custodial']
        }
        
        for module, keywords in modules.items():
            if any(keyword in text.lower() for keyword in keywords):
                metadata['modulo'] = module.title()
                break
        
        return metadata
    
    def validar_con_gpt(self, text1: str, text2: str, module: str) -> Dict[str, Any]:
        """
        Validar si dos textos se refieren al mismo dato usando GPT.
        
        Args:
            text1: Primer texto
            text2: Segundo texto
            module: Módulo que se está comparando
            
        Returns:
            Resultado de validación
        """
        if not self.openai_api_key:
            return {'confidence': 0, 'validated': False, 'reason': 'OpenAI no configurado'}
        
        try:
            prompt = f"""
Analiza si estos dos textos se refieren al mismo precio o condiciones para el mismo módulo de servicios financieros.

Módulo: {module}

Texto 1: {text1[:500]}...

Texto 2: {text2[:500]}...

Responde en formato JSON:
{{
    "same_data": true/false,
    "confidence": 0-100,
    "reason": "explicación",
    "price_match": true/false,
    "country_match": true/false
}}
"""
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un experto en análisis de datos financieros. Responde solo en JSON válido."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content
            result = json.loads(result_text)
            
            return {
                'confidence': result.get('confidence', 0),
                'validated': result.get('same_data', False),
                'reason': result.get('reason', ''),
                'price_match': result.get('price_match', False),
                'country_match': result.get('country_match', False)
            }
            
        except Exception as e:
            logger.error(f"❌ Error en validación GPT: {str(e)}")
            return {'confidence': 0, 'validated': False, 'reason': str(e)}
    
    def scrape_modulo(self, module: str, country: str = None) -> List[Dict[str, Any]]:
        """
        Scrapear información de un módulo específico.
        
        Args:
            module: Módulo a scrapear
            country: País específico (opcional)
            
        Returns:
            Lista de datos extraídos y validados
        """
        logger.info(f"🚀 Iniciando scraping del módulo: {module}")
        
        results = []
        templates = self.search_templates.get(module, [])
        
        for template in templates:
            # Agregar país si se especifica
            if country:
                template = f"{template} {country}"
            
            # Buscar URLs
            urls = self.buscar_urls_google(template, limit=3)
            
            for url in urls:
                # Scrapear URL
                text = self.scrape_url(url)
                if not text:
                    continue
                
                # Extraer metadata
                metadata = self.extraer_metadata_latam(text)
                metadata['url'] = url
                metadata['modulo'] = module
                
                # Solo procesar si es LATAM/México
                if not metadata.get('pais'):
                    logger.info(f"⏭️ Saltando - No es LATAM/México: {url}")
                    continue
                
                # Validar con datos existentes si hay
                if results:
                    # Validar con el último resultado
                    validation = self.validar_con_gpt(text, results[-1]['texto'], module)
                    if validation['validated']:
                        metadata['validado_cruzado'] = True
                        metadata['confianza'] = max(metadata.get('confianza', 0), validation['confidence'])
                        logger.info(f"✅ Validado cruzado - Confianza: {validation['confidence']}%")
                
                # Agregar a resultados
                result = {
                    'texto': text,
                    'metadata': metadata,
                    'url': url,
                    'timestamp': datetime.now().isoformat()
                }
                
                results.append(result)
                logger.info(f"✅ Datos extraídos: {metadata.get('proveedor', 'N/A')} - {metadata.get('pais', 'N/A')} - {metadata.get('precio_estimado', 'N/A')}")
                
                # Pausa entre requests
                time.sleep(random.uniform(1, 3))
        
        logger.info(f"📊 Scraping completado - {len(results)} resultados para {module}")
        return results
    
    def scrape_todos_modulos(self, countries: List[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Scrapear todos los módulos disponibles.
        
        Args:
            countries: Lista de países específicos (opcional)
            
        Returns:
            Diccionario con resultados por módulo
        """
        if not countries:
            countries = ['México', 'Argentina', 'Colombia', 'Chile', 'Perú']
        
        all_results = {}
        
        for module in self.search_templates.keys():
            logger.info(f"🔄 Procesando módulo: {module}")
            
            module_results = []
            for country in countries:
                country_results = self.scrape_modulo(module, country)
                module_results.extend(country_results)
            
            all_results[module] = module_results
            
            # Pausa entre módulos
            time.sleep(random.uniform(2, 5))
        
        return all_results
    
    def guardar_en_pinecone(self, results: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Guardar resultados en Pinecone.
        
        Args:
            results: Resultados del scraping
            
        Returns:
            Estadísticas de almacenamiento
        """
        try:
            from utils.pinecone_manager import get_pinecone_manager
            pinecone_manager = get_pinecone_manager()
            
            stats = {
                'total_stored': 0,
                'validated': 0,
                'by_module': {},
                'by_country': {},
                'errors': 0
            }
            
            for module, module_results in results.items():
                module_stats = {'stored': 0, 'validated': 0, 'errors': 0}
                
                for result in module_results:
                    try:
                        # Validar y almacenar
                        validation_result = pinecone_manager.validate_and_store(
                            result['texto'],
                            result['metadata']
                        )
                        
                        if validation_result['stored']:
                            stats['total_stored'] += 1
                            module_stats['stored'] += 1
                            
                            if validation_result['validated']:
                                stats['validated'] += 1
                                module_stats['validated'] += 1
                        
                        # Contar por país
                        country = result['metadata'].get('pais', 'Unknown')
                        stats['by_country'][country] = stats['by_country'].get(country, 0) + 1
                        
                    except Exception as e:
                        logger.error(f"❌ Error guardando en Pinecone: {str(e)}")
                        stats['errors'] += 1
                        module_stats['errors'] += 1
                
                stats['by_module'][module] = module_stats
            
            logger.info(f"✅ Almacenamiento completado - {stats['total_stored']} registros guardados")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error en almacenamiento Pinecone: {str(e)}")
            return {'error': str(e)}

# Función principal para ejecutar el scraper
async def ejecutar_scraper_inteligente():
    """Ejecutar el scraper inteligente completo."""
    logger.info("🚀 Iniciando Scraper Inteligente")
    
    scraper = ScraperInteligente()
    
    # Scrapear todos los módulos
    results = scraper.scrape_todos_modulos()
    
    # Guardar en Pinecone
    stats = scraper.guardar_en_pinecone(results)
    
    # Mostrar estadísticas
    logger.info("📊 Estadísticas finales:")
    logger.info(f"Total almacenado: {stats.get('total_stored', 0)}")
    logger.info(f"Validados: {stats.get('validated', 0)}")
    logger.info(f"Errores: {stats.get('errors', 0)}")
    
    return results, stats

if __name__ == "__main__":
    asyncio.run(ejecutar_scraper_inteligente()) 