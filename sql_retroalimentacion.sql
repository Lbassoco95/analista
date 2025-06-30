-- SQL para crear tabla de retroalimentación en Supabase
-- Ejecutar en el SQL Editor de Supabase

-- Crear tabla de retroalimentación
CREATE TABLE IF NOT EXISTS retroalimentacion (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    producto TEXT NOT NULL,
    mercado TEXT NOT NULL,
    observacion TEXT NOT NULL,
    categoria TEXT DEFAULT 'general',
    impacto TEXT DEFAULT 'medio' CHECK (impacto IN ('alto', 'medio', 'bajo')),
    accion_recomendada TEXT,
    fuente TEXT DEFAULT 'gpt_chat',
    metadata JSONB DEFAULT '{}',
    fecha TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    estado TEXT DEFAULT 'activo' CHECK (estado IN ('activo', 'eliminado', 'archivado')),
    fecha_eliminacion TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Crear índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_retroalimentacion_producto ON retroalimentacion(producto);
CREATE INDEX IF NOT EXISTS idx_retroalimentacion_mercado ON retroalimentacion(mercado);
CREATE INDEX IF NOT EXISTS idx_retroalimentacion_categoria ON retroalimentacion(categoria);
CREATE INDEX IF NOT EXISTS idx_retroalimentacion_estado ON retroalimentacion(estado);
CREATE INDEX IF NOT EXISTS idx_retroalimentacion_fecha ON retroalimentacion(fecha);
CREATE INDEX IF NOT EXISTS idx_retroalimentacion_producto_mercado ON retroalimentacion(producto, mercado);

-- Crear función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Crear trigger para actualizar updated_at
CREATE TRIGGER update_retroalimentacion_updated_at 
    BEFORE UPDATE ON retroalimentacion 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Crear tabla de análisis de retroalimentación (para almacenar análisis procesados)
CREATE TABLE IF NOT EXISTS analisis_retroalimentacion (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    producto TEXT NOT NULL,
    mercado TEXT NOT NULL,
    total_feedbacks INTEGER DEFAULT 0,
    categorias_mas_comunes JSONB DEFAULT '[]',
    distribucion_impactos JSONB DEFAULT '{}',
    observaciones_clave JSONB DEFAULT '[]',
    recomendaciones JSONB DEFAULT '[]',
    prioridad TEXT DEFAULT 'baja' CHECK (prioridad IN ('alta', 'media', 'baja')),
    fecha_analisis TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    fecha_procesamiento TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Crear índices para análisis
CREATE INDEX IF NOT EXISTS idx_analisis_producto ON analisis_retroalimentacion(producto);
CREATE INDEX IF NOT EXISTS idx_analisis_mercado ON analisis_retroalimentacion(mercado);
CREATE INDEX IF NOT EXISTS idx_analisis_prioridad ON analisis_retroalimentacion(prioridad);
CREATE INDEX IF NOT EXISTS idx_analisis_fecha ON analisis_retroalimentacion(fecha_analisis);

-- Crear trigger para análisis
CREATE TRIGGER update_analisis_retroalimentacion_updated_at 
    BEFORE UPDATE ON analisis_retroalimentacion 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Crear tabla de estadísticas de feedback (para cache de estadísticas)
CREATE TABLE IF NOT EXISTS estadisticas_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    total_feedbacks INTEGER DEFAULT 0,
    productos_unicos INTEGER DEFAULT 0,
    mercados_unicos INTEGER DEFAULT 0,
    categorias JSONB DEFAULT '{}',
    feedbacks_por_mes JSONB DEFAULT '{}',
    fecha_estadisticas TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Crear índices para estadísticas
CREATE INDEX IF NOT EXISTS idx_estadisticas_fecha ON estadisticas_feedback(fecha_estadisticas);

-- Insertar datos de ejemplo para testing
INSERT INTO retroalimentacion (producto, mercado, observacion, categoria, impacto, accion_recomendada) VALUES
('Wallet Crypto', 'México', 'El onboarding fue confuso para usuarios nuevos', 'producto', 'alto', 'Simplificar el proceso de registro'),
('KYC', 'Colombia', 'Los precios son competitivos pero falta documentación', 'precio', 'medio', 'Mejorar documentación técnica'),
('Onboarding Remoto', 'Perú', 'Excelente experiencia de usuario, muy intuitivo', 'producto', 'alto', 'Mantener la simplicidad del diseño'),
('Firma Digital', 'Chile', 'Necesitamos más opciones de integración', 'producto', 'medio', 'Desarrollar APIs adicionales'),
('Wallet Crypto', 'México', 'Las comisiones son muy altas comparadas con la competencia', 'precio', 'alto', 'Revisar estructura de comisiones');

-- Crear vista para feedback más reciente
CREATE OR REPLACE VIEW feedback_reciente AS
SELECT 
    id,
    producto,
    mercado,
    observacion,
    categoria,
    impacto,
    fecha,
    fuente
FROM retroalimentacion 
WHERE estado = 'activo' 
ORDER BY fecha DESC;

-- Crear función para obtener estadísticas en tiempo real
CREATE OR REPLACE FUNCTION obtener_estadisticas_feedback()
RETURNS JSON AS $$
DECLARE
    resultado JSON;
BEGIN
    SELECT json_build_object(
        'total_feedbacks', COUNT(*),
        'productos_unicos', COUNT(DISTINCT producto),
        'mercados_unicos', COUNT(DISTINCT mercado),
        'categorias', json_object_agg(categoria, COUNT(*)),
        'feedbacks_por_mes', json_object_agg(
            TO_CHAR(fecha, 'YYYY-MM'), 
            COUNT(*)
        ),
        'fecha_estadisticas', NOW()
    ) INTO resultado
    FROM retroalimentacion 
    WHERE estado = 'activo';
    
    RETURN resultado;
END;
$$ LANGUAGE plpgsql;

-- Crear función para analizar feedback de un producto específico
CREATE OR REPLACE FUNCTION analizar_feedback_producto(p_producto TEXT, p_mercado TEXT)
RETURNS JSON AS $$
DECLARE
    resultado JSON;
BEGIN
    SELECT json_build_object(
        'producto', p_producto,
        'mercado', p_mercado,
        'total_feedbacks', COUNT(*),
        'categorias_mas_comunes', (
            SELECT json_agg(json_build_object('categoria', categoria, 'count', count))
            FROM (
                SELECT categoria, COUNT(*) as count
                FROM retroalimentacion 
                WHERE producto = p_producto 
                AND mercado = p_mercado 
                AND estado = 'activo'
                GROUP BY categoria
                ORDER BY count DESC
                LIMIT 3
            ) subq
        ),
        'distribucion_impactos', json_build_object(
            'alto', COUNT(*) FILTER (WHERE impacto = 'alto'),
            'medio', COUNT(*) FILTER (WHERE impacto = 'medio'),
            'bajo', COUNT(*) FILTER (WHERE impacto = 'bajo')
        ),
        'observaciones_clave', (
            SELECT json_agg(observacion)
            FROM (
                SELECT observacion
                FROM retroalimentacion 
                WHERE producto = p_producto 
                AND mercado = p_mercado 
                AND estado = 'activo'
                ORDER BY fecha DESC
                LIMIT 5
            ) subq
        ),
        'fecha_analisis', NOW()
    ) INTO resultado
    FROM retroalimentacion 
    WHERE producto = p_producto 
    AND mercado = p_mercado 
    AND estado = 'activo';
    
    RETURN resultado;
END;
$$ LANGUAGE plpgsql;

-- Crear políticas RLS (Row Level Security) si es necesario
-- ALTER TABLE retroalimentacion ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE analisis_retroalimentacion ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE estadisticas_feedback ENABLE ROW LEVEL SECURITY;

-- Crear políticas de acceso (ejemplo para acceso público de lectura)
-- CREATE POLICY "Permitir lectura pública de retroalimentación" ON retroalimentacion
--     FOR SELECT USING (true);

-- CREATE POLICY "Permitir inserción de retroalimentación" ON retroalimentacion
--     FOR INSERT WITH CHECK (true);

-- CREATE POLICY "Permitir actualización de retroalimentación" ON retroalimentacion
--     FOR UPDATE USING (true);

-- Verificar que las tablas se crearon correctamente
SELECT 'Tabla retroalimentacion creada' as status WHERE EXISTS (
    SELECT 1 FROM information_schema.tables 
    WHERE table_name = 'retroalimentacion'
);

SELECT 'Tabla analisis_retroalimentacion creada' as status WHERE EXISTS (
    SELECT 1 FROM information_schema.tables 
    WHERE table_name = 'analisis_retroalimentacion'
);

SELECT 'Tabla estadisticas_feedback creada' as status WHERE EXISTS (
    SELECT 1 FROM information_schema.tables 
    WHERE table_name = 'estadisticas_feedback'
); 