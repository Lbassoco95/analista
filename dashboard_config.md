# Configuración de Dashboards con Metabase/Retool

Esta guía te ayudará a configurar dashboards para visualizar los datos de Supabase usando Metabase o Retool.

## 🎯 Metabase (Recomendado para análisis)

### 1. Configuración Inicial

1. **Crear cuenta en Metabase:**
   - Ve a [metabase.com](https://metabase.com)
   - Crea una cuenta gratuita
   - Selecciona "Connect to your data"

2. **Conectar a Supabase:**
   - Selecciona "PostgreSQL" como base de datos
   - **Host:** `db.[tu-proyecto].supabase.co`
   - **Puerto:** `5432`
   - **Base de datos:** `postgres`
   - **Usuario:** `postgres`
   - **Contraseña:** Tu contraseña de Supabase (en Settings > Database)

### 2. Consultas SQL Recomendadas

#### 📊 Resumen General
```sql
SELECT 
    fuente,
    COUNT(*) as total_registros,
    COUNT(CASE WHEN analizado_gpt = true THEN 1 END) as analizados_gpt,
    AVG(CASE WHEN precio_estimado != 'No especificado' 
        THEN CAST(REPLACE(REPLACE(precio_estimado, '$', ''), ',', '') AS DECIMAL) 
        END) as precio_promedio
FROM precios_modulos 
GROUP BY fuente
ORDER BY total_registros DESC;
```

#### 💰 Análisis de Precios por Módulo
```sql
SELECT 
    clasificacion_gpt,
    COUNT(*) as total,
    AVG(CASE WHEN precio_gpt != 'No especificado' 
        THEN CAST(REPLACE(REPLACE(precio_gpt, '$', ''), ',', '') AS DECIMAL) 
        END) as precio_promedio_gpt,
    MIN(CASE WHEN precio_gpt != 'No especificado' 
        THEN CAST(REPLACE(REPLACE(precio_gpt, '$', ''), ',', '') AS DECIMAL) 
        END) as precio_minimo,
    MAX(CASE WHEN precio_gpt != 'No especificado' 
        THEN CAST(REPLACE(REPLACE(precio_gpt, '$', ''), ',', '') AS DECIMAL) 
        END) as precio_maximo
FROM precios_modulos 
WHERE analizado_gpt = true
GROUP BY clasificacion_gpt
ORDER BY precio_promedio_gpt DESC;
```

#### 📈 Evolución Temporal
```sql
SELECT 
    DATE(fecha) as fecha_extraccion,
    fuente,
    COUNT(*) as nuevos_registros
FROM precios_modulos 
GROUP BY DATE(fecha), fuente
ORDER BY fecha_extraccion DESC;
```

#### 🎯 Comparación de Proveedores
```sql
SELECT 
    fuente,
    clasificacion_gpt,
    COUNT(*) as cantidad,
    AVG(CASE WHEN precio_gpt != 'No especificado' 
        THEN CAST(REPLACE(REPLACE(precio_gpt, '$', ''), ',', '') AS DECIMAL) 
        END) as precio_promedio
FROM precios_modulos 
WHERE analizado_gpt = true
GROUP BY fuente, clasificacion_gpt
ORDER BY fuente, precio_promedio DESC;
```

### 3. Dashboards Recomendados

#### 📊 Dashboard Principal
1. **Métricas clave:**
   - Total de proveedores monitoreados
   - Total de módulos analizados
   - Precio promedio del mercado
   - Última actualización

2. **Gráficos:**
   - Distribución de precios por módulo (gráfico de barras)
   - Comparación de proveedores (gráfico de líneas)
   - Evolución temporal (gráfico de área)

#### 💰 Análisis de Precios
1. **Tabla de precios:**
   - Proveedor
   - Módulo
   - Precio estimado
   - Precio GPT
   - Confianza del análisis

2. **Gráficos:**
   - Rango de precios por módulo (box plot)
   - Distribución de precios (histograma)
   - Top proveedores por precio (gráfico de barras)

## 🔧 Retool (Recomendado para aplicaciones)

### 1. Configuración Inicial

1. **Crear cuenta en Retool:**
   - Ve a [retool.com](https://retool.com)
   - Crea una cuenta gratuita
   - Crea una nueva aplicación

2. **Conectar a Supabase:**
   - En "Resources" > "Add a resource"
   - Selecciona "PostgreSQL"
   - Usa las mismas credenciales que Metabase

### 2. Componentes Recomendados

#### 📋 Tabla de Datos
```javascript
// Query para la tabla
SELECT 
    id,
    fuente,
    modulo,
    clasificacion_gpt,
    precio_estimado,
    precio_gpt,
    confianza_analisis,
    fecha
FROM precios_modulos 
WHERE analizado_gpt = true
ORDER BY fecha DESC;
```

#### 📊 Gráficos
```javascript
// Query para gráfico de precios
SELECT 
    clasificacion_gpt,
    AVG(CASE WHEN precio_gpt != 'No especificado' 
        THEN CAST(REPLACE(REPLACE(precio_gpt, '$', ''), ',', '') AS DECIMAL) 
        END) as precio_promedio
FROM precios_modulos 
WHERE analizado_gpt = true
GROUP BY clasificacion_gpt
ORDER BY precio_promedio DESC;
```

### 3. Aplicación de Gestión

#### 🎛️ Panel de Control
- **Filtros:** Por proveedor, módulo, rango de precios
- **Búsqueda:** Texto libre en descripciones
- **Exportación:** CSV, Excel, PDF

#### 📈 Análisis Competitivo
- Comparación lado a lado de proveedores
- Análisis de tendencias de precios
- Identificación de oportunidades de mercado

## 📊 KPIs Recomendados

### Métricas de Negocio
1. **Precio promedio del mercado:** $X,XXX
2. **Margen potencial:** X%
3. **Proveedores analizados:** X
4. **Módulos cubiertos:** X

### Métricas de Calidad
1. **Datos analizados por GPT:** X%
2. **Confianza promedio del análisis:** X%
3. **Última actualización:** DD/MM/YYYY

## 🔄 Automatización

### Actualizaciones Automáticas
1. **Programar scraping:** Diario/semanal
2. **Análisis GPT:** Automático tras scraping
3. **Alertas:** Cambios significativos de precios

### Integración con Slack/Email
```javascript
// Ejemplo de alerta en Retool
if (precio_cambio > 20%) {
    // Enviar notificación
    sendSlackMessage({
        channel: '#precios',
        text: `🚨 Cambio significativo en ${proveedor}: ${precio_anterior} → ${precio_nuevo}`
    });
}
```

## 📱 Visualizaciones Móviles

### Metabase Mobile
- Dashboards responsivos
- Notificaciones push
- Acceso offline a métricas clave

### Retool Mobile
- Aplicación nativa
- Gestión de datos en tiempo real
- Acciones rápidas

## 🎨 Personalización

### Temas y Colores
- **Verde:** Precios competitivos
- **Amarillo:** Precios medios
- **Rojo:** Precios altos
- **Azul:** Datos neutrales

### Branding
- Logo de tu empresa
- Colores corporativos
- Información de contacto

## 📈 Próximos Pasos

1. **Implementar dashboards básicos**
2. **Configurar alertas automáticas**
3. **Integrar con herramientas de ventas**
4. **Desarrollar análisis predictivos**
5. **Crear reportes ejecutivos**

---

**Nota:** Tanto Metabase como Retool se conectan nativamente a Supabase, por lo que la configuración es muy sencilla. Metabase es mejor para análisis y reportes, mientras que Retool es ideal para aplicaciones interactivas y gestión de datos. 