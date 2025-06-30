import requests
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:8001"

def test_health_check():
    """Prueba que el servidor esté funcionando"""
    print("🔍 Probando health check...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Servidor funcionando correctamente")
            return True
        else:
            print(f"❌ Error en health check: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando al servidor: {e}")
        return False

def test_insert_feedback():
    """Prueba inserción de feedback"""
    print("\n📝 Probando inserción de feedback...")
    
    test_data = {
        "producto": "Wallet + KYC",
        "mercado": "Colombia",
        "observacion": "El onboarding fue confuso para los usuarios",
        "categoria": "producto",
        "impacto": "medio",
        "accion_recomendada": "Simplificar el proceso de onboarding",
        "fuente": "gpt_chat",
        "metadata": {"usuario": "test", "version": "1.0"}
    }
    
    try:
        response = requests.post(f"{BASE_URL}/feedback/guardar_feedback/", json=test_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Feedback insertado exitosamente - ID: {result['id']}")
            return result['id']
        else:
            print(f"❌ Error insertando feedback: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error en inserción: {e}")
        return None

def test_get_feedback():
    """Prueba obtención de feedback"""
    print("\n📊 Probando obtención de feedback...")
    
    try:
        response = requests.get(f"{BASE_URL}/feedback/obtener_feedback/")
        if response.status_code == 200:
            data = response.json()
            feedbacks = data.get('data', [])
            print(f"✅ {len(feedbacks)} feedbacks encontrados")
            for fb in feedbacks[:3]:  # Mostrar solo los primeros 3
                print(f"   - ID: {fb['id']}, Producto: {fb['producto']}, Mercado: {fb['mercado']}")
            return True
        else:
            print(f"❌ Error obteniendo feedback: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error en obtención: {e}")
        return False

def test_multiple_inserts():
    """Prueba inserción múltiple de feedbacks"""
    print("\n🔄 Probando inserción múltiple...")
    
    test_feedbacks = [
        {
            "producto": "KYC",
            "mercado": "México",
            "observacion": "Precios muy altos comparados con la competencia",
            "categoria": "precio",
            "impacto": "alto",
            "accion_recomendada": "Revisar estrategia de precios",
            "fuente": "gpt_chat"
        },
        {
            "producto": "Onboarding Remoto",
            "mercado": "Perú",
            "observacion": "Funcionó muy bien, usuarios lo encontraron intuitivo",
            "categoria": "producto",
            "impacto": "alto",
            "accion_recomendada": "Expandir a otros mercados",
            "fuente": "gpt_chat"
        },
        {
            "producto": "Firma Digital",
            "mercado": "Chile",
            "observacion": "Necesitamos más opciones de integración",
            "categoria": "tecnico",
            "impacto": "medio",
            "accion_recomendada": "Desarrollar más APIs de integración",
            "fuente": "gpt_chat"
        }
    ]
    
    success_count = 0
    for i, feedback in enumerate(test_feedbacks, 1):
        try:
            response = requests.post(f"{BASE_URL}/feedback/guardar_feedback/", json=feedback)
            if response.status_code == 200:
                success_count += 1
                print(f"   ✅ Feedback {i} insertado")
            else:
                print(f"   ❌ Error en feedback {i}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error en feedback {i}: {e}")
    
    print(f"✅ {success_count}/{len(test_feedbacks)} feedbacks insertados exitosamente")
    return success_count == len(test_feedbacks)

def test_error_handling():
    """Prueba manejo de errores"""
    print("\n⚠️ Probando manejo de errores...")
    
    # Prueba con datos incompletos
    incomplete_data = {
        "producto": "Test Product"
        # Falta mercado y observacion (requeridos)
    }
    
    try:
        response = requests.post(f"{BASE_URL}/feedback/guardar_feedback/", json=incomplete_data)
        if response.status_code == 422:  # Validation error
            print("✅ Manejo de errores de validación funcionando")
            return True
        else:
            print(f"❌ Error inesperado: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error en prueba de errores: {e}")
        return False

def test_performance():
    """Prueba de rendimiento básica"""
    print("\n⚡ Probando rendimiento...")
    
    start_time = time.time()
    
    # Hacer 5 requests rápidos
    for i in range(5):
        try:
            response = requests.get(f"{BASE_URL}/feedback/obtener_feedback/")
            if response.status_code != 200:
                print(f"❌ Error en request {i+1}")
                return False
        except Exception as e:
            print(f"❌ Error en request {i+1}: {e}")
            return False
    
    end_time = time.time()
    total_time = end_time - start_time
    avg_time = total_time / 5
    
    print(f"✅ 5 requests completados en {total_time:.2f}s (promedio: {avg_time:.2f}s)")
    return avg_time < 2.0  # Debe ser menor a 2 segundos

def main():
    """Ejecuta todas las pruebas"""
    print("🚀 INICIANDO PRUEBAS COMPLETAS DEL SISTEMA")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health_check),
        ("Inserción de Feedback", test_insert_feedback),
        ("Obtención de Feedback", test_get_feedback),
        ("Inserción Múltiple", test_multiple_inserts),
        ("Manejo de Errores", test_error_handling),
        ("Rendimiento", test_performance)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error ejecutando {test_name}: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON! El sistema está listo para producción.")
        return True
    else:
        print("⚠️ Algunas pruebas fallaron. Revisar antes del despliegue.")
        return False

if __name__ == "__main__":
    main() 