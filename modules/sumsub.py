"""
Scraper específico para Sumsub.
Extrae información sobre soluciones de KYC/KYB y verificación de identidad.
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
import time
import sys
import os

# Agregar el directorio padre al path para importar utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.extract_price import extract_price_from_text, extract_white_label_info, clean_text

class SumsubScraper:
    """Scraper para extraer información de Sumsub."""
    
    def __init__(self):
        """Inicializar el scraper con headers para evitar bloqueos."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # URLs específicas de Sumsub para KYC/KYB y white label
        self.urls = [
            'https://sumsub.com/pricing/',
            'https://sumsub.com/white-label/',
            'https://sumsub.com/solutions/',
            'https://sumsub.com/kyc-kyb/',
            'https://sumsub.com/api/',
            'https://sumsub.com/enterprise/'
        ]
    
    def scrape_page(self, url: str) -> Optional[str]:
        """
        Scrapear una página específica de Sumsub.
        
        Args:
            url: URL de la página a scrapear
            
        Returns:
            Texto extraído de la página, o None si hay error
        """
        try:
            print(f"🔍 Scrapeando: {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraer texto de diferentes secciones
            text_content = []
            
            # Extraer de elementos principales
            main_selectors = [
                'main',
                '.main-content',
                '.content',
                '.page-content',
                'article',
                '.post-content',
                '.hero-section',
                '.pricing-section',
                '.features-section'
            ]
            
            for selector in main_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text_content.append(element.get_text())
            
            # Si no se encontró contenido principal, extraer de todo el body
            if not text_content:
                body = soup.find('body')
                if body:
                    text_content.append(body.get_text())
            
            # Unir todo el texto
            full_text = ' '.join(text_content)
            
            # Limpiar el texto
            cleaned_text = clean_text(full_text)
            
            print(f"✅ Extraídos {len(cleaned_text)} caracteres de {url}")
            return cleaned_text
            
        except requests.RequestException as e:
            print(f"❌ Error de red al scrapear {url}: {str(e)}")
            return None
        except Exception as e:
            print(f"❌ Error inesperado al scrapear {url}: {str(e)}")
            return None
    
    def extract_relevant_info(self, text: str) -> List[Dict[str, Any]]:
        """
        Extraer información relevante del texto scrapeado, filtrando solo LATAM/México.
        """
        results = []
        
        # Lista de países LATAM
        latam_countries = [
            "México", "Mexico", "Argentina", "Colombia", "Chile", "Perú", "Uruguay", "Paraguay", "Bolivia", "Ecuador", "Venezuela", "Guatemala", "Honduras", "El Salvador", "Nicaragua", "Costa Rica", "Panamá", "Cuba", "República Dominicana", "Puerto Rico"
        ]
        
        def get_country(texto):
            for country in latam_countries:
                if country.lower() in texto.lower():
                    return country
            return None
        
        # Extraer información de white label y KYC
        white_label_info = extract_white_label_info(text)
        
        for module, relevant_text in white_label_info:
            country = get_country(relevant_text)
            if not country:
                continue  # Saltar si no es LATAM/México
            price = extract_price_from_text(relevant_text)
            result = {
                'fuente': 'Sumsub',
                'modulo': module,
                'texto_extraido': relevant_text[:500] + '...' if len(relevant_text) > 500 else relevant_text,
                'precio_estimado': price if price else 'No especificado',
                'pais': country,
                'region': 'LATAM' if country != 'México' and country != 'Mexico' else 'México'
            }
            results.append(result)
        
        # Buscar específicamente información de KYC/KYB si no se encontró
        if not results:
            kyc_keywords = ['kyc', 'kyb', 'verification', 'identity', 'compliance']
            text_lower = text.lower()
            for keyword in kyc_keywords:
                if keyword in text_lower:
                    paragraphs = text.split('\n\n')
                    for paragraph in paragraphs:
                        country = get_country(paragraph)
                        if not country:
                            continue
                        if keyword in paragraph.lower():
                            price = extract_price_from_text(paragraph)
                            result = {
                                'fuente': 'Sumsub',
                                'modulo': 'KYC/KYB',
                                'texto_extraido': paragraph[:500] + '...' if len(paragraph) > 500 else paragraph,
                                'precio_estimado': price if price else 'No especificado',
                                'pais': country,
                                'region': 'LATAM' if country != 'México' and country != 'Mexico' else 'México'
                            }
                            results.append(result)
                            break
                    break
        # Si no se encontró información específica, buscar precios generales SOLO si hay país LATAM
        if not results:
            price = extract_price_from_text(text)
            country = get_country(text)
            if price and country:
                result = {
                    'fuente': 'Sumsub',
                    'modulo': 'General Service',
                    'texto_extraido': text[:500] + '...' if len(text) > 500 else text,
                    'precio_estimado': price,
                    'pais': country,
                    'region': 'LATAM' if country != 'México' and country != 'Mexico' else 'México'
                }
                results.append(result)
        return results
    
    def scrape_all(self) -> List[Dict[str, Any]]:
        """
        Scrapear todas las URLs de Sumsub y extraer información relevante.
        
        Returns:
            Lista de diccionarios con toda la información extraída
        """
        all_results = []
        
        for url in self.urls:
            # Pausa entre requests para ser respetuoso
            time.sleep(2)
            
            text = self.scrape_page(url)
            if text:
                results = self.extract_relevant_info(text)
                all_results.extend(results)
        
        print(f"📊 Total de resultados extraídos de Sumsub: {len(all_results)}")
        return all_results
    
    def get_sample_data(self) -> List[Dict[str, Any]]:
        """
        Obtener datos de muestra para testing cuando no se puede acceder a las URLs.
        
        Returns:
            Lista de diccionarios con datos de muestra
        """
        return [
            {
                'fuente': 'Sumsub',
                'modulo': 'KYC/KYB',
                'texto_extraido': 'Sumsub provides comprehensive KYC and KYB verification services with AI-powered identity verification, document analysis, and compliance monitoring. Our white-label solution integrates seamlessly with your platform.',
                'precio_estimado': '$0.50'
            },
            {
                'fuente': 'Sumsub',
                'modulo': 'White Label Solution',
                'texto_extraido': 'Customizable white-label KYC solution with your branding, custom workflows, and dedicated support. Includes API integration, compliance reporting, and fraud detection.',
                'precio_estimado': '$2,000'
            },
            {
                'fuente': 'Sumsub',
                'modulo': 'Compliance',
                'texto_extraido': 'Regulatory compliance solution with automated reporting, audit trails, and multi-jurisdiction support. Meets GDPR, AML, and local regulatory requirements.',
                'precio_estimado': '$1,500'
            },
            {
                'fuente': 'Sumsub',
                'modulo': 'API Integration',
                'texto_extraido': 'RESTful API with comprehensive documentation, SDKs for multiple languages, and 99.9% uptime SLA. Includes webhook support and real-time verification.',
                'precio_estimado': '$500'
            }
        ] 