#!/bin/bash

# Script de despliegue para Google Cloud
# Autor: Sistema de Retroalimentación GPT
# Fecha: $(date)

set -e  # Salir si hay algún error

echo "🚀 INICIANDO DESPLIEGUE EN GOOGLE CLOUD"
echo "========================================"

# Variables de configuración
PROJECT_ID="k-awiil"  # Proyecto K'awiil
REGION="us-central1"
SERVICE_NAME="kawii-feedback-api"

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

# Verificar que gcloud esté instalado
if ! command -v gcloud &> /dev/null; then
    print_error "Google Cloud SDK no está instalado. Instálalo desde: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Verificar que estés autenticado
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    print_warning "No estás autenticado en Google Cloud. Ejecutando autenticación..."
    gcloud auth login
fi

# Verificar que el proyecto esté configurado
if [ "$PROJECT_ID" = "tu-proyecto-id" ]; then
    print_error "Debes configurar tu PROJECT_ID en el script"
    echo "Ejecuta: gcloud projects list"
    echo "Y actualiza la variable PROJECT_ID en este script"
    exit 1
fi

# Configurar proyecto
print_status "Configurando proyecto: $PROJECT_ID"
gcloud config set project $PROJECT_ID

# Habilitar APIs necesarias
print_status "Habilitando APIs necesarias..."
gcloud services enable appengine.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com

echo ""
echo "📋 OPCIONES DE DESPLIEGUE:"
echo "1. Google App Engine (recomendado para APIs)"
echo "2. Google Cloud Run (más flexible)"
echo "3. Google Compute Engine (máximo control)"
echo ""

read -p "Selecciona una opción (1-3): " choice

case $choice in
    1)
        echo ""
        print_status "Desplegando en Google App Engine..."
        
        # Verificar que app.yaml existe
        if [ ! -f "app.yaml" ]; then
            print_error "app.yaml no encontrado"
            exit 1
        fi
        
        # Desplegar en App Engine
        gcloud app deploy app.yaml --quiet
        
        # Obtener URL
        APP_URL=$(gcloud app browse --no-launch-browser)
        print_status "Aplicación desplegada en: $APP_URL"
        ;;
        
    2)
        echo ""
        print_status "Desplegando en Google Cloud Run..."
        
        # Construir y desplegar imagen
        gcloud run deploy $SERVICE_NAME \
            --source . \
            --platform managed \
            --region $REGION \
            --allow-unauthenticated \
            --memory 1Gi \
            --cpu 1 \
            --max-instances 10 \
            --quiet
        
        # Obtener URL
        RUN_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")
        print_status "Aplicación desplegada en: $RUN_URL"
        ;;
        
    3)
        echo ""
        print_warning "Despliegue en Compute Engine requiere configuración manual"
        print_status "Creando imagen de Docker..."
        
        # Construir imagen
        docker build -t gcr.io/$PROJECT_ID/$SERVICE_NAME .
        
        # Subir a Container Registry
        docker push gcr.io/$PROJECT_ID/$SERVICE_NAME
        
        print_status "Imagen subida a: gcr.io/$PROJECT_ID/$SERVICE_NAME"
        print_warning "Configura una instancia de Compute Engine manualmente"
        ;;
        
    *)
        print_error "Opción inválida"
        exit 1
        ;;
esac

echo ""
print_status "Despliegue completado exitosamente!"
echo ""
echo "🔧 PRÓXIMOS PASOS:"
echo "1. Configura las variables de entorno en Google Cloud Console"
echo "2. Prueba los endpoints de la API"
echo "3. Configura el dominio personalizado (opcional)"
echo "4. Configura SSL/TLS (automático en App Engine/Cloud Run)"
echo ""
echo "📊 MONITOREO:"
echo "- Google Cloud Console > Logging"
echo "- Google Cloud Console > Monitoring"
echo "- Google Cloud Console > Error Reporting"
echo ""
echo "🔗 DOCUMENTACIÓN:"
echo "- API Docs: [URL]/docs"
echo "- ReDoc: [URL]/redoc"
echo ""
print_status "¡Sistema listo para producción! 🎉" 