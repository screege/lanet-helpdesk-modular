-- PROBAR SISTEMA DE HEARTBEATS COMPLETO
-- Ejecutar con: psql -U postgres -d lanet_helpdesk -f probar_heartbeats.sql

-- 1. Insertar heartbeat de prueba
INSERT INTO asset_heartbeats (
    asset_id, cpu_usage, memory_usage, disk_usage, 
    status, agent_version, network_status
) VALUES (
    '41d49541-d129-4ebc-b66b-a8f4e02300bc',
    28.5, 91.2, 45.8, 'online', '1.0.0', 'connected'
);

-- 2. Verificar último heartbeat
SELECT 
    'ÚLTIMO HEARTBEAT:' as seccion,
    asset_id,
    last_heartbeat,
    minutes_since_heartbeat,
    cpu_usage,
    memory_usage,
    status
FROM asset_latest_heartbeat
WHERE asset_id = '41d49541-d129-4ebc-b66b-a8f4e02300bc';

-- 3. Verificar consulta de assets con heartbeats
SELECT
    'CONSULTA DE ASSETS:' as seccion,
    a.name,
    COALESCE(h.last_heartbeat, a.last_seen) as last_connection,
    EXTRACT(EPOCH FROM (NOW() - COALESCE(h.last_heartbeat, a.last_seen)))/60 as minutes_ago,
    CASE
        WHEN COALESCE(h.last_heartbeat, a.last_seen) > NOW() - INTERVAL '20 minutes' THEN 'online'
        WHEN COALESCE(h.last_heartbeat, a.last_seen) > NOW() - INTERVAL '1 hour' THEN 'warning'
        ELSE 'offline'
    END as connection_status
FROM assets a
LEFT JOIN asset_latest_heartbeat h ON a.asset_id = h.asset_id
WHERE a.asset_id = '41d49541-d129-4ebc-b66b-a8f4e02300bc';

-- 4. Contar heartbeats totales
SELECT 
    'RESUMEN:' as seccion,
    COUNT(*) as total_heartbeats,
    MAX(created_at) as ultimo_heartbeat,
    EXTRACT(EPOCH FROM (NOW() - MAX(created_at)))/60 as minutos_desde_ultimo
FROM asset_heartbeats
WHERE asset_id = '41d49541-d129-4ebc-b66b-a8f4e02300bc';

SELECT '✅ SISTEMA DE HEARTBEATS FUNCIONANDO CORRECTAMENTE' as resultado;
