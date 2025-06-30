# Sistema Inteligente de Análisis de Proveedores LATAM

Sistema completo que implementa la lógica escalable propuesta con scraping inteligente, validación cruzada, almacenamiento en Pinecone y chat con GPT.

## 🧠 **Arquitectura Inteligente Implementada**

### **✅ Checklist Completado**

- [x] **Ajustar scrapers para filtrar solo LATAM/México**
- [x] **Configurar Pinecone y guardar embeddings + metadata**
- [x] **Definir y normalizar el esquema de metadata**
- [x] **Integrar LangChain para chat con GPT y búsqueda en Pinecone**
- [x] **Enriquecer metadata automáticamente tras cada scraping**
- [x] **Permitir consultas avanzadas y filtradas**
- [x] **Documentar el flujo y actualizar el README**

---

## 🏗️ **Estructura Modular Implementada**

### **1. Scrapers Inteligentes**
```
modules/
├── sumsub.py                    # Scraper con filtro LATAM/México
└── [otros_scrapers.py]          # Escalable para nuevos proveedores
```

### **2. Gestores de Datos**
```
utils/
├── extract_price.py             # Extracción de precios y metadata LATAM
├── pinecone_manager.py          # Gestor de Pinecone con embeddings
├── chat_gpt_manager.py          # Chat inteligente con GPT
└── model_manager.py             # Gestor de modelos locales
```

### **3. Sistema Principal**
```
scraper_inteligente.py           # Scraper con búsqueda semi-dirigida
api/main.py                      # API FastAPI con Function Calling
```

---

## 🔄 **Flujo de Scraping en Capas**

### **Etapa 1: Búsqueda Semi-Dirigida**
```python
# Templates de búsqueda por módulo
search_templates = {
    'wallet': [
        'white label crypto wallet pricing LATAM',
        'crypto wallet API cost Mexico',
        'digital wallet solution pricing Argentina'
    ],
    'kyc': [
        'KYC verification pricing LATAM',
        'identity verification cost Mexico'
    ]
    # ... más módulos
}
```

### **Etapa 2: Validación Cruzada**
```python
# Validación automática con GPT
validation = scraper.validar_con_gpt(text1, text2, module)
if validation['confidence'] > 70:
    metadata['validado_cruzado'] = True
```

### **Etapa 3: Análisis GPT Contextual**
```python
# Análisis inteligente de precios y condiciones
gpt_analysis = await chat_manager.analyze_provider_comparison(
    providers=['Sumsub', 'B2Broker'],
    module='KYC/KYB',
    country='México'
)
```

### **Etapa 4: Scoring de Confiabilidad**
```python
# Metadata enriquecida con scoring
metadata = {
    'pais': 'México',
    'region': 'México',
    'moneda': 'USD',
    'confianza': 85.0,
    'validado_cruzado': True,
    'fuente_url': 'https://sumsub.com/pricing/',
    'tipo_fuente': 'web'
}
```

### **Etapa 5: Almacenamiento Inteligente**
```python
# Almacenamiento en Pinecone con embeddings
pinecone_manager.validate_and_store(text, metadata)
```

---

## 🎯 **Funcionalidades Implementadas**

### **1. Filtrado LATAM/México**
- ✅ Detección automática de países LATAM
- ✅ Filtrado por región (México vs LATAM)
- ✅ Extracción de monedas locales (MXN, ARS, COP, etc.)
- ✅ Validación geográfica automática

### **2. Búsqueda Semi-Dirigida**
- ✅ Templates de búsqueda por módulo
- ✅ Búsqueda específica por país
- ✅ URLs dinámicas basadas en consultas
- ✅ Filtrado inteligente de resultados

### **3. Validación Cruzada**
- ✅ Validación automática con GPT
- ✅ Comparación semántica de datos
- ✅ Scoring de confiabilidad
- ✅ Múltiples fuentes por dato

### **4. Almacenamiento Pinecone**
- ✅ Embeddings automáticos con SentenceTransformers
- ✅ Metadata estructurada y indexada
- ✅ Búsqueda semántica inteligente
- ✅ Filtros avanzados por país/módulo

### **5. Chat Inteligente**
- ✅ Integración LangChain + GPT
- ✅ Contexto de Pinecone automático
- ✅ Análisis comparativo de proveedores
- ✅ Insights del mercado LATAM

---

## 🚀 **Uso del Sistema**

### **1. Configuración Inicial**
```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp env_example.txt .env
# Editar .env con tus credenciales

# Verificar configuración
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('Configuración OK')"
```

### **2. Ejecutar Scraper Inteligente**
```bash
# Scraper completo con validación cruzada
python scraper_inteligente.py

# O desde Python
from scraper_inteligente import ScraperInteligente
scraper = ScraperInteligente()
results = scraper.scrape_todos_modulos(['México', 'Argentina'])
```

### **3. Usar Chat Inteligente**
```python
from utils.chat_gpt_manager import get_chat_gpt_manager
from utils.pinecone_manager import get_pinecone_manager

# Inicializar gestores
chat_manager = get_chat_gpt_manager()
pinecone_manager = get_pinecone_manager()

# Chat con contexto de Pinecone
response = await chat_manager.chat_with_context(
    query="¿Cuáles son los mejores precios de KYC en México?",
    pinecone_manager=pinecone_manager,
    filters={'pais': 'México', 'modulo': 'KYC/KYB'}
)
```

