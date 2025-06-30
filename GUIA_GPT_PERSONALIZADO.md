# 🤖 Guía de Configuración del GPT Personalizado con Retroalimentación

## 📋 Descripción

Esta guía te ayudará a configurar un **GPT personalizado** que puede recibir retroalimentación directamente desde el chat y almacenarla automáticamente en tu base de datos usando **Function Calling**.

## 🎯 Funcionalidades del GPT Personalizado

### ✅ **Capacidades Principales**
- **Análisis de Mercado**: Búsqueda inteligente y análisis estratégico
- **Estrategia Comercial**: Generación de estrategias y pricing
- **Planificación de Producto**: Planes de lanzamiento completos
- **Retroalimentación Automática**: Guarda feedback desde el chat
- **Análisis Histórico**: Consulta y analiza feedback acumulado

### 🔄 **Flujo de Retroalimentación**
```
Usuario en Chat GPT → GPT Procesa → Función guardar_feedback → API → Supabase
```

## 🚀 **PASO 1: Preparar la API**

### 1.1 **Desplegar la API**
```bash
# Opción 1: Local (desarrollo)
cd api
uvicorn main:app --host 0.0.0.0 --port 8000

# Opción 2: Railway (recomendado)
railway login
railway init
railway up

# Opción 3: Render
# Crear nuevo Web Service en Render
# Conectar repositorio y configurar variables de entorno
```

### 1.2 **Verificar Endpoints**
```bash
# Verificar que la API esté funcionando
curl http://tu-api-url.com/health

# Verificar endpoint de feedback
curl http://tu-api-url.com/feedback/estadisticas/
```

## 🗄️ **PASO 2: Configurar Supabase**

### 2.1 **Ejecutar SQL de Retroalimentación**
1. Ve a tu proyecto de Supabase
2. Abre el **SQL Editor**
3. Copia y ejecuta el contenido de `sql_retroalimentacion.sql`

### 2.2 **Verificar Tablas Creadas**
```sql
-- Verificar que las tablas se crearon
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name LIKE '%retroalimentacion%';

-- Verificar datos de ejemplo
SELECT * FROM retroalimentacion LIMIT 5;
```

## 🤖 **PASO 3: Crear GPT Personalizado**

