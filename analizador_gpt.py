"""
Analizador GPT para procesar textos extraídos de Supabase.
Utiliza OpenAI GPT para estimar precios, clasificar módulos y extraer condiciones comerciales.
"""

import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import sys

# Agregar el directorio actual al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase_client import SupabaseManager
from dotenv import load_dotenv
import openai

# Cargar variables de entorno
load_dotenv()

class GPTAnalyzer:
    """Analizador que utiliza GPT para procesar textos extraídos."""
    
    def __init__(self):
        """Inicializar el analizador con las credenciales de OpenAI."""
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError(
                "API Key de OpenAI no encontrada. "
                "Asegúrate de tener OPENAI_API_KEY en tu archivo .env"
            )
        
        openai.api_key = self.api_key
        self.supabase_manager = SupabaseManager()
        
        # Prompt base para el análisis
        self.analysis_prompt = """
        Analiza el siguiente texto extraído de un proveedor de servicios de marca blanca y proporciona:

        1. **Precio estimado**: Si no hay precio explícito, estima uno basado en el tipo de servicio y características mencionadas. Formato: "$X,XXX" o "No especificado"

        2. **Clasificación del módulo**: Clasifica en una de estas categorías:
           - Wallet Base (funcionalidad básica de wallet)
           - Wallet Avanzado (multi-currency, cold storage)
           - KYC/KYB (verificación de identidad)
           - Tarjeta (tarjetas de débito/crédito)
           - Trading Platform (plataforma de trading)
           - Payment Gateway (pasarela de pagos)
           - Liquidity Provider (proveedor de liquidez)
           - Compliance (cumplimiento regulatorio)
           - API Integration (integración de APIs)
           - White Label Solution (solución completa de marca blanca)
           - Otro (especificar)

        3. **Condiciones comerciales**: Extrae información sobre:
           - Setup fee (cargo inicial)
           - Monthly cost (costo mensual)
           - Transaction fees (comisiones por transacción)
           - Minimum requirements (requisitos mínimos)
           - Contract terms (términos del contrato)
           - Otros costos o condiciones

        Texto a analizar:
        {texto}

        Responde en formato JSON:
        {{
            "precio_estimado": "string",
            "clasificacion_modulo": "string",
            "condiciones_comerciales": {{
                "setup_fee": "string",
                "monthly_cost": "string",
                "transaction_fees": "string",
                "minimum_requirements": "string",
                "contract_terms": "string",
                "otros_costos": "string"
            }},
            "confianza_analisis": "alta|media|baja"
        }}
        """
    
    def analyze_text_with_gpt(self, texto: str) -> Dict[str, Any]:
        """
        Analizar texto usando GPT-4.
        
        Args:
            texto: Texto a analizar
            
        Returns:
            Diccionario con el análisis de GPT
        """
        try:
            print(f"🤖 Analizando texto con GPT... ({len(texto)} caracteres)")
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un analista experto en servicios financieros y tecnología blockchain. Analiza textos de proveedores de servicios de marca blanca de manera precisa y estructurada."
                    },
                    {
                        "role": "user",
                        "content": self.analysis_prompt.format(texto=texto)
                    }
                ],
                temperature=0.3,  # Baja temperatura para respuestas más consistentes
                max_tokens=1000
            )
            
            # Extraer y parsear la respuesta JSON
            content = response.choices[0].message.content.strip()
            
            # Limpiar la respuesta si tiene markdown
            if content.startswith('```json'):
                content = content.replace('```json', '').replace('```', '').strip()
            
            analysis = json.loads(content)
            
            print(f"✅ Análisis completado con confianza: {analysis.get('confianza_analisis', 'N/A')}")
            return analysis
            
        except json.JSONDecodeError as e:
            print(f"❌ Error parseando respuesta JSON de GPT: {str(e)}")
            return self._get_fallback_analysis()
        except Exception as e:
            print(f"❌ Error en análisis GPT: {str(e)}")
            return self._get_fallback_analysis()
    
    def _get_fallback_analysis(self) -> Dict[str, Any]:
        """Análisis de respaldo cuando GPT falla."""
        return {
            "precio_estimado": "No especificado",
            "clasificacion_modulo": "No clasificado",
            "condiciones_comerciales": {
                "setup_fee": "No especificado",
                "monthly_cost": "No especificado",
                "transaction_fees": "No especificado",
                "minimum_requirements": "No especificado",
                "contract_terms": "No especificado",
                "otros_costos": "No especificado"
            },
            "confianza_analisis": "baja"
        }
    
    def get_unanalyzed_data(self) -> List[Dict[str, Any]]:
        """
        Obtener datos no analizados de Supabase.
        
        Returns:
            Lista de registros sin análisis GPT
        """
        try:
            # Buscar registros que no tengan análisis GPT
            response = self.supabase_manager.client.table('precios_modulos').select('*').execute()
            
            # Filtrar registros que no tengan análisis GPT (esto se puede mejorar con una columna específica)
            unanalyzed = []
            for record in response.data:
                # Por ahora, asumimos que todos necesitan análisis
                # En el futuro, podrías agregar una columna 'analizado_gpt' a la tabla
                unanalyzed.append(record)
            
            print(f"📊 Encontrados {len(unanalyzed)} registros para analizar")
            return unanalyzed
            
        except Exception as e:
            print(f"❌ Error obteniendo datos de Supabase: {str(e)}")
            return []
    
    def update_record_with_analysis(self, record_id: int, analysis: Dict[str, Any]) -> bool:
        """
        Actualizar registro en Supabase con el análisis de GPT.
        
        Args:
            record_id: ID del registro a actualizar
            analysis: Análisis de GPT
            
        Returns:
            True si se actualizó correctamente
        """
        try:
            update_data = {
                'precio_gpt': analysis.get('precio_estimado'),
                'clasificacion_gpt': analysis.get('clasificacion_modulo'),
                'condiciones_comerciales': json.dumps(analysis.get('condiciones_comerciales', {})),
                'confianza_analisis': analysis.get('confianza_analisis'),
                'fecha_analisis_gpt': datetime.now().isoformat()
            }
            
            response = self.supabase_manager.client.table('precios_modulos').update(update_data).eq('id', record_id).execute()
            
            print(f"✅ Registro {record_id} actualizado con análisis GPT")
            return True
            
        except Exception as e:
            print(f"❌ Error actualizando registro {record_id}: {str(e)}")
            return False
    
    def analyze_all_data(self, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Analizar todos los datos no procesados.
        
        Args:
            limit: Límite de registros a procesar (None para todos)
            
        Returns:
            Estadísticas del análisis
        """
        print("🚀 Iniciando análisis GPT de todos los datos...")
        
        # Obtener datos no analizados
        unanalyzed_data = self.get_unanalyzed_data()
        
        if limit:
            unanalyzed_data = unanalyzed_data[:limit]
        
        if not unanalyzed_data:
            print("✅ No hay datos para analizar")
            return {"procesados": 0, "exitosos": 0, "fallidos": 0}
        
        stats = {
            "procesados": len(unanalyzed_data),
            "exitosos": 0,
            "fallidos": 0
        }
        
        for i, record in enumerate(unanalyzed_data, 1):
            print(f"\n📝 Procesando registro {i}/{len(unanalyzed_data)} (ID: {record['id']})")
            
            try:
                # Analizar texto con GPT
                analysis = self.analyze_text_with_gpt(record['texto_extraido'])
                
                # Actualizar registro en Supabase
                if self.update_record_with_analysis(record['id'], analysis):
                    stats["exitosos"] += 1
                else:
                    stats["fallidos"] += 1
                
                # Pausa entre requests para evitar rate limits
                import time
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Error procesando registro {record['id']}: {str(e)}")
                stats["fallidos"] += 1
        
        print(f"\n📊 Análisis completado:")
        print(f"   - Procesados: {stats['procesados']}")
        print(f"   - Exitosos: {stats['exitosos']}")
        print(f"   - Fallidos: {stats['fallidos']}")
        
        return stats

def main():
    """Función principal del analizador."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analizador GPT para datos de Supabase')
    parser.add_argument('--limit', type=int, help='Límite de registros a procesar')
    parser.add_argument('--test', action='store_true', help='Ejecutar análisis de prueba')
    
    args = parser.parse_args()
    
    print("🧠 Analizador GPT para Datos de Supabase")
    print("=" * 50)
    
    try:
        analyzer = GPTAnalyzer()
        
        if args.test:
            # Análisis de prueba
            test_text = """
            B2Broker offers comprehensive white label solutions for crypto exchanges. 
            Our platform includes advanced trading features, liquidity provision, and 
            regulatory compliance tools. Setup fee starts at $50,000 with monthly 
            maintenance costs of $5,000. Minimum transaction volume required: $1M monthly.
            """
            
            print("🧪 Ejecutando análisis de prueba...")
            analysis = analyzer.analyze_text_with_gpt(test_text)
            print("Resultado del análisis:")
            print(json.dumps(analysis, indent=2, ensure_ascii=False))
            
        else:
            # Análisis completo
            stats = analyzer.analyze_all_data(args.limit)
            print(f"\n🎉 Análisis completado con éxito!")
            
    except Exception as e:
        print(f"❌ Error en el analizador: {str(e)}")
        print("💡 Verifica que tengas OPENAI_API_KEY en tu archivo .env")

if __name__ == "__main__":
    main() 