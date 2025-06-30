# 🤖 Analizador LR Completo

## Descripción

El **Analizador LR Completo** implementa el flujo de análisis de grafos LR (Left-to-Right) para el análisis inteligente de proveedores de servicios financieros en LATAM y México. El sistema automatiza todo el proceso desde el scraping hasta la consulta interactiva.

## 🔄 Flujo LR Implementado

```
A[Scraping con Playwright/Apify] 
    ↓
B[Procesamiento con LangChain] 
    ↓
C[Generación de Embeddings con OpenAI] 
    ↓
D[Almacenamiento en Pinecone] 
    ↓
E[Consulta vía LLM o interfaz chatbot]
```

### Etapas del Flujo

#### **A. Scraping Inteligente**
- Búsqueda semi-dirigida con templates específicos
- Filtros geográficos para LATAM/México
- Extracción de metadata automática
- Validación cruzada con GPT
- Pausas inteligentes para evitar bloqueos

#### **B. Procesamiento con LangChain**
- Extracción estructurada de información
- Análisis de precios y servicios
- Enriquecimiento automático de metadata
- Validación de datos cruzados
- Clasificación por módulos y regiones

#### **C. Generación de Embeddings**
- Embeddings con OpenAI (text-embedding-ada-002)
- Optimización para búsqueda semántica
- Metadata enriquecida para filtros
- Validación de calidad de embeddings

#### **D. Almacenamiento en Pinecone**
- Índice vectorial optimizado
- Metadata indexada para consultas rápidas
- Estadísticas automáticas
- Limpieza de datos antiguos

#### **E. Consulta Inteligente**
- Chat con contexto de Pinecone
- Análisis comparativo de proveedores
- Insights de mercado automáticos
- Recomendaciones personalizadas

## 🚀 Instalación y Configuración

### 1. Requisitos Previos

```bash
# Clonar el repositorio
git clone <repository-url>
cd kawii-analista-datos

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configuración de Variables de Entorno

Crear archivo `.env` basado en `env_example.txt`:

```bash
# OpenAI
OPENAI_API_KEY=tu_api_key_de_openai

# Pinecone
PINECONE_API_KEY=tu_api_key_de_pinecone
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX=proveedores-latam

# Configuración del Scraper
SCRAPER_DELAY=2
SCRAPER_MAX_RETRIES=3
SCRAPER_TIMEOUT=30
SCRAPER_USER_AGENT=Mozilla/5.0...

# Configuración de Análisis
ANALYSIS_BATCH_SIZE=10
ANALYSIS_ENABLE_VALIDATION=true
ANALYSIS_ENABLE_METADATA_ENRICHMENT=true
```

### 3. Configuración de Pinecone

```python
# El sistema creará automáticamente el índice si no existe
# Configuración recomendada:
# - Dimension: 384 (para all-MiniLM-L6-v2)
# - Metric: cosine
# - Metadata indexed: ['proveedor', 'pais', 'region', 'modulo', 'moneda', 'fecha']
```

## 📖 Uso

### 1. Interfaz de Usuario (Recomendado)

```bash
python interfaz_lr.py
```

La interfaz proporciona:
- ✅ Ejecución del flujo LR completo
- 💬 Consultas interactivas
- 📋 Gestión de proveedores
- 📊 Visualización de resultados
- 📁 Gestión de archivos guardados

### 2. Uso Programático

```python
import asyncio
from analizador_lr_completo import AnalizadorLRCompleto

async def main():
    # Inicializar analizador
    analizador = AnalizadorLRCompleto()
    
    # Lista de proveedores a analizar
    proveedores = ["Sumsub", "Jumio", "Onfido", "Veriff"]
    
    # Ejecutar flujo completo
    resultados = await analizador.ejecutar_flujo_completo(proveedores)
    
    # Guardar resultados
    analizador.guardar_resultados(resultados)
    
    # Consulta interactiva
    respuesta = await analizador.consulta_interactiva(
        "¿Cuáles son los mejores proveedores de KYC en México?"
    )
    print(respuesta)

if __name__ == "__main__":
    asyncio.run(main())
```

### 3. Ejecución Directa

```bash
python analizador_lr_completo.py
```

## 🏗️ Arquitectura del Sistema

### Componentes Principales

#### **AnalizadorLRCompleto** (`analizador_lr_completo.py`)
- Orquestador principal del flujo LR
- Coordina todas las etapas del proceso
- Manejo de errores y logging
- Generación de estadísticas

#### **ScraperInteligente** (`scraper_inteligente.py`)
- Scraping con búsqueda semi-dirigida
- Templates específicos por módulo
- Validación cruzada con GPT
- Filtros geográficos LATAM

#### **PineconeManager** (`utils/pinecone_manager.py`)
- Gestión de embeddings y metadata
- Búsqueda semántica optimizada
- Estadísticas automáticas
- Limpieza de datos

#### **ChatGPTManager** (`utils/chat_gpt_manager.py`)
- Chat con contexto de Pinecone
- Análisis comparativo
- Insights de mercado
- Consultas estructuradas

#### **InterfazLR** (`interfaz_lr.py`)
- Interfaz de usuario amigable
- Gestión de proveedores
- Visualización de resultados
- Consultas interactivas

### Flujo de Datos

```
1. Proveedores → ScraperInteligente
2. Datos Raw → LangChain Processing
3. Datos Procesados → OpenAI Embeddings
4. Embeddings + Metadata → Pinecone Storage
5. Consultas → ChatGPT + Pinecone Context
```

## 📊 Funcionalidades

### Análisis de Proveedores
- ✅ Scraping automático de información
- ✅ Extracción de precios y servicios
- ✅ Comparación entre proveedores
- ✅ Análisis de tendencias de mercado
- ✅ Recomendaciones personalizadas

### Consultas Inteligentes
- 💬 Chat natural con contexto
- 🔍 Búsqueda semántica avanzada
- 📈 Análisis comparativo automático
- 🎯 Recomendaciones específicas por región
- 📊 Insights de mercado en tiempo real

### Gestión de Datos
- 💾 Almacenamiento vectorial optimizado
- 🔄 Actualización automática de datos
- 🧹 Limpieza de datos antiguos
- 📈 Estadísticas automáticas
- 🔍 Búsqueda por filtros múltiples

## 🎯 Casos de Uso

### 1. Análisis de Mercado LATAM
```python
# Ejecutar análisis completo
resultados = await analizador.ejecutar_flujo_completo([
    "Sumsub", "Jumio", "Onfido", "Veriff", "IDnow"
])

