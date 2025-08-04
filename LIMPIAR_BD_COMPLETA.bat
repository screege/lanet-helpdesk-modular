@echo off
echo ========================================
echo LIMPIEZA COMPLETA DE BASE DE DATOS
echo ========================================
echo.
echo ESTO VA A ELIMINAR:
echo   🗑️  Todos los assets registrados
echo   🗑️  Todos los tokens de agentes
echo   🗑️  Todos los heartbeats
echo   🗑️  Todo el historial de agentes
echo.
echo PARA PRUEBA DESDE CERO:
echo   ✅ Registro completamente nuevo
echo   ✅ Token completamente nuevo
echo   ✅ Asset ID completamente nuevo
echo   ✅ Prueba manual completa
echo.
echo ========================================

echo.
echo ⚠️  ADVERTENCIA: Esta operación es IRREVERSIBLE
echo.
set /p confirm="¿Estás seguro de eliminar TODOS los datos de agentes? (s/n): "
if /i not "%confirm%"=="s" (
    echo ❌ Operación cancelada
    pause
    exit /b 0
)

echo.
echo 🛑 PASO 1: Detener agente actual
sc stop LANETAgent 2>nul
timeout /t 3 /nobreak >nul

echo.
echo 🗑️  PASO 2: Limpieza completa de base de datos
echo   Conectando a PostgreSQL...

psql -U postgres -d lanet_helpdesk -c "
-- Eliminar todos los heartbeats
DELETE FROM asset_heartbeats;
VACUUM asset_heartbeats;

-- Eliminar todos los assets
DELETE FROM assets;
VACUUM assets;

-- Eliminar todos los tokens de agentes
DELETE FROM agent_tokens;
VACUUM agent_tokens;

-- Resetear secuencias si existen
SELECT setval(pg_get_serial_sequence('assets', 'id'), 1, false);
SELECT setval(pg_get_serial_sequence('agent_tokens', 'id'), 1, false);

-- Mostrar conteos finales
SELECT 'Assets restantes:' as tabla, COUNT(*) as cantidad FROM assets
UNION ALL
SELECT 'Tokens restantes:' as tabla, COUNT(*) as cantidad FROM agent_tokens
UNION ALL
SELECT 'Heartbeats restantes:' as tabla, COUNT(*) as cantidad FROM asset_heartbeats;
"

if %errorLevel% == 0 (
    echo ✅ Base de datos limpiada exitosamente
) else (
    echo ❌ Error limpiando base de datos
    echo   Verifica que PostgreSQL esté ejecutándose
    echo   Usuario: postgres, Contraseña: Poikl55+*
    pause
    exit /b 1
)

echo.
echo 🗑️  PASO 3: Limpiar agente local
rmdir /s /q "C:\Program Files\LANET Agent" 2>nul
sc delete LANETAgent 2>nul

echo.
echo ✅ LIMPIEZA COMPLETA FINALIZADA
echo.
echo ESTADO ACTUAL:
echo   🗑️  Base de datos: COMPLETAMENTE LIMPIA
echo   🗑️  Agente local: ELIMINADO
echo   🗑️  Tokens: TODOS ELIMINADOS
echo   🗑️  Assets: TODOS ELIMINADOS
echo   🗑️  Heartbeats: TODOS ELIMINADOS
echo.
echo 📋 PRÓXIMOS PASOS PARA PRUEBA MANUAL:
echo   1. Instalar agente con heartbeat simple
echo   2. Usar token completamente nuevo
echo   3. Verificar registro desde cero
echo   4. Probar heartbeats desde el inicio
echo.
echo 🎯 RESULTADO ESPERADO:
echo   ✅ Registro completamente nuevo
echo   ✅ Asset ID nuevo generado
echo   ✅ Token nuevo validado
echo   ✅ Heartbeats funcionando desde el primer momento
echo.
echo ========================================

pause