### 3.1 **Acceder a GPTs**
1. Ve a [https://chat.openai.com/gpts](https://chat.openai.com/gpts)
2. Haz clic en **"Create"** o **"Crear"**

### 3.2 **Configurar Información Básica**
```
Nombre: "Asistente Estratégico de Mercado"
Descripción: "Especialista en análisis de mercado, estrategia comercial y planificación de productos para LATAM"
Instrucciones: [Ver sección 3.3]
```

### 3.3 **Configurar Instrucciones del Sistema**
```markdown
Eres un asistente estratégico especializado en análisis de mercado, estrategia comercial y planificación de productos para LATAM. 

**Tus capacidades principales:**
- Análisis completo de mercados usando múltiples fuentes
- Generación de estrategias comerciales y pricing
- Planificación de lanzamientos de productos
- Procesamiento automático de retroalimentación de usuarios

**Instrucciones importantes:**
1. Siempre analiza el contexto completo antes de responder
2. Cuando recibas retroalimentación, guárdala automáticamente usando guardar_feedback
3. Proporciona análisis basados en datos y múltiples fuentes
4. Genera recomendaciones accionables y específicas
5. Mantén un historial de análisis y retroalimentación
6. Usa el análisis de retroalimentación para mejorar futuras estrategias
7. Considera el contexto geográfico y regulatorio de cada mercado

**Ejemplos de uso:**
- "Queremos lanzar wallet crypto en México"
- "El onboarding en Colombia fue confuso"
- "Necesitamos estrategia de pricing para KYC en Perú"
```

### 3.4 **Configurar Funciones (Function Calling)**

#### **Función 1: guardar_feedback**
```json
{
  "name": "guardar_feedback",
  "description": "Guarda una retroalimentación de producto o estrategia comercial desde el chat de GPT",
  "parameters": {
    "type": "object",
    "properties": {
      "producto": {
        "type": "string",
        "description": "Nombre del producto o solución evaluada"
      },
      "mercado": {
        "type": "string",
        "description": "País o sector donde se aplicó"
      },
      "observacion": {
        "type": "string",
        "description": "Retroalimentación o aprendizaje clave"
      },
      "categoria": {
        "type": "string",
        "description": "Categoría del feedback",
        "enum": ["precio", "producto", "mercado", "competencia", "regulacion", "usuario", "tecnico", "general"]
      },
      "impacto": {
        "type": "string",
        "description": "Impacto del feedback",
        "enum": ["alto", "medio", "bajo"]
      },
      "accion_recomendada": {
        "type": "string",
        "description": "Acción recomendada basada en el feedback"
      }
    },
    "required": ["producto", "mercado", "observacion"]
  }
}
```

#### **Función 2: analizar_mercado_completo**
```json
{
  "name": "analizar_mercado_completo",
  "description": "Realiza análisis completo de mercado para un producto en un país",
  "parameters": {
    "type": "object",
    "properties": {
      "consulta": {
        "type": "string",
        "description": "Consulta en lenguaje natural sobre el análisis de mercado",
        "required": true
      }
    },
    "required": ["consulta"]
  }
}
```

#### **Función 3: obtener_feedback**
```json
{
  "name": "obtener_feedback",
  "description": "Obtiene retroalimentación existente para un producto o mercado específico",
  "parameters": {
    "type": "object",
    "properties": {
      "producto": {
        "type": "string",
        "description": "Nombre del producto para filtrar"
      },
      "mercado": {
        "type": "string",
        "description": "País o mercado para filtrar"
      }
    }
  }
}
```

### 3.5 **Configurar URLs de las Funciones**
Para cada función, configura la URL de tu API:

```
Base URL: https://tu-api-url.com

guardar_feedback: POST /feedback/guardar_feedback/
analizar_mercado_completo: POST /analizar_mercado_completo/
obtener_feedback: GET /feedback/obtener_feedback/
analizar_feedback_producto: GET /feedback/analizar_feedback/{producto}/{mercado}
procesar_retroalimentacion: POST /feedback/procesar_retroalimentacion/
```

## 🧪 **PASO 4: Probar la Integración**

### 4.1 **Ejecutar Simulador Local**
```bash
# Ejecutar simulador para probar
python ejemplo_retroalimentacion_gpt.py
```

### 4.2 **Probar en Chat de GPT**
Una vez configurado, prueba estas conversaciones:

#### **Ejemplo 1: Retroalimentación de Producto**
```
Usuario: "El producto Wallet + KYC en Colombia tuvo baja adopción porque el onboarding fue confuso."

GPT debería responder:
"Entiendo el problema. He guardado esta retroalimentación importante sobre Wallet + KYC en Colombia. 
Esta información será utilizada para mejorar nuestras estrategias futuras. 
¿Te gustaría que analice el feedback acumulado para este producto?"
```

#### **Ejemplo 2: Análisis de Mercado**
```
Usuario: "¿Qué sabes del mercado de wallets en México?"

GPT debería responder:
"Te ayudo con un análisis completo del mercado de wallets en México. 
Voy a recopilar información de múltiples fuentes y generar un análisis estratégico."
```

#### **Ejemplo 3: Consulta de Feedback**
```
Usuario: "¿Qué feedback tenemos sobre KYC en Colombia?"

GPT debería responder:
"Voy a consultar el feedback acumulado sobre KYC en Colombia y analizar los patrones principales."
```

## 🔧 **PASO 5: Configuración Avanzada**

### 5.1 **Variables de Entorno**
Asegúrate de que tu API tenga estas variables configuradas:

```bash
# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key

# APIs de búsqueda (opcional)
PERPLEXITY_API_KEY=your_perplexity_key
SERPAPI_KEY=your_serpapi_key
BRAVE_API_KEY=your_brave_key

# OpenAI
OPENAI_API_KEY=your_openai_key
```

### 5.2 **Configurar Autenticación (Opcional)**
Si necesitas autenticación en tu API:

```python
# En tu API, agregar middleware de autenticación
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_token(token: str = Depends(security)):
    # Verificar token
    if not is_valid_token(token.credentials):
        raise HTTPException(status_code=401, detail="Token inválido")
    return token.credentials
```

## 📊 **PASO 6: Monitoreo y Análisis**

### 6.1 **Verificar Feedback Almacenado**
```sql
-- Consultar feedback reciente
SELECT * FROM retroalimentacion 
WHERE estado = 'activo' 
ORDER BY fecha DESC 
LIMIT 10;

-- Estadísticas por producto
SELECT producto, COUNT(*) as total_feedbacks
FROM retroalimentacion 
WHERE estado = 'activo'
GROUP BY producto
ORDER BY total_feedbacks DESC;
```

### 6.2 **Análisis de Tendencias**
```sql
-- Categorías más comunes
SELECT categoria, COUNT(*) as count
FROM retroalimentacion 
WHERE estado = 'activo'
GROUP BY categoria
ORDER BY count DESC;

-- Impactos por mercado
SELECT mercado, impacto, COUNT(*) as count
FROM retroalimentacion 
WHERE estado = 'activo'
GROUP BY mercado, impacto
ORDER BY mercado, count DESC;
```

## 🚨 **Solución de Problemas**

### **Problema 1: GPT no llama a las funciones**
**Solución:**
- Verificar que las URLs de las funciones sean correctas
- Asegurar que la API esté funcionando
- Revisar que las definiciones de funciones sean válidas

### **Problema 2: Error 401/403 en API**
**Solución:**
- Verificar variables de entorno de Supabase
- Revisar políticas RLS en Supabase
- Confirmar que la API tenga acceso a la base de datos

### **Problema 3: Feedback no se guarda**
**Solución:**
- Verificar logs de la API
- Confirmar que la tabla `retroalimentacion` existe
- Revisar que los datos enviados sean válidos

### **Problema 4: GPT no entiende el contexto**
**Solución:**
- Mejorar las instrucciones del sistema
- Agregar más ejemplos de uso
- Refinar las descripciones de las funciones

## 📈 **Casos de Uso Avanzados**

### **Caso 1: Análisis Continuo**
```
Usuario: "¿Cómo ha evolucionado el feedback de nuestro producto en los últimos 3 meses?"

GPT debería:
1. Consultar feedback histórico
2. Analizar tendencias temporales
3. Identificar patrones de mejora o deterioro
4. Generar recomendaciones basadas en la evolución
```

### **Caso 2: Comparación de Mercados**
```
Usuario: "¿Cómo se compara el feedback de KYC entre México y Colombia?"

GPT debería:
1. Obtener feedback de ambos mercados
2. Comparar categorías y impactos
3. Identificar diferencias culturales o regulatorias
4. Sugerir estrategias específicas por mercado
```

### **Caso 3: Optimización de Producto**
```
Usuario: "Basándome en el feedback acumulado, ¿qué deberíamos mejorar primero?"

GPT debería:
1. Analizar todos los feedbacks activos
2. Priorizar por impacto y frecuencia
3. Generar roadmap de mejoras
4. Estimar recursos necesarios
```

## 🎯 **Próximos Pasos**

1. **Configurar Alertas**: Crear notificaciones para feedback de alto impacto
2. **Dashboard**: Desarrollar interfaz para visualizar feedback en tiempo real
3. **Análisis Predictivo**: Implementar ML para predecir tendencias
4. **Integración CRM**: Conectar con sistemas de ventas para correlacionar feedback con métricas
5. **Automatización**: Crear flujos automáticos basados en feedback

---

## ✅ **Checklist de Configuración**

- [ ] API desplegada y funcionando
- [ ] Tablas de Supabase creadas
- [ ] GPT personalizado creado
- [ ] Funciones configuradas
- [ ] URLs de API configuradas
- [ ] Pruebas básicas realizadas
- [ ] Variables de entorno configuradas
- [ ] Documentación del equipo actualizada

**¡Tu GPT personalizado con retroalimentación automática está listo!** 🚀 