# Consultar insights
respuesta = await analizador.consulta_interactiva(
    "¿Qué tendencias observas en el mercado de KYC en LATAM?"
)
```

### 2. Comparación de Proveedores
```python
# Comparar proveedores específicos
respuesta = await analizador.consulta_interactiva(
    "Compara los precios y características de Sumsub vs Jumio para México"
)
```

### 3. Recomendaciones por Región
```python
# Obtener recomendaciones específicas
respuesta = await analizador.consulta_interactiva(
    "Recomienda los mejores proveedores de white label wallet para Argentina"
)
```

### 4. Análisis de Precios
```python
# Analizar estructura de precios
respuesta = await analizador.consulta_interactiva(
    "¿Cuál es el rango de precios para servicios de KYC en Colombia?"
)
```

## 📈 Monitoreo y Estadísticas

### Logs Automáticos
- 📝 Logs detallados en `analizador_lr.log`
- ⏱️ Tiempos de ejecución por etapa
- ❌ Errores y excepciones
- 📊 Estadísticas de rendimiento

### Métricas del Sistema
- 🔢 Total de proveedores analizados
- 📊 Tasa de éxito por etapa
- 💾 Datos almacenados en Pinecone
- 🎯 Calidad de embeddings
- ⚡ Tiempo de respuesta de consultas

### Archivos de Resultados
- 📄 JSON con resultados completos
- 📊 Estadísticas por etapa
- 🔍 Datos de contexto utilizados
- 📈 Insights generados

## 🔧 Configuración Avanzada

### Personalización de Templates
```python
# Modificar templates de búsqueda
scraper.search_templates['kyc'] = [
    'KYC verification pricing LATAM',
    'identity verification cost Mexico',
    # Agregar más templates...
]
```

### Configuración de Embeddings
```python
# Cambiar modelo de embeddings
pinecone_manager.embedding_model = SentenceTransformer('all-mpnet-base-v2')
```

### Filtros Personalizados
```python
# Aplicar filtros específicos
filtros = {
    'pais': 'México',
    'modulo': 'kyc',
    'precio_min': 100,
    'precio_max': 1000
}
```

## 🚨 Troubleshooting

### Problemas Comunes

#### **Error de API Keys**
```bash
# Verificar variables de entorno
echo $OPENAI_API_KEY
echo $PINECONE_API_KEY
```

#### **Error de Conexión Pinecone**
```python
# Verificar configuración
pinecone.init(api_key=api_key, environment=environment)
print(pinecone.list_indexes())
```

#### **Scraping Bloqueado**
```python
# Ajustar configuración
config['delay_between_batches'] = 5  # Aumentar delay
config['max_retries'] = 5  # Aumentar reintentos
```

#### **Memoria Insuficiente**
```python
# Reducir batch size
config['batch_size'] = 5  # Reducir tamaño de lote
```

### Logs y Debugging
```bash
# Ver logs en tiempo real
tail -f analizador_lr.log

# Verificar archivos de resultados
ls -la resultados_lr_*.json
```

## 🔮 Próximos Pasos

### Mejoras Planificadas
- 🎨 Interfaz web con Streamlit
- 📊 Dashboard de métricas en tiempo real
- 🤖 Integración con más LLMs
- 🔄 Actualización automática de datos
- 📱 API REST para integración externa

### Optimizaciones
- ⚡ Paralelización de scraping
- 🧠 Modelos de embeddings más avanzados
- 📈 Análisis predictivo de precios
- 🔍 Búsqueda más inteligente
- 💾 Optimización de almacenamiento

## 📞 Soporte

### Documentación Adicional
- 📖 [README_INTELIGENTE.md](README_INTELIGENTE.md) - Sistema inteligente
- 📖 [README_API.md](README_API.md) - API con FastAPI
- 📖 [README_OPTIMIZED.md](README_OPTIMIZED.md) - Versión optimizada

### Archivos de Configuración
- ⚙️ `env_example.txt` - Variables de entorno
- 📋 `requirements.txt` - Dependencias
- 🔧 `dashboard_config.md` - Configuración de dashboard

### Estructura del Proyecto
```
kawii-analista-datos/
├── analizador_lr_completo.py    # Orquestador principal
├── interfaz_lr.py              # Interfaz de usuario
├── scraper_inteligente.py      # Scraper inteligente
├── utils/                      # Utilidades
│   ├── pinecone_manager.py     # Gestor Pinecone
│   ├── chat_gpt_manager.py     # Gestor GPT
│   └── extract_price.py        # Extracción de precios
├── modules/                    # Módulos específicos
│   └── sumsub.py              # Scraper Sumsub
└── README_LR.md               # Esta documentación
```

---

**¡El Analizador LR Completo está listo para revolucionar tu análisis de proveedores LATAM! 🚀** 