### **4. Consultas Avanzadas**
```python
# Búsqueda por módulo y país
results = pinecone_manager.search_by_module('KYC/KYB', 'México')

# Comparación de proveedores
comparison = await chat_manager.analyze_provider_comparison(
    providers=['Sumsub', 'B2Broker'],
    module='KYC/KYB',
    country='México'
)

# Insights del mercado
insights = await chat_manager.get_market_insights(
    country='México',
    module='wallet'
)
```

---

## 📊 **Esquema de Metadata Implementado**

### **Campos Principales**
```json
{
  "proveedor": "Sumsub",
  "pais": "México",
  "region": "México",
  "modulo": "KYC/KYB",
  "moneda": "USD",
  "precio": "$0.50",
  "fecha_publicacion": "2024-01-15",
  "confianza": 85.0,
  "validado_cruzado": true,
  "fuente_url": "https://sumsub.com/pricing/",
  "tipo_fuente": "web",
  "timestamp": "2024-01-15T10:30:00"
}
```

### **Campos de Validación**
```json
{
  "cross_reference": {
    "same_module": true,
    "same_price": true,
    "same_country": true,
    "confidence": 85.0
  },
  "gpt_validation": {
    "validated": true,
    "confidence": 92.0,
    "reason": "Precios y condiciones coinciden"
  }
}
```

---

## 🔧 **Configuración Avanzada**

### **Variables de Entorno Clave**
```env
# Pinecone
PINECONE_API_KEY=tu_api_key_de_pinecone
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX=proveedores-latam

# OpenAI (para validación cruzada)
OPENAI_API_KEY=tu_clave_de_openai

# Scraper Inteligente
SCRAPER_DELAY_MIN=1
SCRAPER_DELAY_MAX=3
CROSS_VALIDATION_MIN_CONFIDENCE=70
GPT_VALIDATION_ENABLED=true
```

### **Templates de Búsqueda Personalizables**
```python
# Agregar nuevos módulos
scraper.search_templates['nuevo_modulo'] = [
    'nuevo módulo pricing LATAM',
    'nuevo módulo cost Mexico'
]

# Agregar nuevos países
scraper.latam_countries.append('Nuevo País')
```

---

## 📈 **Métricas y Monitoreo**

### **Estadísticas Disponibles**
```python
# Estadísticas de Pinecone
stats = pinecone_manager.get_statistics()
print(f"Total vectores: {stats['total_vectors']}")
print(f"Distribución por país: {stats['country_distribution']}")
print(f"Distribución por módulo: {stats['module_distribution']}")

# Estadísticas del scraper
scraper_stats = {
    'total_stored': 150,
    'validated': 120,
    'by_module': {'wallet': 30, 'kyc': 45, 'trading': 25},
    'by_country': {'México': 50, 'Argentina': 40, 'Colombia': 30}
}
```

---

## 🎯 **Casos de Uso Implementados**

### **1. Análisis de Precios por País**
```python
# Buscar precios de KYC en México
results = pinecone_manager.search_by_module('KYC/KYB', 'México')
analysis = await chat_manager.chat_with_context(
    "Analiza los precios de KYC en México",
    pinecone_manager,
    filters={'pais': 'México', 'modulo': 'KYC/KYB'}
)
```

### **2. Comparación de Proveedores**
```python
# Comparar Sumsub vs B2Broker en wallet
comparison = await chat_manager.analyze_provider_comparison(
    providers=['Sumsub', 'B2Broker'],
    module='wallet',
    country='Argentina'
)
```

### **3. Insights del Mercado**
```python
# Obtener tendencias del mercado LATAM
insights = await chat_manager.get_market_insights(
    country='México',
    module='trading'
)
```

---

## 🔍 **Troubleshooting**

### **Problemas Comunes**

1. **Error de Pinecone**:
   ```bash
   # Verificar credenciales
   python -c "from utils.pinecone_manager import get_pinecone_manager; pm = get_pinecone_manager(); print(pm.get_statistics())"
   ```

2. **Error de OpenAI**:
   ```bash
   # Verificar API key
   python -c "import openai; openai.api_key = 'tu_key'; print('OK')"
   ```

3. **Scraper no encuentra datos**:
   ```bash
   # Verificar filtros LATAM
   python scraper_inteligente.py --debug
   ```

---

## 🚀 **Próximos Pasos**

### **Optimizaciones Futuras**
1. **Integración con SerpAPI** para búsquedas más precisas
2. **Fine-tuning de modelos** para dominio específico
3. **Dashboard en tiempo real** con Streamlit
4. **Alertas automáticas** de cambios de precios
5. **API de terceros** para datos adicionales

### **Escalabilidad**
- ✅ Módulos configurables
- ✅ Países extensibles
- ✅ Proveedores dinámicos
- ✅ Templates personalizables
- ✅ Validación automática

---

## 📚 **Documentación Adicional**

- **[API FastAPI](README_API.md)**: Documentación de la API
- **[Optimizaciones](README_OPTIMIZED.md)**: Detalles técnicos
- **[Dashboard](dashboard_config.md)**: Configuración de dashboards

---

**✅ Sistema completamente implementado y funcional para análisis inteligente de proveedores LATAM con scraping, validación cruzada, Pinecone y chat GPT.** 