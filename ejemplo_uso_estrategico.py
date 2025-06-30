#!/usr/bin/env python3
"""
Ejemplo de Uso del Sistema Estratégico
Demuestra el uso completo del GPT estratégico para análisis de mercado
"""

import asyncio
import json
import logging
from datetime import datetime

from gpt_estrategico import GPTEstrategico

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def ejemplo_analisis_completo():
    """Ejemplo de análisis completo de mercado"""
    print("🚀 Iniciando Ejemplo de Análisis Estratégico")
    print("=" * 60)
    
    # Inicializar GPT estratégico
    gpt = GPTEstrategico()
    
    # Ejemplo 1: Análisis de wallet crypto en México
    print("\n📊 EJEMPLO 1: Wallet Crypto en México")
    print("-" * 40)
    
    consulta_1 = "Queremos lanzar una wallet crypto en México para freelancers. ¿Qué sabes del mercado y qué nos recomiendas?"
    
    try:
        analisis_1 = await gpt.analizar_mercado_completo(consulta_1)
        
        print(f"✅ Análisis completado en {len(analisis_1.get('insights_integrados', []))} insights")
        print(f"📄 Documentos generados: {len(analisis_1.get('documentos_generados', []))}")
        print(f"🎯 Recomendaciones: {len(analisis_1.get('recomendaciones_finales', []))}")
        
        # Mostrar insights principales
        print("\n💡 Insights Principales:")
        for i, insight in enumerate(analisis_1.get('insights_integrados', [])[:3], 1):
            print(f"  {i}. {insight}")
        
        # Mostrar recomendaciones
        print("\n🎯 Recomendaciones Clave:")
        for i, rec in enumerate(analisis_1.get('recomendaciones_finales', [])[:3], 1):
            print(f"  {i}. {rec.get('recomendacion', 'N/A')}")
            print(f"     Acción: {rec.get('accion', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error en análisis 1: {str(e)}")
    
    # Ejemplo 2: Análisis de KYC en Colombia
    print("\n📊 EJEMPLO 2: KYC en Colombia")
    print("-" * 40)
    
    consulta_2 = "Vamos a lanzar una solución de KYC para fintechs en Colombia. Necesitamos análisis de mercado y plan de lanzamiento."
    
    try:
        analisis_2 = await gpt.analizar_mercado_completo(consulta_2)
        
        print(f"✅ Análisis completado en {len(analisis_2.get('insights_integrados', []))} insights")
        
        # Mostrar estrategia de entrada
        estrategia = analisis_2.get('estrategia_comercial', {})
        if estrategia:
            print(f"\n🚀 Estrategia de Entrada:")
            print(f"  Enfoque: {estrategia.get('estrategia_entrada', {}).get('enfoque', 'N/A')}")
            print(f"  Precio Sugerido: {estrategia.get('precio_sugerido', {}).get('precio_base', 'N/A')} USD")
        
        # Mostrar plan de producto
        plan = analisis_2.get('plan_producto', {})
        if plan:
            print(f"\n📋 Plan de Producto:")
            print(f"  Fases: {len(plan.get('fases', []))}")
            print(f"  Timeline: {plan.get('timeline', {}).get('duracion_total', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error en análisis 2: {str(e)}")
    
    # Ejemplo 3: Análisis de onboarding remoto en Perú
    print("\n📊 EJEMPLO 3: Onboarding Remoto en Perú")
    print("-" * 40)
    
    consulta_3 = "Vamos a lanzar una nueva solución de onboarding remoto para fintechs en Perú. ¿Qué necesitamos saber?"
    
    try:
        analisis_3 = await gpt.analizar_mercado_completo(consulta_3)
        
        print(f"✅ Análisis completado en {len(analisis_3.get('insights_integrados', []))} insights")
        
        # Mostrar buyer persona
        buyer_persona = analisis_3.get('estrategia_comercial', {}).get('buyer_persona', {})
        if buyer_persona:
            print(f"\n👤 Buyer Persona:")
            print(f"  Nombre: {buyer_persona.get('nombre', 'N/A')}")
            print(f"  Edad: {buyer_persona.get('edad', 'N/A')}")
            print(f"  Ingresos: {buyer_persona.get('ingresos', 'N/A')}")
            print(f"  Necesidades: {', '.join(buyer_persona.get('necesidades', [])[:2])}")
        
        # Mostrar recursos comerciales
        recursos = analisis_3.get('estrategia_comercial', {}).get('recursos_comerciales', {})
        if recursos:
            equipo = recursos.get('equipo', {})
            print(f"\n👥 Equipo Necesario:")
            for rol, cantidad in equipo.items():
                print(f"  {rol}: {cantidad} personas")
        
    except Exception as e:
        print(f"❌ Error en análisis 3: {str(e)}")

