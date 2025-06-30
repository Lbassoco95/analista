"""
Script para iniciar el servidor de la API FastAPI.
"""

import os
import sys
import uvicorn
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Función principal para iniciar el servidor."""
    
    # Verificar que estamos en el directorio correcto
    current_dir = Path(__file__).parent
    project_root = current_dir.parent
    
    # Agregar el directorio del proyecto al path
    sys.path.insert(0, str(project_root))
    
    # Verificar variables de entorno
    required_env_vars = ['SUPABASE_URL', 'SUPABASE_KEY']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.warning(f"⚠️ Variables de entorno faltantes: {missing_vars}")
        logger.info("💡 Crea un archivo .env basado en env_example.txt")
    
    # Configuración del servidor
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', 8000))
    reload = os.getenv('API_RELOAD', 'true').lower() == 'true'
    log_level = os.getenv('API_LOG_LEVEL', 'info')
    
    logger.info("🚀 Iniciando servidor de API FastAPI...")
    logger.info(f"📍 Host: {host}")
    logger.info(f"🔌 Puerto: {port}")
    logger.info(f"🔄 Reload: {reload}")
    logger.info(f"📝 Log Level: {log_level}")
    
    # Iniciar servidor
    try:
        uvicorn.run(
            "api.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level=log_level,
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("🛑 Servidor detenido por el usuario")
    except Exception as e:
        logger.error(f"❌ Error iniciando servidor: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 