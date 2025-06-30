"""
Analizador optimizado principal que integra Hugging Face Transformers, Safetensors y GPT.
Implementa principios de desarrollo robusto basados en las mejores prácticas.
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import sys

# Agregar el directorio actual al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase_client import SupabaseManager
from utils.optimized_analyzer import OptimizedAnalyzer
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OptimizedGPTAnalyzer:
    """
    Analizador GPT optimizado que combina modelos locales de Hugging Face
    con análisis GPT para máxima eficiencia y precisión.
    """
    
    def __init__(self, use_local_models: bool = True, use_gpt: bool = True):
        """
        Inicializar el analizador optimizado.
        
        Args:
            use_local_models: Si usar modelos locales de Hugging Face
            use_gpt: Si usar análisis GPT como respaldo
        """
        self.supabase_manager = SupabaseManager()
        self.optimized_analyzer = OptimizedAnalyzer(use_local_models, use_gpt)
        
        logger.info("Optimized GPT Analyzer initialized successfully")
    
    async def analyze_all_data_optimized(self, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Analizar todos los datos usando estrategia optimizada.
        
        Args:
            limit: Límite de registros a procesar
            
        Returns:
            Estadísticas del análisis
        """
        logger.info("🚀 Iniciando análisis optimizado de todos los datos...")
        
        # Obtener datos no analizados
        unanalyzed_data = self.get_unanalyzed_data()
        
        if limit:
            unanalyzed_data = unanalyzed_data[:limit]
        
        if not unanalyzed_data:
            logger.info("✅ No hay datos para analizar")
            return {"procesados": 0, "exitosos": 0, "fallidos": 0}
        
        stats = {
            "procesados": len(unanalyzed_data),
            "exitosos": 0,
            "fallidos": 0,
            "analysis_methods": {},
            "performance_metrics": {}
        }
        
        # Preparar datos para análisis en lote
        texts_for_analysis = []
        for record in unanalyzed_data:
            texts_for_analysis.append({
                'text': record['texto_extraido'],
                'source': record['fuente'],
                'record_id': record['id']
            })
        
        # Análisis en lote optimizado
        start_time = datetime.now()
        analysis_results = await self.optimized_analyzer.analyze_batch_optimized(texts_for_analysis)
        end_time = datetime.now()
        
        # Procesar resultados y actualizar Supabase
        for i, (text_data, analysis_result) in enumerate(zip(texts_for_analysis, analysis_results)):
            try:
                # Actualizar registro en Supabase
                if self.update_record_with_analysis(text_data['record_id'], analysis_result):
                    stats["exitosos"] += 1
                    
                    # Contar métodos de análisis utilizados
                    method = analysis_result.get("analysis_method", "unknown")
                    stats["analysis_methods"][method] = stats["analysis_methods"].get(method, 0) + 1
                else:
                    stats["fallidos"] += 1
                
                logger.info(f"✅ Procesado registro {i+1}/{len(unanalyzed_data)} (ID: {text_data['record_id']})")
                
            except Exception as e:
                logger.error(f"❌ Error procesando registro {text_data['record_id']}: {str(e)}")
                stats["fallidos"] += 1
        
        # Calcular métricas de rendimiento
        processing_time = (end_time - start_time).total_seconds()
        stats["performance_metrics"] = {
            "total_time_seconds": processing_time,
            "average_time_per_record": processing_time / len(unanalyzed_data) if unanalyzed_data else 0,
            "records_per_second": len(unanalyzed_data) / processing_time if processing_time > 0 else 0
        }
        
        logger.info(f"\n📊 Análisis optimizado completado:")
        logger.info(f"   - Procesados: {stats['procesados']}")
        logger.info(f"   - Exitosos: {stats['exitosos']}")
        logger.info(f"   - Fallidos: {stats['fallidos']}")
        logger.info(f"   - Tiempo total: {processing_time:.2f} segundos")
        logger.info(f"   - Métodos utilizados: {stats['analysis_methods']}")
        
        return stats
    
    def get_unanalyzed_data(self) -> List[Dict[str, Any]]:
        """
        Obtener datos no analizados de Supabase.
        
        Returns:
            Lista de registros sin análisis
        """
        try:
            # Buscar registros que no tengan análisis
            response = self.supabase_manager.client.table('precios_modulos').select('*').execute()
            
            # Filtrar registros que no tengan análisis GPT
            unanalyzed = []
            for record in response.data:
                # Verificar si ya fue analizado
                if not record.get('analizado_gpt', False):
                    unanalyzed.append(record)
            
            logger.info(f"📊 Encontrados {len(unanalyzed)} registros para analizar")
            return unanalyzed
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo datos de Supabase: {str(e)}")
            return []
    
    def update_record_with_analysis(self, record_id: int, analysis: Dict[str, Any]) -> bool:
        """
        Actualizar registro en Supabase con el análisis optimizado.
        
        Args:
            record_id: ID del registro a actualizar
            analysis: Análisis optimizado
            
        Returns:
            True si se actualizó correctamente
        """
        try:
            update_data = {
                'precio_gpt': analysis.get('precio_estimado'),
                'clasificacion_gpt': analysis.get('clasificacion_modulo'),
                'condiciones_comerciales': json.dumps(analysis.get('condiciones_comerciales', {})),
                'confianza_analisis': analysis.get('confianza_analisis'),
                'fecha_analisis_gpt': datetime.now().isoformat(),
                'analizado_gpt': True,
                'metodo_analisis': analysis.get('analysis_method', 'unknown')
            }
            
            response = self.supabase_manager.client.table('precios_modulos').update(update_data).eq('id', record_id).execute()
            
            logger.debug(f"✅ Registro {record_id} actualizado con análisis optimizado")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error actualizando registro {record_id}: {str(e)}")
            return False
    
    async def test_analysis_pipeline(self) -> Dict[str, Any]:
        """
        Probar el pipeline de análisis con datos de ejemplo.
        
        Returns:
            Resultados de la prueba
        """
        logger.info("🧪 Probando pipeline de análisis optimizado...")
        
        test_texts = [
            {
                'text': 'B2Broker offers comprehensive white label solutions for crypto exchanges. Setup fee starts at $50,000 with monthly maintenance costs of $5,000.',
                'source': 'B2Broker Test'
            },
            {
                'text': 'Sumsub provides KYC verification services with AI-powered identity verification. Pricing starts at $0.50 per verification.',
                'source': 'Sumsub Test'
            },
            {
                'text': 'Wallester offers secure digital wallet solution with advanced encryption. Monthly subscription costs $2,500.',
                'source': 'Wallester Test'
            }
        ]
        
        try:
            # Análisis en lote
            results = await self.optimized_analyzer.analyze_batch_optimized(test_texts)
            
            # Mostrar resultados
            logger.info("📋 Resultados de la prueba:")
            for i, (test_data, result) in enumerate(zip(test_texts, results)):
                logger.info(f"  Test {i+1} ({test_data['source']}):")
                logger.info(f"    - Método: {result.get('analysis_method', 'unknown')}")
                logger.info(f"    - Clasificación: {result.get('clasificacion_modulo', 'N/A')}")
                logger.info(f"    - Precio: {result.get('precio_estimado', 'N/A')}")
                logger.info(f"    - Confianza: {result.get('confianza_analisis', 'N/A')}")
            
            return {
                "success": True,
                "results": results,
                "stats": self.optimized_analyzer.get_analysis_stats()
            }
            
        except Exception as e:
            logger.error(f"❌ Error en prueba de pipeline: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """
        Obtener estadísticas completas del sistema.
        
        Returns:
            Estadísticas del sistema
        """
        stats = {
            "timestamp": datetime.now().isoformat(),
            "analyzer_stats": self.optimized_analyzer.get_analysis_stats(),
            "supabase_connection": self.supabase_manager.test_connection(),
            "system_info": {
                "python_version": sys.version,
                "platform": sys.platform,
                "cpu_count": os.cpu_count()
            }
        }
        
        return stats
    
    def optimize_system(self):
        """Optimizar el sistema de análisis."""
        logger.info("🔧 Optimizando sistema de análisis...")
        
        # Optimizar cache
        self.optimized_analyzer.optimize_cache()
        
        # Limpiar memoria si es necesario
        import gc
        gc.collect()
        
        logger.info("✅ Sistema optimizado")

async def main():
    """Función principal del analizador optimizado."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analizador GPT Optimizado con Hugging Face')
    parser.add_argument('--limit', type=int, help='Límite de registros a procesar')
    parser.add_argument('--test', action='store_true', help='Ejecutar prueba del pipeline')
    parser.add_argument('--local-only', action='store_true', help='Usar solo modelos locales')
    parser.add_argument('--gpt-only', action='store_true', help='Usar solo GPT')
    parser.add_argument('--stats', action='store_true', help='Mostrar estadísticas del sistema')
    
    args = parser.parse_args()
    
    logger.info("🧠 Analizador GPT Optimizado con Hugging Face")
    logger.info("=" * 60)
    
    try:
        # Configurar modo de análisis
        use_local = not args.gpt_only
        use_gpt = not args.local_only
        
        analyzer = OptimizedGPTAnalyzer(use_local_models=use_local, use_gpt=use_gpt)
        
        if args.test:
            # Prueba del pipeline
            result = await analyzer.test_analysis_pipeline()
            if result["success"]:
                logger.info("✅ Prueba del pipeline exitosa")
            else:
                logger.error(f"❌ Prueba del pipeline fallida: {result.get('error')}")
        
        elif args.stats:
            # Mostrar estadísticas
            stats = analyzer.get_system_stats()
            logger.info("📊 Estadísticas del sistema:")
            logger.info(json.dumps(stats, indent=2, ensure_ascii=False))
        
        else:
            # Análisis completo
            stats = await analyzer.analyze_all_data_optimized(args.limit)
            logger.info(f"🎉 Análisis optimizado completado con éxito!")
            
            # Optimizar sistema después del análisis
            analyzer.optimize_system()
            
    except Exception as e:
        logger.error(f"❌ Error en el analizador optimizado: {str(e)}")
        logger.info("💡 Verifica que tengas las dependencias instaladas y las credenciales configuradas")

if __name__ == "__main__":
    asyncio.run(main()) 