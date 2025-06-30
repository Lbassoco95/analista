#!/usr/bin/env python3
"""
Script de Prueba para el Analizador LR Completo
Verifica que todos los componentes funcionen correctamente
"""

import asyncio
import os
import sys
from typing import List, Dict, Any

def verificar_dependencias():
    """Verificar que todas las dependencias estén instaladas"""
    print("🔍 Verificando dependencias...")
    
    dependencias = [
        'openai', 'pinecone', 'langchain', 'sentence_transformers',
        'requests', 'beautifulsoup4', 'numpy', 'pandas'
    ]
    
    faltantes = []
    for dep in dependencias:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} - FALTANTE")
            faltantes.append(dep)
    
    if faltantes:
        print(f"\n❌ Dependencias faltantes: {', '.join(faltantes)}")
        print("Ejecuta: pip install -r requirements.txt")
        return False
    
    print("✅ Todas las dependencias están instaladas")
    return True

def verificar_variables_entorno():
    """Verificar variables de entorno necesarias"""
    print("\n🔍 Verificando variables de entorno...")
    
    variables = [
        'OPENAI_API_KEY',
        'PINECONE_API_KEY',
        'PINECONE_ENVIRONMENT'
    ]
    
    faltantes = []
    for var in variables:
        if os.getenv(var):
            print(f"✅ {var}")
        else:
            print(f"❌ {var} - NO CONFIGURADA")
            faltantes.append(var)
    
    if faltantes:
        print(f"\n❌ Variables faltantes: {', '.join(faltantes)}")
        print("Configura las variables en tu archivo .env")
        return False
    
    print("✅ Todas las variables están configuradas")
    return True

async def test_componentes():
    """Probar componentes individuales"""
    print("\n🧪 Probando componentes...")
    
    try:
        # Test 1: ScraperInteligente
        print("1. Probando ScraperInteligente...")
        from scraper_inteligente import ScraperInteligente
        scraper = ScraperInteligente()
        print("✅ ScraperInteligente inicializado")
        
        # Test 2: PineconeManager
        print("2. Probando PineconeManager...")
        from utils.pinecone_manager import PineconeManager
        pinecone_manager = PineconeManager()
        print("✅ PineconeManager inicializado")
        
        # Test 3: ChatGPTManager
        print("3. Probando ChatGPTManager...")
        from utils.chat_gpt_manager import ChatGPTManager
        chat_manager = ChatGPTManager()
        print("✅ ChatGPTManager inicializado")
        
        # Test 4: AnalizadorLRCompleto
        print("4. Probando AnalizadorLRCompleto...")
        from analizador_lr_completo import AnalizadorLRCompleto
        analizador = AnalizadorLRCompleto()
        print("✅ AnalizadorLRCompleto inicializado")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en componentes: {str(e)}")
        return False

async def test_flujo_mini():
    """Probar un flujo mínimo con un proveedor"""
    print("\n🚀 Probando flujo mínimo...")
    
    try:
        from analizador_lr_completo import AnalizadorLRCompleto
        
        # Inicializar analizador
        analizador = AnalizadorLRCompleto()
        
        # Configurar para prueba rápida
        analizador.config['batch_size'] = 1
        analizador.config['delay_between_batches'] = 1
        analizador.config['enable_validation'] = False
        analizador.config['enable_metadata_enrichment'] = False
        
        # Probar con un solo proveedor
        proveedores = ["Sumsub"]
        
        print(f"Analizando {len(proveedores)} proveedor(es)...")
        
        # Ejecutar flujo completo
        resultados = await analizador.ejecutar_flujo_completo(proveedores)
        
        # Verificar resultados
        if resultados and 'etapas' in resultados:
            print("✅ Flujo completado exitosamente")
            print(f"   - Etapas: {len(resultados['etapas'])}")
            print(f"   - Errores: {len(resultados['errores'])}")
            return True
        else:
            print("❌ Flujo no completado correctamente")
            return False
            
    except Exception as e:
        print(f"❌ Error en flujo mínimo: {str(e)}")
        return False

async def test_consulta():
    """Probar consulta interactiva"""
    print("\n💬 Probando consulta interactiva...")
    
    try:
        from analizador_lr_completo import AnalizadorLRCompleto
        
        analizador = AnalizadorLRCompleto()
        
        # Consulta simple
        pregunta = "¿Qué es el análisis de proveedores?"
        respuesta = await analizador.consulta_interactiva(pregunta)
        
        if respuesta and len(respuesta) > 10:
            print("✅ Consulta interactiva funcionando")
            print(f"   Respuesta: {respuesta[:100]}...")
            return True
        else:
            print("❌ Consulta no funcionó correctamente")
            return False
            
    except Exception as e:
        print(f"❌ Error en consulta: {str(e)}")
        return False

async def main():
    """Función principal de pruebas"""
    print("🧪 INICIANDO PRUEBAS DEL ANALIZADOR LR COMPLETO")
    print("="*60)
    
    # Verificar dependencias
    if not verificar_dependencias():
        sys.exit(1)
    
    # Verificar variables de entorno
    if not verificar_variables_entorno():
        print("\n⚠️  Algunas variables no están configuradas")
        print("Las pruebas pueden fallar")
    
    # Probar componentes
    if not await test_componentes():
        print("\n❌ Error en componentes básicos")
        sys.exit(1)
    
    # Probar flujo mínimo
    if not await test_flujo_mini():
        print("\n❌ Error en flujo mínimo")
        sys.exit(1)
    
    # Probar consulta
    if not await test_consulta():
        print("\n❌ Error en consulta interactiva")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("🎉 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!")
    print("="*60)
    print("\nEl Analizador LR Completo está listo para usar.")
    print("\nPróximos pasos:")
    print("1. Ejecuta: python interfaz_lr.py")
    print("2. O ejecuta: python analizador_lr_completo.py")
    print("3. Consulta la documentación en README_LR.md")

if __name__ == "__main__":
    asyncio.run(main()) 