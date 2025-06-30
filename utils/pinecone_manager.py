"""
Gestor de Pinecone para almacenamiento y búsqueda de embeddings con metadata.
Integrado con análisis de LATAM/México y validación cruzada.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import asyncio

import pinecone
from sentence_transformers import SentenceTransformer
import numpy as np

logger = logging.getLogger(__name__)

class PineconeManager:
    """
    Gestor para operaciones con Pinecone incluyendo embeddings y metadata.
    """
    
    def __init__(self, api_key: str = None, environment: str = None, index_name: str = None):
        """
        Inicializar gestor de Pinecone.
        
        Args:
            api_key: API key de Pinecone
            environment: Environment de Pinecone
            index_name: Nombre del índice
        """
        self.api_key = api_key or os.getenv('PINECONE_API_KEY')
        self.environment = environment or os.getenv('PINECONE_ENVIRONMENT', 'us-west1-gcp')
        self.index_name = index_name or os.getenv('PINECONE_INDEX', 'proveedores-latam')
        
        if not self.api_key:
            raise ValueError("PINECONE_API_KEY no configurada")
        
        # Inicializar Pinecone
        pinecone.init(api_key=self.api_key, environment=self.environment)
        
        # Cargar modelo de embeddings
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        # Verificar/conectar al índice
        self._ensure_index_exists()
        
        logger.info(f"✅ PineconeManager inicializado - Índice: {self.index_name}")
    
    def _ensure_index_exists(self):
        """Asegurar que el índice existe, crearlo si no."""
        try:
            if self.index_name not in pinecone.list_indexes():
                # Crear índice con configuración optimizada
                pinecone.create_index(
                    name=self.index_name,
                    dimension=384,  # Dimension del modelo all-MiniLM-L6-v2
                    metric='cosine',
                    metadata_config={
                        'indexed': ['proveedor', 'pais', 'region', 'modulo', 'moneda', 'fecha']
                    }
                )
                logger.info(f"✅ Índice {self.index_name} creado")
            else:
                logger.info(f"✅ Índice {self.index_name} ya existe")
        except Exception as e:
            logger.error(f"❌ Error creando/conectando al índice: {str(e)}")
            raise
    
    def get_index(self):
        """Obtener conexión al índice."""
        return pinecone.Index(self.index_name)
    
    def create_embedding(self, text: str) -> List[float]:
        """
        Crear embedding para un texto.
        
        Args:
            text: Texto a convertir en embedding
            
        Returns:
            Lista de floats (embedding)
        """
        try:
            # Limpiar y truncar texto si es muy largo
            if len(text) > 1000:
                text = text[:1000]
            
            embedding = self.embedding_model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"❌ Error creando embedding: {str(e)}")
            return []
    
    def store_data(self, 
                   text: str, 
                   metadata: Dict[str, Any], 
                   vector_id: str = None) -> bool:
        """
        Almacenar texto con su embedding y metadata en Pinecone.
        
        Args:
            text: Texto a almacenar
            metadata: Metadata asociada
            vector_id: ID único del vector (opcional)
            
        Returns:
            True si se almacenó correctamente
        """
        try:
            # Crear embedding
            embedding = self.create_embedding(text)
            if not embedding:
                return False
            
            # Generar ID si no se proporciona
            if not vector_id:
                vector_id = f"{metadata.get('proveedor', 'unknown')}_{metadata.get('pais', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Preparar metadata
            pinecone_metadata = {
                'texto': text[:1000],  # Truncar texto largo
                'proveedor': metadata.get('proveedor', ''),
                'pais': metadata.get('pais', ''),
                'region': metadata.get('region', ''),
                'modulo': metadata.get('modulo', ''),
                'moneda': metadata.get('moneda', ''),
                'precio': metadata.get('precio_estimado', ''),
                'fecha': metadata.get('fecha_publicacion', ''),
                'confianza': metadata.get('confianza', 0.0),
                'fuente_url': metadata.get('url', ''),
                'tipo_fuente': metadata.get('tipo_fuente', 'web'),
                'validado_cruzado': metadata.get('validado_cruzado', False),
                'timestamp': datetime.now().isoformat()
            }
            
            # Insertar en Pinecone
            index = self.get_index()
            index.upsert(
                vectors=[(vector_id, embedding, pinecone_metadata)]
            )
            
            logger.info(f"✅ Datos almacenados en Pinecone - ID: {vector_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error almacenando en Pinecone: {str(e)}")
            return False
    
    def search_similar(self, 
                      query: str, 
                      filters: Dict[str, Any] = None, 
                      top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Buscar textos similares en Pinecone.
        
        Args:
            query: Texto de consulta
            filters: Filtros de metadata (ej: {'pais': 'México'})
            top_k: Número máximo de resultados
            
        Returns:
            Lista de resultados con metadata
        """
        try:
            # Crear embedding de la consulta
            query_embedding = self.create_embedding(query)
            if not query_embedding:
                return []
            
            # Preparar filtros para Pinecone
            pinecone_filters = {}
            if filters:
                for key, value in filters.items():
                    if value:
                        pinecone_filters[key] = value
            
            # Buscar en Pinecone
            index = self.get_index()
            results = index.query(
                vector=query_embedding,
                filter=pinecone_filters,
                top_k=top_k,
                include_metadata=True
            )
            
            # Formatear resultados
            formatted_results = []
            for match in results.matches:
                result = {
                    'id': match.id,
                    'score': match.score,
                    'metadata': match.metadata
                }
                formatted_results.append(result)
            
            logger.info(f"✅ Búsqueda completada - {len(formatted_results)} resultados")
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Error en búsqueda Pinecone: {str(e)}")
            return []
    
    def search_by_module(self, 
                        module: str, 
                        country: str = None, 
                        top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Buscar por módulo específico y opcionalmente por país.
        
        Args:
            module: Módulo a buscar (ej: 'KYC/KYB', 'White Label Wallet')
            country: País específico (opcional)
            top_k: Número máximo de resultados
            
        Returns:
            Lista de resultados
        """
        filters = {'modulo': module}
        if country:
            filters['pais'] = country
        
        # Usar una consulta genérica del módulo
        query = f"pricing information for {module} services"
        
        return self.search_similar(query, filters, top_k)
    
    def search_by_country(self, 
                         country: str, 
                         top_k: int = 20) -> List[Dict[str, Any]]:
        """
        Buscar todos los datos de un país específico.
        
        Args:
            country: País a buscar
            top_k: Número máximo de resultados
            
        Returns:
            Lista de resultados
        """
        filters = {'pais': country}
        query = f"crypto services pricing in {country}"
        
        return self.search_similar(query, filters, top_k)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Obtener estadísticas del índice Pinecone.
        
        Returns:
            Diccionario con estadísticas
        """
        try:
            index = self.get_index()
            stats = index.describe_index_stats()
            
            # Contar por país
            country_counts = {}
            module_counts = {}
            
            # Obtener todos los vectores para análisis
            all_vectors = index.query(
                vector=[0] * 384,  # Vector dummy
                top_k=10000,
                include_metadata=True
            )
            
            for match in all_vectors.matches:
                metadata = match.metadata
                
                # Contar países
                country = metadata.get('pais', 'Unknown')
                country_counts[country] = country_counts.get(country, 0) + 1
                
                # Contar módulos
                module = metadata.get('modulo', 'Unknown')
                module_counts[module] = module_counts.get(module, 0) + 1
            
            return {
                'total_vectors': stats.total_vector_count,
                'dimension': stats.dimension,
                'index_name': self.index_name,
                'country_distribution': country_counts,
                'module_distribution': module_counts,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas: {str(e)}")
            return {}
    
    def delete_old_data(self, days_old: int = 30) -> int:
        """
        Eliminar datos antiguos del índice.
        
        Args:
            days_old: Días de antigüedad para eliminar
            
        Returns:
            Número de vectores eliminados
        """
        try:
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            # Buscar vectores antiguos
            index = self.get_index()
            old_vectors = index.query(
                vector=[0] * 384,
                top_k=10000,
                include_metadata=True
            )
            
            vectors_to_delete = []
            for match in old_vectors.matches:
                metadata = match.metadata
                timestamp_str = metadata.get('timestamp', '')
                
                if timestamp_str:
                    try:
                        vector_date = datetime.fromisoformat(timestamp_str)
                        if vector_date < cutoff_date:
                            vectors_to_delete.append(match.id)
                    except:
                        continue
            
            # Eliminar vectores antiguos
            if vectors_to_delete:
                index.delete(ids=vectors_to_delete)
                logger.info(f"✅ Eliminados {len(vectors_to_delete)} vectores antiguos")
                return len(vectors_to_delete)
            
            return 0
            
        except Exception as e:
            logger.error(f"❌ Error eliminando datos antiguos: {str(e)}")
            return 0
    
    def validate_and_store(self, 
                          text: str, 
                          metadata: Dict[str, Any], 
                          existing_data: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Validar datos antes de almacenar usando información existente.
        
        Args:
            text: Texto a validar y almacenar
            metadata: Metadata asociada
            existing_data: Datos existentes para validación cruzada
            
        Returns:
            Resultado de la validación y almacenamiento
        """
        result = {
            'stored': False,
            'validated': False,
            'confidence': 0.0,
            'cross_reference': None,
            'vector_id': None
        }
        
        try:
            # Buscar datos similares existentes
            similar_results = self.search_similar(text, top_k=5)
            
            # Validar con datos existentes si hay
            if similar_results:
                best_match = similar_results[0]
                
                # Importar función de validación
                from utils.extract_price import validate_cross_reference
                
                validation = validate_cross_reference(
                    text, 
                    best_match['metadata'].get('texto', ''), 
                    metadata.get('modulo', '')
                )
                
                result['cross_reference'] = validation
                result['confidence'] = validation['confidence']
                
                # Si la confianza es alta, marcar como validado
                if validation['confidence'] > 70:
                    result['validated'] = True
                    metadata['validado_cruzado'] = True
                    metadata['confianza'] = max(metadata.get('confianza', 0), validation['confidence'])
            
            # Almacenar datos
            vector_id = f"{metadata.get('proveedor', 'unknown')}_{metadata.get('pais', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            if self.store_data(text, metadata, vector_id):
                result['stored'] = True
                result['vector_id'] = vector_id
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error en validación y almacenamiento: {str(e)}")
            return result

# Función de utilidad para uso directo
def get_pinecone_manager() -> PineconeManager:
    """Obtener instancia del gestor de Pinecone."""
    return PineconeManager() 