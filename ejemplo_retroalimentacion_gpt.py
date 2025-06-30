#!/usr/bin/env python3
"""
Ejemplo de Retroalimentación desde GPT Personalizado
Demuestra cómo funciona la integración de retroalimentación con Function Calling
"""

import asyncio
import json
import logging
from datetime import datetime
import requests
from typing import Dict, Any

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GPTFeedbackSimulator:
    """
    Simulador de GPT personalizado que envía retroalimentación
    """
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        """Inicializar simulador"""
        self.api_base_url = api_base_url
        self.feedback_endpoint = f"{api_base_url}/feedback/guardar_feedback/"
        
        # Ejemplos de conversaciones de chat
        self.chat_examples = [
            {
                "user_message": "El producto Wallet + KYC en Colombia tuvo baja adopción porque el onboarding fue confuso.",
                "expected_feedback": {
                    "producto": "Wallet + KYC",
                    "mercado": "Colombia",
                    "observacion": "Baja adopción debido a onboarding confuso",
                    "categoria": "producto",
                    "impacto": "alto",
                    "accion_recomendada": "Rediseñar proceso de onboarding para mayor claridad"
                }
            },
            {
                "user_message": "Los precios de KYC en México son muy altos comparados con la competencia.",
                "expected_feedback": {
                    "producto": "KYC",
                    "mercado": "México",
                    "observacion": "Precios muy altos comparados con la competencia",
                    "categoria": "precio",
                    "impacto": "alto",
                    "accion_recomendada": "Revisar estrategia de pricing para ser más competitivo"
                }
            },
            {
                "user_message": "El onboarding remoto en Perú funcionó muy bien, los usuarios lo encontraron intuitivo.",
                "expected_feedback": {
                    "producto": "Onboarding Remoto",
                    "mercado": "Perú",
                    "observacion": "Onboarding funcionó muy bien, usuarios lo encontraron intuitivo",
                    "categoria": "producto",
                    "impacto": "alto",
                    "accion_recomendada": "Mantener la simplicidad del diseño y replicar en otros mercados"
                }
            },
            {
                "user_message": "Necesitamos más opciones de integración para la firma digital en Chile.",
                "expected_feedback": {
                    "producto": "Firma Digital",
                    "mercado": "Chile",
                    "observacion": "Necesitamos más opciones de integración",
                    "categoria": "tecnico",
                    "impacto": "medio",
                    "accion_recomendada": "Desarrollar APIs adicionales y documentación de integración"
                }
            },
            {
                "user_message": "El mercado de wallets en Argentina está muy regulado, necesitamos ajustar nuestra estrategia.",
                "expected_feedback": {
                    "producto": "Wallet",
                    "mercado": "Argentina",
                    "observacion": "Mercado muy regulado, necesitamos ajustar estrategia",
                    "categoria": "regulacion",
                    "impacto": "alto",
                    "accion_recomendada": "Consultar con expertos legales y ajustar estrategia de compliance"
                }
            }
        ]
    
    async def simular_conversacion_gpt(self, example_index: int = 0):
        """
        Simula una conversación de GPT que procesa retroalimentación
        
        Args:
            example_index: Índice del ejemplo a usar
        """
        if example_index >= len(self.chat_examples):
            logger.error("Índice de ejemplo fuera de rango")
            return
        
        example = self.chat_examples[example_index]
        user_message = example["user_message"]
        expected_feedback = example["expected_feedback"]
        
        print(f"\n🤖 SIMULACIÓN DE CONVERSACIÓN GPT")
        print("=" * 50)
        print(f"👤 Usuario: {user_message}")
        
        # Simular procesamiento de GPT
        print(f"\n🧠 GPT procesando mensaje...")
        
        # Extraer información del mensaje (simulado)
        extracted_info = self._extraer_info_mensaje(user_message)
        
        print(f"📝 Información extraída:")
        print(f"   Producto: {extracted_info['producto']}")
        print(f"   Mercado: {extracted_info['mercado']}")
        print(f"   Observación: {extracted_info['observacion']}")
        print(f"   Categoría: {extracted_info['categoria']}")
        print(f"   Impacto: {extracted_info['impacto']}")
        
        # Simular llamada a función
        print(f"\n🔗 GPT llamando función guardar_feedback...")
        
        # Enviar feedback a la API
        success = await self._enviar_feedback_api(extracted_info)
        
        if success:
            print(f"✅ Feedback guardado exitosamente")
            print(f"💾 Información almacenada en Supabase")
            
            # Simular respuesta de GPT
            print(f"\n🤖 Respuesta de GPT:")
            print(f"   He guardado tu retroalimentación sobre {extracted_info['producto']} en {extracted_info['mercado']}.")
            print(f"   Esta información será utilizada para mejorar nuestras estrategias futuras.")
            print(f"   ¿Te gustaría que analice el feedback acumulado para este producto?")
        else:
            print(f"❌ Error guardando feedback")
    
    def _extraer_info_mensaje(self, mensaje: str) -> Dict[str, Any]:
        """
        Extrae información estructurada del mensaje del usuario
        (En producción, esto lo haría GPT automáticamente)
        """
        # Mapeo de productos
        productos = {
            'wallet': 'Wallet',
            'kyc': 'KYC',
            'onboarding': 'Onboarding Remoto',
            'firma digital': 'Firma Digital'
        }
        
        # Mapeo de países
        paises = ['mexico', 'colombia', 'peru', 'chile', 'argentina', 'brasil']
        
        # Mapeo de categorías
        categorias = {
            'precio': ['precio', 'costos', 'tarifas', 'caro', 'barato'],
            'producto': ['onboarding', 'confuso', 'intuitivo', 'funcionalidad'],
            'mercado': ['mercado', 'competencia', 'adopción'],
            'regulacion': ['regulado', 'regulaciones', 'compliance'],
            'tecnico': ['integración', 'api', 'técnico', 'desarrollo']
        }
        
        # Extraer información
        mensaje_lower = mensaje.lower()
        
        # Producto
        producto_extraido = "Producto Genérico"
        for key, value in productos.items():
            if key in mensaje_lower:
                producto_extraido = value
                break
        
        # País
        pais_extraido = "País Genérico"
        for pais in paises:
            if pais in mensaje_lower:
                pais_extraido = pais.title()
                break
        
        # Categoría
        categoria_extraida = "general"
        for categoria, keywords in categorias.items():
            if any(keyword in mensaje_lower for keyword in keywords):
                categoria_extraida = categoria
                break
        
        # Impacto (simulado basado en palabras clave)
        impacto = "medio"
        if any(word in mensaje_lower for word in ['muy', 'alto', 'crítico', 'importante']):
            impacto = "alto"
        elif any(word in mensaje_lower for word in ['bajo', 'poco', 'menor']):
            impacto = "bajo"
        
        # Observación (simplificada)
        observacion = mensaje[:100] + "..." if len(mensaje) > 100 else mensaje
        
        return {
            'producto': producto_extraido,
            'mercado': pais_extraido,
            'observacion': observacion,
            'categoria': categoria_extraida,
            'impacto': impacto,
            'accion_recomendada': f"Revisar {categoria_extraida} para {producto_extraido} en {pais_extraido}",
            'fuente': 'gpt_chat'
        }
    
    async def _enviar_feedback_api(self, feedback_data: Dict[str, Any]) -> bool:
        """
        Envía feedback a la API
        
        Args:
            feedback_data: Datos del feedback
            
        Returns:
            True si se guardó exitosamente
        """
        try:
            response = requests.post(
                self.feedback_endpoint,
                json=feedback_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Feedback guardado: {result.get('id', 'N/A')}")
                return True
            else:
                logger.error(f"Error API: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error enviando feedback: {str(e)}")
            return False
    
    async def simular_multiples_conversaciones(self):
        """Simula múltiples conversaciones de GPT"""
        print("🚀 SIMULACIÓN DE MÚLTIPLES CONVERSACIONES GPT")
        print("=" * 60)
        
        for i, example in enumerate(self.chat_examples):
            print(f"\n📝 Conversación {i+1}/{len(self.chat_examples)}")
            await self.simular_conversacion_gpt(i)
            
            # Pausa entre conversaciones
            if i < len(self.chat_examples) - 1:
                print("\n⏳ Esperando 2 segundos...")
                await asyncio.sleep(2)
    
    async def consultar_feedback_almacenado(self, producto: str = None, mercado: str = None):
        """
        Consulta feedback almacenado
        
        Args:
            producto: Filtrar por producto
            mercado: Filtrar por mercado
        """
        try:
            endpoint = f"{self.api_base_url}/feedback/obtener_feedback/"
            params = {}
            
            if producto:
                params['producto'] = producto
            if mercado:
                params['mercado'] = mercado
            
            response = requests.get(endpoint, params=params, timeout=10)
            
            if response.status_code == 200:
                feedbacks = response.json()
                print(f"\n📊 FEEDBACK ALMACENADO")
                print("=" * 40)
                print(f"Total encontrados: {len(feedbacks)}")
                
                for i, feedback in enumerate(feedbacks[:5], 1):  # Mostrar solo los primeros 5
                    print(f"\n{i}. {feedback.get('producto', 'N/A')} en {feedback.get('mercado', 'N/A')}")
                    print(f"   Observación: {feedback.get('observacion', 'N/A')[:50]}...")
                    print(f"   Categoría: {feedback.get('categoria', 'N/A')}")
                    print(f"   Impacto: {feedback.get('impacto', 'N/A')}")
                    print(f"   Fecha: {feedback.get('fecha', 'N/A')}")
                
                return feedbacks
            else:
                logger.error(f"Error consultando feedback: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error en consulta: {str(e)}")
            return []
    
    async def analizar_feedback_producto(self, producto: str, mercado: str):
        """
        Analiza feedback de un producto específico
        
        Args:
            producto: Nombre del producto
            mercado: País o mercado
        """
        try:
            endpoint = f"{self.api_base_url}/feedback/analizar_feedback/{producto}/{mercado}"
            response = requests.get(endpoint, timeout=10)
            
            if response.status_code == 200:
                analisis = response.json()
                print(f"\n📈 ANÁLISIS DE FEEDBACK")
                print("=" * 40)
                print(f"Producto: {analisis.get('producto', 'N/A')}")
                print(f"Mercado: {analisis.get('mercado', 'N/A')}")
                print(f"Total feedbacks: {analisis.get('total_feedbacks', 0)}")
                
                # Categorías más comunes
                categorias = analisis.get('categorias_mas_comunes', [])
                if categorias:
                    print(f"\n🏷️ Categorías más comunes:")
                    for categoria, count in categorias:
                        print(f"   {categoria}: {count} feedbacks")
                
                # Distribución de impactos
                impactos = analisis.get('distribucion_impactos', {})
                if impactos:
                    print(f"\n📊 Distribución de impactos:")
                    for impacto, count in impactos.items():
                        print(f"   {impacto}: {count} feedbacks")
                
                # Observaciones clave
                observaciones = analisis.get('observaciones_clave', [])
                if observaciones:
                    print(f"\n💡 Observaciones clave:")
                    for i, obs in enumerate(observaciones[:3], 1):
                        print(f"   {i}. {obs[:60]}...")
                
                return analisis
            else:
                logger.error(f"Error analizando feedback: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error en análisis: {str(e)}")
            return None

async def main():
    """Función principal"""
    print("🎯 SIMULADOR DE RETROALIMENTACIÓN GPT")
    print("=" * 60)
    print("Este script simula cómo GPT personalizado procesa retroalimentación")
    print("y la envía automáticamente a la API para almacenamiento.")
    
    # Inicializar simulador
    simulador = GPTFeedbackSimulator()
    
    try:
        # 1. Simular múltiples conversaciones
        await simulador.simular_multiples_conversaciones()
        
        # 2. Consultar feedback almacenado
        print(f"\n" + "=" * 60)
        await simulador.consultar_feedback_almacenado()
        
        # 3. Analizar feedback específico
        print(f"\n" + "=" * 60)
        await simulador.analizar_feedback_producto("Wallet + KYC", "Colombia")
        
        print(f"\n" + "=" * 60)
        print("✅ SIMULACIÓN COMPLETADA")
        print("\n🎯 Próximos pasos:")
        print("1. Configurar GPT personalizado en https://chat.openai.com/gpts")
        print("2. Agregar las funciones definidas en gpt_function_definitions.json")
        print("3. Conectar con tu API desplegada")
        print("4. Probar retroalimentación real desde el chat")
        
    except Exception as e:
        print(f"\n❌ Error en simulación: {str(e)}")
        print("Verificar que la API esté ejecutándose en http://localhost:8000")

if __name__ == "__main__":
    asyncio.run(main()) 