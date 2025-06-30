"""
Cliente optimizado para Supabase con funcionalidades avanzadas.
Implementa patrones de desarrollo robusto y manejo de errores.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import asyncio
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    logger.warning("Supabase no está disponible. Instala: pip install supabase-py")
    SUPABASE_AVAILABLE = False
    Client = None

class SupabaseManager:
    """
    Gestor optimizado para Supabase con funcionalidades avanzadas.
    """
    
    def __init__(self):
        """Inicializar el gestor de Supabase."""
        if not SUPABASE_AVAILABLE:
            raise ImportError("Supabase no está disponible. Instala: pip install supabase-py")
        
        self.url = os.getenv('SUPABASE_URL')
        self.key = os.getenv('SUPABASE_KEY')
        
        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL y SUPABASE_KEY deben estar configurados en .env")
        
        try:
            self.client = create_client(self.url, self.key)
            logger.info("✅ Conexión a Supabase establecida")
        except Exception as e:
            logger.error(f"❌ Error conectando a Supabase: {str(e)}")
            raise
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Probar conexión a Supabase.
        
        Returns:
            Estado de la conexión
        """
        try:
            # Intentar una consulta simple
            response = self.client.table('precios_modulos').select('count', count='exact').limit(1).execute()
            
            return {
                "status": "connected",
                "timestamp": datetime.now().isoformat(),
                "table_exists": True,
                "record_count": response.count if hasattr(response, 'count') else "unknown"
            }
        except Exception as e:
            return {
                "status": "error",
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "table_exists": False
            }
    
    def insert_data(self, data: Dict[str, Any]) -> Optional[int]:
        """
        Insertar datos en la tabla precios_modulos.
        
        Args:
            data: Datos a insertar
            
        Returns:
            ID del registro insertado o None si falla
        """
        try:
            # Validar datos requeridos
            required_fields = ['fuente', 'texto_extraido']
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Campo requerido faltante: {field}")
            
            # Agregar timestamp si no existe
            if 'fecha_extraccion' not in data:
                data['fecha_extraccion'] = datetime.now().isoformat()
            
            # Insertar datos
            response = self.client.table('precios_modulos').insert(data).execute()
            
            if response.data:
                record_id = response.data[0].get('id')
                logger.info(f"✅ Datos insertados correctamente (ID: {record_id})")
                return record_id
            else:
                logger.error("❌ No se pudo insertar datos")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error insertando datos: {str(e)}")
            return None
    
    def insert_batch_data(self, data_list: List[Dict[str, Any]]) -> List[int]:
        """
        Insertar múltiples registros en lote.
        
        Args:
            data_list: Lista de datos a insertar
            
        Returns:
            Lista de IDs de registros insertados
        """
        inserted_ids = []
        
        try:
            # Preparar datos para inserción en lote
            for data in data_list:
                if 'fecha_extraccion' not in data:
                    data['fecha_extraccion'] = datetime.now().isoformat()
            
            # Insertar en lote
            response = self.client.table('precios_modulos').insert(data_list).execute()
            
            if response.data:
                for record in response.data:
                    record_id = record.get('id')
                    if record_id:
                        inserted_ids.append(record_id)
                
                logger.info(f"✅ {len(inserted_ids)} registros insertados en lote")
            else:
                logger.error("❌ No se pudieron insertar datos en lote")
                
        except Exception as e:
            logger.error(f"❌ Error insertando datos en lote: {str(e)}")
        
        return inserted_ids
    
    def get_data(self, limit: Optional[int] = None, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Obtener datos de la tabla precios_modulos.
        
        Args:
            limit: Límite de registros
            offset: Desplazamiento
            
        Returns:
            Lista de registros
        """
        try:
            query = self.client.table('precios_modulos').select('*')
            
            if limit:
                query = query.limit(limit)
            
            if offset > 0:
                query = query.range(offset, offset + (limit or 100) - 1)
            
            response = query.execute()
            
            logger.info(f"📊 Obtenidos {len(response.data)} registros")
            return response.data
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo datos: {str(e)}")
            return []
    
    def get_unanalyzed_data(self) -> List[Dict[str, Any]]:
        """
        Obtener datos no analizados por GPT.
        
        Returns:
            Lista de registros sin análisis
        """
        try:
            response = self.client.table('precios_modulos').select('*').eq('analizado_gpt', False).execute()
            
            logger.info(f"📊 Encontrados {len(response.data)} registros sin analizar")
            return response.data
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo datos no analizados: {str(e)}")
            return []
    
    def update_record(self, record_id: int, update_data: Dict[str, Any]) -> bool:
        """
        Actualizar un registro específico.
        
        Args:
            record_id: ID del registro a actualizar
            update_data: Datos a actualizar
            
        Returns:
            True si se actualizó correctamente
        """
        try:
            response = self.client.table('precios_modulos').update(update_data).eq('id', record_id).execute()
            
            if response.data:
                logger.info(f"✅ Registro {record_id} actualizado correctamente")
                return True
            else:
                logger.error(f"❌ No se pudo actualizar registro {record_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error actualizando registro {record_id}: {str(e)}")
            return False
    
    def update_batch_records(self, updates: List[Dict[str, Any]]) -> int:
        """
        Actualizar múltiples registros en lote.
        
        Args:
            updates: Lista de actualizaciones con 'id' y datos a actualizar
            
        Returns:
            Número de registros actualizados
        """
        updated_count = 0
        
        try:
            for update in updates:
                record_id = update.pop('id', None)
                if record_id and self.update_record(record_id, update):
                    updated_count += 1
            
            logger.info(f"✅ {updated_count} registros actualizados en lote")
            
        except Exception as e:
            logger.error(f"❌ Error actualizando registros en lote: {str(e)}")
        
        return updated_count
    
    def delete_record(self, record_id: int) -> bool:
        """
        Eliminar un registro específico.
        
        Args:
            record_id: ID del registro a eliminar
            
        Returns:
            True si se eliminó correctamente
        """
        try:
            response = self.client.table('precios_modulos').delete().eq('id', record_id).execute()
            
            if response.data:
                logger.info(f"✅ Registro {record_id} eliminado correctamente")
                return True
            else:
                logger.error(f"❌ No se pudo eliminar registro {record_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error eliminando registro {record_id}: {str(e)}")
            return False
    
    def search_data(self, search_term: str, fields: List[str] = None) -> List[Dict[str, Any]]:
        """
        Buscar datos por término de búsqueda.
        
        Args:
            search_term: Término de búsqueda
            fields: Campos donde buscar (por defecto: ['fuente', 'texto_extraido'])
            
        Returns:
            Lista de registros que coinciden
        """
        if fields is None:
            fields = ['fuente', 'texto_extraido']
        
        try:
            # Construir consulta de búsqueda
            query = self.client.table('precios_modulos').select('*')
            
            # Buscar en cada campo
            for field in fields:
                query = query.ilike(field, f'%{search_term}%')
            
            response = query.execute()
            
            logger.info(f"🔍 Encontrados {len(response.data)} registros para '{search_term}'")
            return response.data
            
        except Exception as e:
            logger.error(f"❌ Error buscando datos: {str(e)}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Obtener estadísticas de la base de datos.
        
        Returns:
            Estadísticas de la base de datos
        """
        try:
            stats = {
                "timestamp": datetime.now().isoformat(),
                "total_records": 0,
                "analyzed_records": 0,
                "unanalyzed_records": 0,
                "sources": {},
                "analysis_methods": {},
                "recent_activity": []
            }
            
            # Total de registros
            total_response = self.client.table('precios_modulos').select('count', count='exact').execute()
            stats["total_records"] = total_response.count if hasattr(total_response, 'count') else 0
            
            # Registros analizados
            analyzed_response = self.client.table('precios_modulos').select('count', count='exact').eq('analizado_gpt', True).execute()
            stats["analyzed_records"] = analyzed_response.count if hasattr(analyzed_response, 'count') else 0
            
            # Registros no analizados
            stats["unanalyzed_records"] = stats["total_records"] - stats["analyzed_records"]
            
            # Fuentes
            sources_response = self.client.table('precios_modulos').select('fuente').execute()
            for record in sources_response.data:
                source = record.get('fuente', 'unknown')
                stats["sources"][source] = stats["sources"].get(source, 0) + 1
            
            # Métodos de análisis
            methods_response = self.client.table('precios_modulos').select('metodo_analisis').eq('analizado_gpt', True).execute()
            for record in methods_response.data:
                method = record.get('metodo_analisis', 'unknown')
                stats["analysis_methods"][method] = stats["analysis_methods"].get(method, 0) + 1
            
            # Actividad reciente
            recent_response = self.client.table('precios_modulos').select('*').order('fecha_extraccion', desc=True).limit(10).execute()
            stats["recent_activity"] = recent_response.data
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas: {str(e)}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def cleanup_old_data(self, days_old: int = 30) -> int:
        """
        Limpiar datos antiguos.
        
        Args:
            days_old: Días de antigüedad para eliminar
            
        Returns:
            Número de registros eliminados
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            # Obtener registros antiguos
            old_records = self.client.table('precios_modulos').select('id').lt('fecha_extraccion', cutoff_date.isoformat()).execute()
            
            deleted_count = 0
            for record in old_records.data:
                if self.delete_record(record['id']):
                    deleted_count += 1
            
            logger.info(f"🧹 Eliminados {deleted_count} registros antiguos (> {days_old} días)")
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ Error limpiando datos antiguos: {str(e)}")
            return 0
    
    def export_data(self, format: str = 'json', filename: str = None) -> str:
        """
        Exportar datos a archivo.
        
        Args:
            format: Formato de exportación ('json', 'csv')
            filename: Nombre del archivo (opcional)
            
        Returns:
            Ruta del archivo exportado
        """
        try:
            # Obtener todos los datos
            data = self.get_data()
            
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"supabase_export_{timestamp}.{format}"
            
            if format.lower() == 'json':
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            elif format.lower() == 'csv':
                import csv
                if data:
                    with open(filename, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=data[0].keys())
                        writer.writeheader()
                        writer.writerows(data)
            
            logger.info(f"📁 Datos exportados a {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"❌ Error exportando datos: {str(e)}")
            return ""
    
    def backup_table(self) -> str:
        """
        Crear backup de la tabla.
        
        Returns:
            Ruta del archivo de backup
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"backup_precios_modulos_{timestamp}.json"
        
        return self.export_data('json', backup_filename)
    
    def restore_from_backup(self, backup_file: str) -> bool:
        """
        Restaurar datos desde backup.
        
        Args:
            backup_file: Ruta del archivo de backup
            
        Returns:
            True si se restauró correctamente
        """
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # Insertar datos del backup
            inserted_ids = self.insert_batch_data(backup_data)
            
            logger.info(f"🔄 Restaurados {len(inserted_ids)} registros desde backup")
            return len(inserted_ids) > 0
            
        except Exception as e:
            logger.error(f"❌ Error restaurando desde backup: {str(e)}")
            return False 