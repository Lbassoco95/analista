"""
Gestor de chat con GPT integrado con Pinecone para consultas inteligentes sobre proveedores LATAM.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio

import openai
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate

logger = logging.getLogger(__name__)

class ChatGPTManager:
    """
    Gestor para chat con GPT usando datos de Pinecone.
    """
    
    def __init__(self, api_key: str = None, model: str = "gpt-4"):
        """
        Inicializar gestor de chat GPT.
        
        Args:
            api_key: API key de OpenAI
            model: Modelo a usar
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY no configurada")
        
        # Configurar OpenAI
        openai.api_key = self.api_key
        
        # Inicializar LangChain
        self.llm = ChatOpenAI(
            openai_api_key=self.api_key,
            model_name=self.model,
            temperature=0.3
        )
        
        logger.info(f"✅ ChatGPTManager inicializado - Modelo: {self.model}")
    
    def create_system_prompt(self) -> str:
        """
        Crear prompt del sistema para análisis de proveedores LATAM.
        
        Returns:
            Prompt del sistema
        """
        return """Eres un experto analista de proveedores de servicios financieros y crypto para Latinoamérica y México. 

Tu función es:
1. Analizar información sobre precios, servicios y condiciones de proveedores
2. Proporcionar insights relevantes para el mercado LATAM
3. Comparar opciones y hacer recomendaciones
4. Identificar tendencias y oportunidades

Información disponible:
- Proveedores: B2Broker, Wallester, Sumsub, y otros
- Módulos: White Label Wallet, KYC/KYB, Crypto Trading, Payment Gateway, Digital Signature, Custody, Cross Border
- Países: México, Argentina, Colombia, Chile, Perú, Uruguay, Paraguay, Bolivia, Ecuador, Venezuela, Guatemala, Honduras, El Salvador, Nicaragua, Costa Rica, Panamá, Cuba, República Dominicana, Puerto Rico

Responde siempre en español y proporciona información específica y accionable."""
    
    def create_analysis_prompt(self, query: str, context_data: List[Dict[str, Any]]) -> str:
        """
        Crear prompt para análisis específico.
        
        Args:
            query: Consulta del usuario
            context_data: Datos de contexto de Pinecone
            
        Returns:
            Prompt formateado
        """
        # Formatear datos de contexto
        context_text = ""
        for i, data in enumerate(context_data[:5]):  # Usar solo los 5 más relevantes
            metadata = data.get('metadata', {})
            context_text += f"\n--- Fuente {i+1} ---\n"
            context_text += f"Proveedor: {metadata.get('proveedor', 'N/A')}\n"
            context_text += f"País: {metadata.get('pais', 'N/A')}\n"
            context_text += f"Módulo: {metadata.get('modulo', 'N/A')}\n"
            context_text += f"Precio: {metadata.get('precio', 'N/A')}\n"
            context_text += f"Moneda: {metadata.get('moneda', 'N/A')}\n"
            context_text += f"Confianza: {metadata.get('confianza', 0)}%\n"
            context_text += f"Texto: {metadata.get('texto', 'N/A')[:300]}...\n"
        
        prompt = f"""
Consulta del usuario: {query}

Datos disponibles de proveedores LATAM:
{context_text}

Por favor analiza esta información y proporciona:
1. Resumen de precios y servicios encontrados
2. Comparación entre proveedores (si aplica)
3. Recomendaciones específicas para el mercado LATAM
4. Consideraciones importantes sobre confianza de datos
5. Oportunidades o tendencias identificadas

Responde de manera estructurada y profesional en español.
"""
        return prompt
    
    async def chat_with_context(self, 
                               query: str, 
                               pinecone_manager, 
                               filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Chat con GPT usando contexto de Pinecone.
        
        Args:
            query: Consulta del usuario
            pinecone_manager: Instancia del gestor de Pinecone
            filters: Filtros para la búsqueda (ej: {'pais': 'México'})
            
        Returns:
            Respuesta estructurada de GPT
        """
        try:
            # Buscar datos relevantes en Pinecone
            context_data = pinecone_manager.search_similar(query, filters, top_k=10)
            
            if not context_data:
                return {
                    'success': False,
                    'message': 'No se encontraron datos relevantes para tu consulta.',
                    'suggestions': [
                        'Intenta con términos más generales',
                        'Especifica un país o módulo',
                        'Verifica que los datos estén disponibles'
                    ]
                }
            
            # Crear prompt
            system_prompt = self.create_system_prompt()
            analysis_prompt = self.create_analysis_prompt(query, context_data)
            
            # Generar respuesta con GPT
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=analysis_prompt)
            ]
            
            response = await self.llm.agenerate([messages])
            
            # Extraer respuesta
            gpt_response = response.generations[0][0].text
            
            # Estructurar respuesta
            result = {
                'success': True,
                'query': query,
                'response': gpt_response,
                'context_sources': len(context_data),
                'filters_applied': filters,
                'timestamp': datetime.now().isoformat(),
                'model_used': self.model
            }
            
            # Agregar estadísticas de contexto
            if context_data:
                countries = set()
                providers = set()
                modules = set()
                
                for data in context_data:
                    metadata = data.get('metadata', {})
                    if metadata.get('pais'):
                        countries.add(metadata['pais'])
                    if metadata.get('proveedor'):
                        providers.add(metadata['proveedor'])
                    if metadata.get('modulo'):
                        modules.add(metadata['modulo'])
                
                result['context_stats'] = {
                    'countries_found': list(countries),
                    'providers_found': list(providers),
                    'modules_found': list(modules),
                    'avg_confidence': sum(data.get('metadata', {}).get('confianza', 0) for data in context_data) / len(context_data)
                }
            
            logger.info(f"✅ Chat completado - Fuentes: {len(context_data)}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error en chat con GPT: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Error procesando tu consulta.'
            }
    
    async def analyze_provider_comparison(self, 
                                        providers: List[str], 
                                        module: str, 
                                        country: str = None,
                                        pinecone_manager = None) -> Dict[str, Any]:
        """
        Analizar comparación entre proveedores específicos.
        
        Args:
            providers: Lista de proveedores a comparar
            module: Módulo a analizar
            country: País específico (opcional)
            pinecone_manager: Gestor de Pinecone
            
        Returns:
            Análisis comparativo
        """
        try:
            if not pinecone_manager:
                from .pinecone_manager import get_pinecone_manager
                pinecone_manager = get_pinecone_manager()
            
            # Buscar datos de cada proveedor
            all_data = []
            for provider in providers:
                filters = {'proveedor': provider, 'modulo': module}
                if country:
                    filters['pais'] = country
                
                provider_data = pinecone_manager.search_similar(
                    f"{module} pricing {provider}", 
                    filters, 
                    top_k=5
                )
                all_data.extend(provider_data)
            
            if not all_data:
                return {
                    'success': False,
                    'message': f'No se encontraron datos para comparar {", ".join(providers)} en {module}'
                }
            
            # Crear prompt de comparación
            comparison_prompt = f"""
Compara los siguientes proveedores para el módulo {module}:
{', '.join(providers)}

Datos disponibles:
"""
            
            for data in all_data:
                metadata = data.get('metadata', {})
                comparison_prompt += f"""
- {metadata.get('proveedor', 'N/A')}: {metadata.get('precio', 'N/A')} ({metadata.get('moneda', 'N/A')}) - Confianza: {metadata.get('confianza', 0)}%
"""
            
            comparison_prompt += f"""

Proporciona un análisis comparativo que incluya:
1. Comparación de precios y costos
2. Ventajas y desventajas de cada proveedor
3. Recomendación para el mercado LATAM
4. Consideraciones de implementación
5. Factores de riesgo y confianza

Responde en español de manera estructurada.
"""
            
            # Generar respuesta
            messages = [
                SystemMessage(content=self.create_system_prompt()),
                HumanMessage(content=comparison_prompt)
            ]
            
            response = await self.llm.agenerate([messages])
            gpt_response = response.generations[0][0].text
            
            return {
                'success': True,
                'providers': providers,
                'module': module,
                'country': country,
                'comparison': gpt_response,
                'data_sources': len(all_data),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error en comparación de proveedores: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Error realizando comparación.'
            }
    
    async def get_market_insights(self, 
                                country: str = None, 
                                module: str = None,
                                pinecone_manager = None) -> Dict[str, Any]:
        """
        Obtener insights del mercado basado en datos disponibles.
        
        Args:
            country: País específico (opcional)
            module: Módulo específico (opcional)
            pinecone_manager: Gestor de Pinecone
            
        Returns:
            Insights del mercado
        """
        try:
            if not pinecone_manager:
                from .pinecone_manager import get_pinecone_manager
                pinecone_manager = get_pinecone_manager()
            
            # Obtener estadísticas
            stats = pinecone_manager.get_statistics()
            
            # Buscar datos relevantes
            query = "market trends pricing analysis"
            filters = {}
            if country:
                filters['pais'] = country
            if module:
                filters['modulo'] = module
            
            context_data = pinecone_manager.search_similar(query, filters, top_k=15)
            
            # Crear prompt de insights
            insights_prompt = f"""
Analiza los siguientes datos del mercado de servicios financieros y crypto:

Estadísticas generales:
- Total de datos: {stats.get('total_vectors', 0)}
- Distribución por país: {stats.get('country_distribution', {})}
- Distribución por módulo: {stats.get('module_distribution', {})}

Datos específicos:
"""
            
            for i, data in enumerate(context_data[:10]):
                metadata = data.get('metadata', {})
                insights_prompt += f"""
{i+1}. {metadata.get('proveedor', 'N/A')} - {metadata.get('modulo', 'N/A')} - {metadata.get('pais', 'N/A')} - {metadata.get('precio', 'N/A')}
"""
            
            insights_prompt += f"""

Proporciona insights sobre:
1. Tendencias de precios en el mercado
2. Proveedores más activos por región
3. Módulos con mayor demanda
4. Oportunidades de mercado
5. Recomendaciones estratégicas para LATAM

Responde en español de manera profesional y estructurada.
"""
            
            # Generar respuesta
            messages = [
                SystemMessage(content=self.create_system_prompt()),
                HumanMessage(content=insights_prompt)
            ]
            
            response = await self.llm.agenerate([messages])
            gpt_response = response.generations[0][0].text
            
            return {
                'success': True,
                'country': country,
                'module': module,
                'insights': gpt_response,
                'statistics': stats,
                'data_sources': len(context_data),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo insights: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Error obteniendo insights del mercado.'
            }

# Función de utilidad
def get_chat_gpt_manager() -> ChatGPTManager:
    """Obtener instancia del gestor de chat GPT."""
    return ChatGPTManager() 