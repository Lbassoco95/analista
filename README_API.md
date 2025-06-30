# API FastAPI con GPT Function Calling

API completa para análisis de proveedores de marca blanca que expone funciones que GPT puede invocar automáticamente usando Function Calling.

## 🚀 Características Principales

### **Integración con GPT Function Calling**
- **Funciones expuestas** que GPT puede invocar automáticamente
- **Definiciones JSON** compatibles con OpenAI Function Calling
- **Respuestas estructuradas** para procesamiento automático
- **Manejo de errores** robusto y informativo

### **Endpoints Principales**
- **`/analyze`**: Análisis de texto con modelos locales y GPT
- **`/analyze-batch`**: Análisis en lote de múltiples textos
- **`/scrape`**: Web scraping de proveedores específicos
- **`/extract-price`**: Extracción específica de precios
- **`/model-info`**: Información de modelos cargados
- **`/stats`**: Estadísticas completas del sistema

### **Funcionalidades Avanzadas**
- **Procesamiento asíncrono** con `asyncio`
- **Cache inteligente** para optimización
- **Validación de datos** con Pydantic
- **Documentación automática** con Swagger/OpenAPI
- **CORS habilitado** para integración web

## 📦 Instalación y Configuración

### **1. Instalar dependencias**
```bash
pip install -r requirements.txt
```

### **2. Configurar variables de entorno**
```bash
cp env_example.txt .env
# Editar .env con tus credenciales
```

### **3. Iniciar el servidor**
```bash
# Opción 1: Usando el script de inicio
python api/start_server.py

# Opción 2: Directamente con uvicorn
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### **4. Verificar funcionamiento**
```bash
# Verificar estado de salud
curl http://localhost:8000/health

# Ver documentación
# Abrir http://localhost:8000/docs en el navegador
```

## 🎯 Uso de la API

### **Endpoints Principales**

#### **1. Análisis de Texto**
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "B2Broker offers white label solutions for crypto exchanges. Setup fee starts at $50,000.",
    "source": "B2Broker",
    "use_local_models": true,
    "use_gpt_backup": true
  }'
```

#### **2. Análisis en Lote**
```bash
curl -X POST "http://localhost:8000/analyze-batch" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      {"text": "Sumsub KYC services cost $0.50 per verification", "source": "Sumsub"},
      {"text": "Wallester wallet solution costs $2,500 monthly", "source": "Wallester"}
    ],
    "use_local_models": true,
    "use_gpt_backup": true
  }'
```

#### **3. Scraping de Proveedores**
```bash
curl -X POST "http://localhost:8000/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "providers": ["b2broker", "wallester", "sumsub"],
    "use_sample_data": false
  }'
```

#### **4. Extracción de Precios**
```bash
curl -X POST "http://localhost:8000/extract-price" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Monthly subscription costs $2,500 with setup fee of $10,000",
    "currency": "USD"
  }'
```

#### **5. Información de Modelos**
```bash
curl -X GET "http://localhost:8000/model-info"
```

#### **6. Estadísticas del Sistema**
```bash
curl -X GET "http://localhost:8000/stats"
```

#### **7. Definiciones de Funciones para GPT**
```bash
curl -X GET "http://localhost:8000/function-definitions"
```

## 🤖 Integración con GPT Function Calling

### **Configuración para GPT**

La API expone definiciones de funciones que GPT puede usar automáticamente:

```python
import openai
import json

# Obtener definiciones de funciones
async def get_function_definitions():
    async with aiohttp.ClientSession() as session:
        async with session.get("http://localhost:8000/function-definitions") as response:
            return await response.json()

# Configurar GPT con las funciones
functions = await get_function_definitions()

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {
            "role": "user",
            "content": "Analiza este texto de B2Broker y extrae el precio y clasificación del módulo"
        }
    ],
    functions=functions["functions"],
    function_call="auto"
)
```

### **Funciones Disponibles para GPT**

#### **1. analyze_text**
```json
{
  "name": "analyze_text",
  "description": "Analizar un texto usando modelos locales y/o GPT",
  "parameters": {
    "type": "object",
    "properties": {
      "text": {"type": "string", "description": "Texto a analizar"},
      "source": {"type": "string", "description": "Fuente del texto"},
      "use_local_models": {"type": "boolean", "default": true},
      "use_gpt_backup": {"type": "boolean", "default": true}
    },
    "required": ["text", "source"]
  }
}
```

#### **2. analyze_batch**
```json
{
  "name": "analyze_batch",
  "description": "Analizar múltiples textos en lote",
  "parameters": {
    "type": "object",
    "properties": {
      "texts": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "text": {"type": "string"},
            "source": {"type": "string"}
          }
        }
      },
      "use_local_models": {"type": "boolean", "default": true},
      "use_gpt_backup": {"type": "boolean", "default": true}
    },
    "required": ["texts"]
  }
}
```

#### **3. scrape_providers**
```json
{
  "name": "scrape_providers",
  "description": "Realizar web scraping de proveedores",
  "parameters": {
    "type": "object",
    "properties": {
      "providers": {
        "type": "array",
        "items": {"type": "string"},
        "enum": ["b2broker", "wallester", "sumsub"]
      },
      "use_sample_data": {"type": "boolean", "default": false}
    },
    "required": ["providers"]
  }
}
```

