-- Limpiar base de datos completa para prueba final
DELETE FROM agent_token_usage_history;
DELETE FROM asset_heartbeats;
DELETE FROM assets;
DELETE FROM agent_installation_tokens;

-- Verificar limpieza
SELECT 'LIMPIEZA COMPLETADA' as resultado;
SELECT 'Assets:' as tabla, COUNT(*) as cantidad FROM assets
UNION ALL
SELECT 'Tokens:' as tabla, COUNT(*) as cantidad FROM agent_installation_tokens
UNION ALL
SELECT 'Heartbeats:' as tabla, COUNT(*) as cantidad FROM asset_heartbeats
UNION ALL
SELECT 'Token Usage:' as tabla, COUNT(*) as cantidad FROM agent_token_usage_history;
