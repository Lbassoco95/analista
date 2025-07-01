import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_result(endpoint_name, response):
    print(f"\n{'='*50}")
    print(f"🔍 {endpoint_name}")
    print(f"{'='*50}")
    print(f"Status: {response.status_code}")
    print(f"URL: {response.url}")
    
    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
    except:
        print(f"Response: {response.text}")
    
    print(f"{'='*50}")

def test_analyze():
    print("\n🧠 Probando análisis de texto...")
    data = {
        "text": "El precio del módulo de inventario es de $500 USD por mes",
        "source": "test_web"
    }
    r = requests.post(f"{BASE_URL}/analyze", json=data)
    print_result("Análisis de Texto", r)

def test_analyze_batch():
    print("\n📦 Probando análisis en lote...")
    data = {
        "texts": [
            {"text": "Módulo CRM: $300 USD/mes", "source": "web1"},
            {"text": "Sistema de facturación: $150 USD por mes", "source": "web2"}
        ],
        "use_local_models": True,
        "use_gpt_backup": True
    }
    r = requests.post(f"{BASE_URL}/analyze-batch", json=data)
    print_result("Análisis en Lote", r)

def test_scraping():
    print("\n🌐 Probando scraping...")
    data = {
        "url": "https://example.com"
    }
    r = requests.post(f"{BASE_URL}/scraping/extraer", json=data)
    print_result("Scraping Extraer Info", r)

def test_feedback():
    print("\n💬 Probando feedback...")
    data = {
        "producto": "CRM",
        "mercado": "México",
        "comentario": "Excelente funcionalidad",
        "calificacion": 5,
        "fuente": "cliente_test"
    }
    r = requests.post(f"{BASE_URL}/feedback/guardar", json=data)
    print_result("Guardar Feedback", r)

def test_obtener_feedback():
    print("\n📋 Obteniendo feedback...")
    r = requests.get(f"{BASE_URL}/feedback/obtener")
    print_result("Obtener Feedback", r)

def test_analizar_feedback():
    print("\n📊 Analizando feedback...")
    r = requests.get(f"{BASE_URL}/feedback/analizar/CRM/México")
    print_result("Analizar Feedback", r)

def test_estadisticas():
    print("\n📈 Obteniendo estadísticas...")
    r = requests.get(f"{BASE_URL}/feedback/estadisticas")
    print_result("Estadísticas", r)

def test_documentos_scrapings():
    print("\n📄 Probando consulta de documentos scrapings...")
    r = requests.get(f"{BASE_URL}/scraping/documentos?limit=10")
    print_result("Documentos Scrapings", r)

def test_documento_especifico():
    print("\n🔍 Probando documento específico...")
    # Primero obtenemos la lista para ver si hay documentos
    r_list = requests.get(f"{BASE_URL}/scraping/documentos?limit=1")
    if r_list.status_code == 200:
        data = r_list.json()
        if data.get("documentos") and len(data["documentos"]) > 0:
            doc_id = data["documentos"][0]["id"]
            r = requests.get(f"{BASE_URL}/scraping/documentos/{doc_id}")
            print_result(f"Documento Específico (ID: {doc_id})", r)
        else:
            print("No hay documentos para probar")
    else:
        print("Error obteniendo lista de documentos")

def test_model_info():
    print("\n🤖 Obteniendo información de modelos...")
    r = requests.get(f"{BASE_URL}/model-info")
    print_result("Model Info", r)

def test_stats():
    print("\n📊 Obteniendo estadísticas del sistema...")
    r = requests.get(f"{BASE_URL}/stats")
    print_result("System Stats", r)

def test_function_definitions():
    print("\n🔧 Obteniendo definiciones de funciones...")
    r = requests.get(f"{BASE_URL}/function-definitions")
    print_result("Function Definitions", r)

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de endpoints de la API")
    print(f"Base URL: {BASE_URL}")
    
    try:
        # Pruebas básicas
        test_analyze()
        test_analyze_batch()
        test_scraping()
        
        # Pruebas de feedback
        test_feedback()
        test_obtener_feedback()
        test_analizar_feedback()
        test_estadisticas()
        
        # Pruebas de documentos scrapings
        test_documentos_scrapings()
        test_documento_especifico()
        
        # Pruebas de información del sistema
        test_model_info()
        test_stats()
        test_function_definitions()
        
        print("\n✅ Todas las pruebas completadas")
        
    except requests.exceptions.ConnectionError:
        print(f"❌ No se pudo conectar a {BASE_URL}")
        print("Asegúrate de que el servidor esté ejecutándose")
    except Exception as e:
        print(f"❌ Error durante las pruebas: {str(e)}") 