#### **4. extract_price**
```json
{
  "name": "extract_price",
  "description": "Extraer precio específico de un texto",
  "parameters": {
    "type": "object",
    "properties": {
      "text": {"type": "string", "description": "Texto del que extraer precio"},
      "currency": {"type": "string", "enum": ["USD", "EUR", "GBP"]}
    },
    "required": ["text"]
  }
}
```

#### **5. get_model_info**
```json
{
  "name": "get_model_info",
  "description": "Obtener información de modelos cargados",
  "parameters": {
    "type": "object",
    "properties": {
      "model_type": {
        "type": "string",
        "enum": ["classification", "embedding", "summarization"]
      }
    }
  }
}
```

#### **6. get_system_stats**
```json
{
  "name": "get_system_stats",
  "description": "Obtener estadísticas del sistema",
  "parameters": {
    "type": "object",
    "properties": {}
  }
}
```

## 📊 Respuestas de la API

### **Formato de Respuesta Estándar**
```json
{
  "success": true,
  "data": {
    "clasificacion_modulo": "White Label Solution",
    "precio_estimado": "$50,000",
    "condiciones_comerciales": {
      "setup_fee": "$50,000",
      "monthly_cost": "$5,000",
      "transaction_fees": "No especificado"
    },
    "confianza_analisis": "alta",
    "analysis_method": "local_models",
    "fuente": "B2Broker",
    "timestamp": "2024-01-15T10:30:00"
  },
  "timestamp": "2024-01-15T10:30:00",
  "processing_time": 0.85
}
```

### **Formato de Error**
```json
{
  "success": false,
  "error": "Error description",
  "details": "Additional error details",
  "timestamp": "2024-01-15T10:30:00"
}
```

## 🔧 Cliente Python

### **Uso del Cliente de Ejemplo**
```python
import asyncio
from api.client_example import APIClient

async def main():
    async with APIClient() as client:
        # Analizar texto
        result = await client.analyze_text(
            text="B2Broker offers comprehensive white label solutions...",
            source="B2Broker"
        )
        
        if result["success"]:
            print(f"Clasificación: {result['data']['clasificacion_modulo']}")
            print(f"Precio: {result['data']['precio_estimado']}")

# Ejecutar
asyncio.run(main())
```

### **Ejecutar Ejemplos**
```bash
# Ejecutar ejemplos del cliente
python api/client_example.py

# Ejecutar ejemplo de GPT Function Calling
python api/gpt_integration.py
```

## 📈 Monitoreo y Logging

### **Endpoints de Monitoreo**
- **`/health`**: Estado de salud de la API y componentes
- **`/stats`**: Estadísticas completas del sistema
- **`/model-info`**: Información de modelos cargados

### **Logging Configurado**
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### **Métricas Disponibles**
- Tiempo de procesamiento por request
- Uso de memoria de modelos
- Estadísticas de cache
- Métodos de análisis utilizados
- Errores y excepciones

## 🛠️ Configuración Avanzada

### **Variables de Entorno**
```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true
API_LOG_LEVEL=info

# Supabase
SUPABASE_URL=tu_url_de_supabase
SUPABASE_KEY=tu_clave_de_supabase

# OpenAI (opcional)
OPENAI_API_KEY=tu_clave_de_openai

# Modelos locales
MODEL_CACHE_DIR=./models_cache
USE_LOCAL_MODELS=true
USE_GPT_BACKUP=true
```

### **Configuración de CORS**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configurar según necesidades
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### **Rate Limiting (Opcional)**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/analyze")
@limiter.limit("10/minute")
async def analyze_text(request: Request, ...):
    # Tu código aquí
```

## 🔍 Troubleshooting

### **Problemas Comunes**

1. **Error de conexión a Supabase**:
   ```bash
   # Verificar credenciales
   curl http://localhost:8000/health
   ```

2. **Modelos no cargan**:
   ```bash
   # Verificar información de modelos
   curl http://localhost:8000/model-info
   ```

3. **Error de dependencias**:
   ```bash
   # Reinstalar dependencias
   pip install -r requirements.txt --force-reinstall
   ```

4. **Puerto ocupado**:
   ```bash
   # Cambiar puerto
   uvicorn api.main:app --port 8001
   ```

### **Debugging**
```bash
# Modo verbose
uvicorn api.main:app --log-level debug

# Ver logs detallados
tail -f logs/api.log
```

## 🚀 Despliegue

### **Docker (Recomendado)**
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **Docker Compose**
```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
    volumes:
      - ./models_cache:/app/models_cache
```

### **Nginx (Producción)**
```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📚 Documentación Adicional

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/docs/openapi.json`

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama para feature
3. Implementar cambios
4. Agregar tests si es necesario
5. Enviar Pull Request

---

**Nota**: Esta API está diseñada para ser completamente compatible con GPT Function Calling, permitiendo que GPT invoque automáticamente las funciones para análisis de proveedores de marca blanca. 