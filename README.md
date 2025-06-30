# Kawii Analista Datos - Web Scraper con Hugging Face

Sistema completo de web scraping y análisis de proveedores de marca blanca (B2Broker, Wallester, Sumsub) usando modelos locales de Hugging Face y GPT como respaldo, **ahora con retroalimentación automática desde GPT personalizado**.

## 🚀 Características Principales

### **Web Scraping Inteligente**
- **Scrapers especializados** para B2Broker, Wallester y Sumsub
- **Extracción de precios** con patrones optimizados
- **Detección de términos comerciales** relevantes
- **Almacenamiento en Supabase** con estructura optimizada

### **Análisis con IA Avanzado**
- **Modelos locales Hugging Face** (más rápido, sin costos)
- **GPT-4 como respaldo** para casos complejos
- **Clasificación automática** de módulos
- **Estimación de precios** inteligente
- **Extracción de condiciones comerciales**

### **API FastAPI con Function Calling**
- **Funciones expuestas** que GPT puede invocar automáticamente
- **Endpoints RESTful** para integración
- **Documentación automática** con Swagger/OpenAPI
- **Procesamiento asíncrono** optimizado

### **🤖 Retroalimentación Automática desde GPT Personalizado**
- **Integración directa** con chat de GPT personalizado
- **Guardado automático** de feedback en Supabase
- **Análisis de retroalimentación** en tiempo real
- **Recomendaciones basadas** en feedback acumulado
- **Memoria estratégica** para mejorar decisiones futuras

### **Arquitectura Optimizada**
- **Cache inteligente** para modelos
- **Procesamiento en lote** eficiente
- **Manejo de errores** robusto
- **Logging detallado** para debugging

## 📦 Instalación

### **1. Clonar repositorio**
```bash
git clone <repository-url>
cd kawii-analista-datos
```

### **2. Instalar dependencias**
```bash
pip install -r requirements.txt
```

### **3. Configurar variables de entorno**
```bash
cp env_example.txt .env
# Editar .env con tus credenciales
```

### **4. Verificar instalación**
```bash
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import transformers; print(f'Transformers: {transformers.__version__}')"
```

## 🎯 Uso Rápido

### **1. Iniciar la API FastAPI**
```bash
# Opción 1: Script de inicio
python api/start_server.py

# Opción 2: Directamente
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### **2. Verificar funcionamiento**
```bash
# Estado de salud
curl http://localhost:8000/health

# Documentación
# Abrir http://localhost:8000/docs en el navegador
```

### **3. Analizar texto**
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

### **4. Ejecutar scraping**
```bash
curl -X POST "http://localhost:8000/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "providers": ["b2broker", "wallester", "sumsub"],
    "use_sample_data": true
  }'
```

## 🤖 Integración con GPT Function Calling

### **Configuración Automática**
La API expone funciones que GPT puede invocar automáticamente:

```python
import openai
import aiohttp

# Obtener definiciones de funciones
async def get_function_definitions():
    async with aiohttp.ClientSession() as session:
        async with session.get("http://localhost:8000/function-definitions") as response:
            return await response.json()

# Usar con GPT
functions = await get_function_definitions()
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Analiza este texto de B2Broker"}],
    functions=functions["functions"],
    function_call="auto"
)
```

### **Funciones Disponibles**
- **`analyze_text`**: Análisis de texto individual
- **`analyze_batch`**: Análisis en lote
- **`scrape_providers`**: Web scraping de proveedores
- **`extract_price`**: Extracción específica de precios
- **`get_model_info`**: Información de modelos
- **`get_system_stats`**: Estadísticas del sistema

## 🎯 **NUEVO: Retroalimentación desde GPT Personalizado**

### **Configuración Rápida**
1. **Desplegar API**: `railway up` o `render deploy`
2. **Crear tablas**: Ejecutar `sql_retroalimentacion.sql` en Supabase
3. **Configurar GPT**: Seguir `GUIA_GPT_PERSONALIZADO.md`
4. **Probar integración**: `python ejemplo_retroalimentacion_gpt.py`

### **Funciones de Retroalimentación**
- **`guardar_feedback`**: Guarda retroalimentación automáticamente
- **`obtener_feedback`**: Consulta feedback existente
- **`analizar_feedback_producto`**: Analiza feedback específico
- **`procesar_retroalimentacion`**: Genera recomendaciones

### **Ejemplo de Uso**
```
Usuario en Chat GPT: "El producto Wallet + KYC en Colombia tuvo baja adopción porque el onboarding fue confuso."

GPT automáticamente:
1. Procesa el mensaje
2. Llama a guardar_feedback()
3. Almacena en Supabase
4. Responde: "He guardado tu retroalimentación. ¿Te gustaría que analice el feedback acumulado?"
```

### **Análisis de Retroalimentación**
```bash
# Consultar feedback almacenado
curl "http://localhost:8000/feedback/obtener_feedback/?producto=Wallet%20%2B%20KYC&mercado=Colombia"

