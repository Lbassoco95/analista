#!/bin/bash

# Script de despliegue para AWS EC2
# Autor: Sistema de Retroalimentación GPT
# Fecha: $(date)

set -e  # Salir si hay algún error

echo "🚀 INICIANDO DESPLIEGUE EN AWS EC2"
echo "=================================="

# Variables de configuración
EC2_IP="54.219.211.204"
EC2_USER="ubuntu"
PROJECT_PATH="/home/ubuntu/kawii-analista-datos"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir con colores
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️ $1${NC}"
}

echo ""
print_info "Este script te ayudará a desplegar los cambios en tu instancia EC2"
echo ""

# Verificar que los cambios estén en GitHub
print_status "Verificando que los cambios estén en GitHub..."
if ! git status --porcelain | grep -q .; then
    print_warning "No hay cambios pendientes para subir"
else
    print_error "Tienes cambios sin commitear. Ejecuta:"
    echo "  git add ."
    echo "  git commit -m 'Tu mensaje'"
    echo "  git push origin main"
    exit 1
fi

echo ""
print_info "PASOS PARA DESPLEGAR EN EC2:"
echo ""

print_info "1. Conéctate a tu instancia EC2:"
echo "   ssh -i TU_CLAVE.pem ubuntu@$EC2_IP"
echo ""

print_info "2. Una vez conectado, ejecuta estos comandos:"
echo "   cd $PROJECT_PATH"
echo "   git pull origin main"
echo ""

print_info "3. Reinicia el servidor:"
echo "   sudo systemctl restart kawii-api"
echo "   # O si usas PM2:"
echo "   pm2 restart kawii-api"
echo "   # O si usas screen/uvicorn directamente:"
echo "   pkill -f uvicorn"
echo "   cd api && python -m uvicorn main_production:app --host 0.0.0.0 --port 8000"
echo ""

print_info "4. Verifica que el servidor esté funcionando:"
echo "   curl http://localhost:8000/docs"
echo ""

print_info "5. Prueba los nuevos endpoints:"
echo "   curl http://localhost:8000/scraping/documentos?limit=5"
echo ""

echo ""
print_warning "IMPORTANTE:"
echo "- Asegúrate de tener tu clave SSH (.pem) en el directorio correcto"
echo "- La clave debe tener permisos 400: chmod 400 TU_CLAVE.pem"
echo "- Si no tienes la clave, descárgala desde la consola de AWS"
echo ""

print_info "¿Necesitas ayuda con alguno de estos pasos?"
echo ""

print_status "¡Listo para desplegar! 🎉" 