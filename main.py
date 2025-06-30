"""
Script principal para ejecutar el web scraping de proveedores de marca blanca.
Coordina la ejecución de todos los scrapers y guarda los datos en Supabase.
"""

import sys
import os
from typing import List, Dict, Any
import argparse

# Agregar el directorio actual al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase_client import SupabaseManager
from modules.b2broker import B2BrokerScraper
from modules.wallester import WallesterScraper
from modules.sumsub import SumsubScraper

def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(description='Web Scraper para proveedores de marca blanca')
    parser.add_argument('--sample', action='store_true', 
                       help='Usar datos de muestra en lugar de hacer scraping real')
    parser.add_argument('--providers', nargs='+', 
                       choices=['b2broker', 'wallester', 'sumsub', 'all'],
                       default=['all'],
                       help='Proveedores específicos a scrapear')
    
    args = parser.parse_args()
    
    print("🎯 Web Scraper de Proveedores de Marca Blanca")
    print("=" * 60)
    
    # Inicializar Supabase
    try:
        print("🔌 Conectando a Supabase...")
        supabase_manager = SupabaseManager()
        
        # Probar conexión
        if not supabase_manager.test_connection():
            print("❌ No se pudo conectar a Supabase. Verifica las credenciales.")
            return
        
    except Exception as e:
        print(f"❌ Error inicializando Supabase: {str(e)}")
        print("💡 Asegúrate de tener un archivo .env con las credenciales correctas")
        return
    
    # Definir scrapers disponibles
    scrapers = {
        'b2broker': (B2BrokerScraper, 'B2Broker'),
        'wallester': (WallesterScraper, 'Wallester'),
        'sumsub': (SumsubScraper, 'Sumsub')
    }
    
    # Determinar qué scrapers ejecutar
    if 'all' in args.providers:
        scrapers_to_run = list(scrapers.keys())
    else:
        scrapers_to_run = args.providers
    
    all_results = []
    
    # Ejecutar scrapers
    for scraper_key in scrapers_to_run:
        if scraper_key in scrapers:
            scraper_class, scraper_name = scrapers[scraper_key]
            results = run_scraper(scraper_class, scraper_name, args.sample)
            all_results.extend(results)
        else:
            print(f"⚠️  Scraper '{scraper_key}' no encontrado")
    
    # Guardar en Supabase
    if all_results:
        print(f"\n💾 Guardando {len(all_results)} resultados en Supabase...")
        saved_count = save_to_supabase(supabase_manager, all_results)
        print(f"✅ {saved_count} de {len(all_results)} registros guardados exitosamente")
    else:
        print("⚠️  No se encontraron resultados para guardar")
    
    print("\n🎉 Proceso completado!")
    print("=" * 60) 