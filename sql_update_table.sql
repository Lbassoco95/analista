-- Script SQL para actualizar la tabla precios_modulos con columnas para análisis GPT
-- Ejecuta este script en el editor SQL de Supabase

-- Agregar nuevas columnas para el análisis GPT
ALTER TABLE precios_modulos 
ADD COLUMN IF NOT EXISTS precio_gpt VARCHAR(100),
ADD COLUMN IF NOT EXISTS clasificacion_gpt VARCHAR(200),
ADD COLUMN IF NOT EXISTS condiciones_comerciales JSONB,
ADD COLUMN IF NOT EXISTS confianza_analisis VARCHAR(50),
ADD COLUMN IF NOT EXISTS fecha_analisis_gpt TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS analizado_gpt BOOLEAN DEFAULT FALSE;

-- Crear índices para mejorar el rendimiento de consultas
CREATE INDEX IF NOT EXISTS idx_precios_modulos_fuente ON precios_modulos(fuente);
CREATE INDEX IF NOT EXISTS idx_precios_modulos_clasificacion ON precios_modulos(clasificacion_gpt);
CREATE INDEX IF NOT EXISTS idx_precios_modulos_analizado ON precios_modulos(analizado_gpt);
CREATE INDEX IF NOT EXISTS idx_precios_modulos_fecha ON precios_modulos(fecha);

-- Crear vista para datos analizados
CREATE OR REPLACE VIEW datos_analizados AS
SELECT 
    id,
    fuente,
    modulo,
    texto_extraido,
    precio_estimado,
    precio_gpt,
    clasificacion_gpt,
    condiciones_comerciales,
    confianza_analisis,
    fecha,
    fecha_analisis_gpt,
    analizado_gpt
FROM precios_modulos
WHERE analizado_gpt = TRUE;

-- Crear vista para datos pendientes de análisis
CREATE OR REPLACE VIEW datos_pendientes_analisis AS
SELECT 
    id,
    fuente,
    modulo,
    texto_extraido,
    precio_estimado,
    fecha
FROM precios_modulos
WHERE analizado_gpt = FALSE OR analizado_gpt IS NULL;

-- Función para actualizar el estado de análisis
CREATE OR REPLACE FUNCTION marcar_como_analizado(record_id INTEGER)
RETURNS VOID AS $$
BEGIN
    UPDATE precios_modulos 
    SET analizado_gpt = TRUE, 
        fecha_analisis_gpt = NOW()
    WHERE id = record_id;
END;
$$ LANGUAGE plpgsql;

-- Comentarios en las columnas para documentación
COMMENT ON COLUMN precios_modulos.precio_gpt IS 'Precio estimado por GPT';
COMMENT ON COLUMN precios_modulos.clasificacion_gpt IS 'Clasificación del módulo realizada por GPT';
COMMENT ON COLUMN precios_modulos.condiciones_comerciales IS 'Condiciones comerciales extraídas por GPT en formato JSON';
COMMENT ON COLUMN precios_modulos.confianza_analisis IS 'Nivel de confianza del análisis GPT (alta/media/baja)';
COMMENT ON COLUMN precios_modulos.fecha_analisis_gpt IS 'Fecha y hora del análisis GPT';
COMMENT ON COLUMN precios_modulos.analizado_gpt IS 'Indica si el registro ha sido analizado por GPT'; 