async def ejemplo_consulta_historial():
    """Ejemplo de consulta de historial"""
    print("\n📚 EJEMPLO: Consulta de Historial")
    print("-" * 40)
    
    gpt = GPTEstrategico()
    
    try:
        # Consultar historial
        historial = await gpt.consultar_historial()
        
        print(f"📊 Análisis en historial: {len(historial)}")
        
        if historial:
            print("\n📋 Últimos Análisis:")
            for i, analisis in enumerate(historial[:3], 1):
                print(f"  {i}. {analisis.get('producto', 'N/A')} en {analisis.get('pais', 'N/A')}")
                print(f"     Fecha: {analisis.get('timestamp', 'N/A')}")
                print(f"     Estado: {analisis.get('estado', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error consultando historial: {str(e)}")

async def ejemplo_retroalimentacion():
    """Ejemplo de análisis de retroalimentación"""
    print("\n🔄 EJEMPLO: Análisis de Retroalimentación")
    print("-" * 40)
    
    gpt = GPTEstrategico()
    
    try:
        # Datos de ventas simulados
        datos_ventas = {
            'precio_real': 35.0,  # USD
            'adopcion_real': 65,  # %
            'mrr_real': 45000,    # USD
            'cac_real': 450,      # USD
            'churn_real': 4.5,    # %
            'periodo': '6 meses'
        }
        
        # Simular ID de análisis (en producción vendría de Supabase)
        id_analisis = "ejemplo_123"
        
        print("📊 Analizando retroalimentación de ventas...")
        print(f"  Precio Real: ${datos_ventas['precio_real']}")
        print(f"  Adopción Real: {datos_ventas['adopcion_real']}%")
        print(f"  MRR Real: ${datos_ventas['mrr_real']:,}")
        
        # En producción, esto analizaría datos reales
        print("\n✅ Análisis de retroalimentación completado")
        print("💡 Ajustes recomendados generados")
        
    except Exception as e:
        print(f"❌ Error en retroalimentación: {str(e)}")

async def ejemplo_documentos():
    """Ejemplo de generación de documentos"""
    print("\n📄 EJEMPLO: Generación de Documentos")
    print("-" * 40)
    
    gpt = GPTEstrategico()
    
    consulta = "Queremos lanzar firma digital en México para notarías y abogados"
    
    try:
        analisis = await gpt.analizar_mercado_completo(consulta)
        
        documentos = analisis.get('documentos_generados', [])
        
        print(f"📄 Documentos generados: {len(documentos)}")
        
        for i, doc in enumerate(documentos, 1):
            print(f"\n  {i}. {doc.get('titulo', 'N/A')}")
            print(f"     Tipo: {doc.get('tipo', 'N/A')}")
            print(f"     Formato: {doc.get('formato', 'N/A')}")
            
            # Mostrar preview del contenido
            contenido = doc.get('contenido', '')
            if contenido:
                preview = contenido[:100] + "..." if len(contenido) > 100 else contenido
                print(f"     Preview: {preview}")
        
    except Exception as e:
        print(f"❌ Error generando documentos: {str(e)}")

async def main():
    """Función principal"""
    print("🎯 SISTEMA ESTRATÉGICO - DEMOSTRACIÓN COMPLETA")
    print("=" * 60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Este script demuestra las capacidades del sistema estratégico")
    print("para análisis de mercado, estrategia comercial y planificación.")
    
    try:
        # Ejemplo 1: Análisis completo
        await ejemplo_analisis_completo()
        
        # Ejemplo 2: Consulta de historial
        await ejemplo_consulta_historial()
        
        # Ejemplo 3: Retroalimentación
        await ejemplo_retroalimentacion()
        
        # Ejemplo 4: Documentos
        await ejemplo_documentos()
        
        print("\n" + "=" * 60)
        print("✅ DEMOSTRACIÓN COMPLETADA")
        print("\n🎯 Próximos pasos:")
        print("1. Configurar variables de entorno (.env)")
        print("2. Instalar dependencias: pip install -r requirements.txt")
        print("3. Configurar APIs (Perplexity, SerpAPI, Brave)")
        print("4. Ejecutar análisis reales")
        print("5. Monitorear resultados y ajustar estrategias")
        
    except Exception as e:
        print(f"\n❌ Error en demostración: {str(e)}")
        print("Verificar configuración y dependencias")

if __name__ == "__main__":
    asyncio.run(main()) 