# Analizar feedback específico
curl "http://localhost:8000/feedback/analizar_feedback/Wallet%20%2B%20KYC/Colombia"

# Procesar recomendaciones
curl -X POST "http://localhost:8000/feedback/procesar_retroalimentacion/?producto=Wallet%20%2B%20KYC&mercado=Colombia"
```

## 📊 Scripts Principales

### **1. Analizador Optimizado**
```bash
python analizador_optimizado.py --help
python analizador_optimizado.py --test
python analizador_optimizado.py --stats
python analizador_optimizado.py --batch
```

### **2. Analizador GPT**
```bash
python analizador_gpt.py
```

### **3. Modelo de Venta por Niveles**
```bash
python modelo_venta_niveles.py
```

### **4. Cliente de Ejemplo**
```bash
python api/client_example.py
```

### **5. 🆕 Simulador de Retroalimentación GPT**
```bash
python ejemplo_retroalimentacion_gpt.py
```

## 🏗️ Arquitectura del Sistema

```
kawii-analista-datos/
├── api/                          # API FastAPI
│   ├── main.py                   # Servidor principal
│   ├── feedback.py               # 🆕 Endpoints de retroalimentación
│   ├── gpt_integration.py        # Integración GPT
│   ├── client_example.py         # Cliente de ejemplo
│   └── start_server.py           # Script de inicio
├── utils/                        # Utilidades
│   ├── model_manager.py          # Gestor de modelos
│   ├── optimized_analyzer.py     # Analizador optimizado
│   └── extract_price.py          # Extracción de precios
├── modules/                      # Módulos de scraping
│   └── sumsub.py                 # Scraper Sumsub
├── analizador_optimizado.py      # Script principal optimizado
├── analizador_gpt.py             # Script GPT
├── modelo_venta_niveles.py       # Modelo de venta
├── ejemplo_retroalimentacion_gpt.py  # 🆕 Simulador GPT
├── gpt_function_definitions.json # 🆕 Definiciones para GPT
├── sql_retroalimentacion.sql     # 🆕 SQL para retroalimentación
├── GUIA_GPT_PERSONALIZADO.md     # 🆕 Guía de configuración
├── supabase_client.py            # Cliente Supabase
└── requirements.txt              # Dependencias
```

## 🔧 Configuración Avanzada

### **Variables de Entorno**
```env
# Supabase
SUPABASE_URL=tu_url_de_supabase
SUPABASE_KEY=tu_clave_de_supabase

# OpenAI (opcional)
OPENAI_API_KEY=tu_clave_de_openai

# APIs de búsqueda (para análisis estratégico)
PERPLEXITY_API_KEY=tu_clave_perplexity
SERPAPI_KEY=tu_clave_serpapi
BRAVE_API_KEY=tu_clave_brave

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true
API_LOG_LEVEL=info

# Modelos locales
MODEL_CACHE_DIR=./models_cache
USE_LOCAL_MODELS=true
USE_GPT_BACKUP=true
```

## 📚 Documentación Adicional

### **Guías Específicas**
- **[README_ESTRATEGICO.md](README_ESTRATEGICO.md)**: Sistema estratégico completo
- **[GUIA_GPT_PERSONALIZADO.md](GUIA_GPT_PERSONALIZADO.md)**: Configuración de GPT con retroalimentación
- **[README_API.md](README_API.md)**: Documentación completa de la API
- **[README_LR.md](README_LR.md)**: Análisis de grafos LR

### **Scripts de Ejemplo**
- **[ejemplo_uso_estrategico.py](ejemplo_uso_estrategico.py)**: Uso completo del sistema estratégico
- **[ejemplo_retroalimentacion_gpt.py](ejemplo_retroalimentacion_gpt.py)**: Simulación de retroalimentación GPT

## 🎯 Casos de Uso

### **1. Análisis de Mercado Tradicional**
```bash
python analizador_optimizado.py --source b2broker --analyze
```

### **2. 🆕 Análisis Estratégico con Retroalimentación**
```bash
python ejemplo_uso_estrategico.py
```

### **3. 🆕 Retroalimentación desde Chat GPT**
1. Configurar GPT personalizado siguiendo `GUIA_GPT_PERSONALIZADO.md`
2. Conversar naturalmente: "El onboarding en Colombia fue confuso"
3. GPT automáticamente guarda y analiza el feedback

### **4. Análisis de Grafos LR**
```bash
python interfaz_lr.py
```

## 🚀 Próximos Pasos

1. **Configurar GPT personalizado** con retroalimentación automática
2. **Desplegar API** en Railway o Render
3. **Ejecutar análisis estratégico** para tu producto
4. **Probar retroalimentación** desde el chat de GPT
5. **Analizar resultados** y ajustar estrategias

---

**¡Sistema completo de análisis estratégico con retroalimentación automática desde GPT personalizado!** 🚀 