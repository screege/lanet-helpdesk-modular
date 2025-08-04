-- CREAR INFRAESTRUCTURA DE HEARTBEATS PARA LANET HELPDESK
-- Ejecutar con: psql -U postgres -d lanet_helpdesk -f crear_heartbeats.sql

-- 1. Crear tabla de heartbeats
CREATE TABLE IF NOT EXISTS asset_heartbeats (
    heartbeat_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id UUID REFERENCES assets(asset_id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    cpu_usage DECIMAL(5,2),
    memory_usage DECIMAL(5,2),
    disk_usage DECIMAL(5,2),
    network_status VARCHAR(20) DEFAULT 'connected',
    agent_version VARCHAR(50),
    system_uptime BIGINT,
    status VARCHAR(20) DEFAULT 'online'
);

-- 2. Crear índices para performance
CREATE INDEX IF NOT EXISTS idx_asset_heartbeats_asset_id ON asset_heartbeats(asset_id);
CREATE INDEX IF NOT EXISTS idx_asset_heartbeats_created_at ON asset_heartbeats(created_at);
CREATE INDEX IF NOT EXISTS idx_asset_heartbeats_asset_created ON asset_heartbeats(asset_id, created_at);

-- 3. Crear función para limpiar heartbeats antiguos
CREATE OR REPLACE FUNCTION cleanup_old_heartbeats()
RETURNS void AS $$
BEGIN
    -- Mantener solo los últimos 7 días de heartbeats
    DELETE FROM asset_heartbeats 
    WHERE created_at < NOW() - INTERVAL '7 days';
END;
$$ LANGUAGE plpgsql;

-- 4. Crear vista para último heartbeat por asset
CREATE OR REPLACE VIEW asset_latest_heartbeat AS
SELECT DISTINCT ON (asset_id)
    asset_id,
    created_at as last_heartbeat,
    cpu_usage,
    memory_usage,
    disk_usage,
    status,
    EXTRACT(EPOCH FROM (NOW() - created_at))/60 as minutes_since_heartbeat
FROM asset_heartbeats
ORDER BY asset_id, created_at DESC;

-- 5. Insertar heartbeat de prueba para el asset actual
INSERT INTO asset_heartbeats (
    asset_id, 
    cpu_usage, 
    memory_usage, 
    disk_usage, 
    status
) 
SELECT 
    asset_id,
    23.50,
    87.20,
    45.30,
    'online'
FROM assets 
WHERE name LIKE '%Agent%' AND status = 'active'
LIMIT 1;

-- Mostrar resultado
SELECT 'INFRAESTRUCTURA DE HEARTBEATS CREADA EXITOSAMENTE' as resultado;
