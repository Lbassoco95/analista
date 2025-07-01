#!/usr/bin/env python3
"""
Script de prueba para verificar que todas las importaciones funcionen correctamente.
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Probar todas las importaciones críticas."""
    print("🔍 Probando importaciones...")
    
    try:
        # Probar importaciones de utils
        print("  ✅ Probando utils.optimized_analyzer...")
        from utils.optimized_analyzer import OptimizedAnalyzer
        print("  ✅ OptimizedAnalyzer importado correctamente")
        
        print("  ✅ Probando utils.model_manager...")
        from utils.model_manager import ModelManager
        print("  ✅ ModelManager importado correctamente")
        
        print("  ✅ Probando utils.extract_price...")
        from utils.extract_price import extract_price_from_text, clean_text
        print("  ✅ extract_price importado correctamente")
        
        print("  ✅ Probando utils.pinecone_manager...")
        from utils.pinecone_manager import PineconeManager
        print("  ✅ PineconeManager importado correctamente")
        
        print("  ✅ Probando utils.chat_gpt_manager...")
        from utils.chat_gpt_manager import ChatGPTManager
        print("  ✅ ChatGPTManager importado correctamente")
        
        # Probar importaciones de api
        print("  ✅ Probando api.main_production...")
        from api.main_production import app
        print("  ✅ app de main_production importado correctamente")
        
        print("  ✅ Probando api.feedback...")
        from api.feedback import router as feedback_router
        print("  ✅ feedback_router importado correctamente")
        
        print("  ✅ Probando api.scraping...")
        from api.scraping import router as scraping_router
        print("  ✅ scraping_router importado correctamente")
        
        print("  ✅ Probando api.analisis_estrategico...")
        from api.analisis_estrategico import router as analisis_router
        print("  ✅ analisis_router importado correctamente")
        
        print("  ✅ Probando api.consulta_inteligente...")
        from api.consulta_inteligente import router as consulta_router
        print("  ✅ consulta_router importado correctamente")
        
        print("\n🎉 ¡Todas las importaciones funcionan correctamente!")
        return True
        
    except ImportError as e:
        print(f"\n❌ Error de importación: {str(e)}")
        return False
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        return False

def test_basic_functionality():
    """Probar funcionalidad básica de los componentes."""
    print("\n🔍 Probando funcionalidad básica...")
    
    try:
        # Probar OptimizedAnalyzer
        print("  ✅ Probando OptimizedAnalyzer...")
        analyzer = OptimizedAnalyzer(use_local_models=False, use_gpt=False)
        print("  ✅ OptimizedAnalyzer inicializado correctamente")
        
        # Probar funciones de extract_price
        print("  ✅ Probando extract_price...")
        test_text = "El precio es $100 USD"
        result = extract_price_from_text(test_text)
        print(f"  ✅ extract_price_from_text funcionó: {result}")
        
        # Probar clean_text
        cleaned = clean_text(test_text)
        print(f"  ✅ clean_text funcionó: {cleaned}")
        
        print("\n🎉 ¡Todas las funcionalidades básicas funcionan correctamente!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error en funcionalidad básica: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de importación y funcionalidad...\n")
    
    imports_ok = test_imports()
    functionality_ok = test_basic_functionality()
    
    if imports_ok and functionality_ok:
        print("\n✅ ¡Todas las pruebas pasaron exitosamente!")
        sys.exit(0)
    else:
        print("\n❌ Algunas pruebas fallaron.")
        sys.exit(1) 