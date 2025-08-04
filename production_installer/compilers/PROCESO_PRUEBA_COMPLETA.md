# PROCESO DE PRUEBA COMPLETA - LANET AGENT
## Desde Cero - Manual Completo

### 📁 Ubicación de Scripts
```
C:\lanet-helpdesk-v3\production_installer\compilers\
├── limpiar_base_datos.py           # ← Limpiar BD
├── compile_agent.py                # ← Compilar agente
└── PROCESO_PRUEBA_COMPLETA.md      # ← Esta guía
```

### 🎯 Objetivo
Probar completamente el agente LANET desde cero para verificar:
- ✅ No se crean assets duplicados después de reinicios
- ✅ Heartbeat funciona cada 15 minutos
- ✅ Hardware fingerprinting previene duplicados
- ✅ Sistema funciona para 2000+ assets

---

## 🚀 PROCESO PASO A PASO

### **PASO 1: Limpieza Completa de Base de Datos**

```bash
# Ejecutar script de limpieza
cd C:\lanet-helpdesk-v3\production_installer\compilers
python limpiar_base_datos.py
```

**¿Qué hace?**
- 🗑️ Elimina TODOS los assets de agente
- 🗑️ Elimina TODOS los tokens de instalación
- 🗑️ Elimina TODO el historial de tokens
- ✅ Verifica que la limpieza fue exitosa

**Resultado esperado:**
```
✅ LIMPIEZA COMPLETA EXITOSA
🎯 BASE DE DATOS LISTA PARA PRUEBA DESDE CERO
```

---

### **PASO 2: Limpieza Completa del Equipo**

```bash
# Ejecutar como ADMINISTRADOR
C:\lanet-helpdesk-v3\LIMPIAR_AGENTE_COMPLETO.bat
```

**¿Qué hace?**
- 🛑 Detiene y elimina servicio LANETAgent
- 🔪 Termina todos los procesos del agente
- 📁 Elimina directorios del agente
- 🗂️ Limpia registro de Windows
- 🗑️ Elimina archivos temporales
- 🗄️ Limpia base de datos local del agente

**Resultado esperado:**
```
✅ LIMPIEZA COMPLETA FINALIZADA
🎯 El sistema está listo para una instalación limpia del agente
```

---

### **PASO 3: Reiniciar Computadora**

```bash
# Reiniciar para limpieza completa
shutdown /r /t 0
```

**¿Por qué?**
- 🔄 Asegura que todos los procesos estén terminados
- 🧹 Limpia memoria y recursos del sistema
- ✅ Garantiza instalación completamente limpia

---

### **PASO 4: Generar Token Manualmente**

**Opción A: Frontend Web**
1. Ir a `http://localhost:5173` (o tu URL del helpdesk)
2. Login como superadmin
3. Ir a **Configuración > Tokens de Agente**
4. Crear nuevo token
5. Copiar el token generado

**Opción B: Base de Datos Directa**
```sql
-- Conectar a PostgreSQL
psql -U postgres -d lanet_helpdesk

-- Crear token manualmente
INSERT INTO agent_installation_tokens (
    token_id, client_id, site_id, token_value, is_active,
    created_by, created_at, expires_at, usage_count
) VALUES (
    gen_random_uuid(),
    'tu-client-id',
    'tu-site-id', 
    'LANET-TEST-SITE-ABC123',
    true,
    'tu-user-id',
    NOW(),
    NOW() + INTERVAL '30 days',
    0
);
```

**Formato del Token:**
```
LANET-{CLIENTE}-{SITIO}-{RANDOM}
Ejemplo: LANET-TEST-MAIN-A1B2C3
```

---

### **PASO 5: Instalar Agente con Nuevo Instalador**

```bash
# Ejecutar como ADMINISTRADOR
C:\lanet-helpdesk-v3\production_installer\deployment\LANET_Agent_Installer.exe
```

**Configuración de Instalación:**
1. **Modo**: Custom Install
2. **Token**: Pegar el token generado en Paso 4
3. **Configuración**: Dejar por defecto
4. **Instalación**: Completar proceso

**Resultado esperado:**
- ✅ Instalación exitosa
- ✅ Servicio LANETAgent iniciado
- ✅ 1 asset creado en base de datos
- ✅ Asset con heartbeat reciente (<15 minutos)

---

### **PASO 6: Verificar Primera Instalación**

```bash
# Verificar en base de datos
cd C:\lanet-helpdesk-v3\production_installer\compilers
python -c "
import psycopg2
conn = psycopg2.connect('postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk')
cur = conn.cursor()

cur.execute('''
SELECT name, COUNT(*) as count, STRING_AGG(asset_id::text, ', ') as asset_ids
FROM assets 
WHERE status = 'active' AND name LIKE '%Agent%'
GROUP BY name
''')

results = cur.fetchall()
for name, count, asset_ids in results:
    print(f'{name}: {count} asset(s)')
    print(f'Asset IDs: {asset_ids}')

conn.close()
"
```

**Resultado esperado:**
```
benny-lenovo (Agent): 1 asset(s)
Asset IDs: abc123-def456-ghi789
```

---

### **PASO 7: Prueba de Reinicios Múltiples**

**Reinicio 1:**
```bash
shutdown /r /t 0
```
- ⏱️ Esperar que reinicie completamente
- ⏱️ Esperar 2-3 minutos para que el agente se conecte
- ✅ Verificar que sigue siendo 1 asset

**Reinicio 2:**
```bash
shutdown /r /t 0
```
- ⏱️ Esperar que reinicie completamente
- ⏱️ Esperar 2-3 minutos para que el agente se conecte
- ✅ Verificar que sigue siendo 1 asset

**Reinicio 3:**
```bash
shutdown /r /t 0
```
- ⏱️ Esperar que reinicie completamente
- ⏱️ Esperar 2-3 minutos para que el agente se conecte
- ✅ Verificar que sigue siendo 1 asset

---

### **PASO 8: Verificación Final**

```bash
# Verificar assets finales
cd C:\lanet-helpdesk-v3\production_installer\compilers
python -c "
import psycopg2
from datetime import datetime

conn = psycopg2.connect('postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk')
cur = conn.cursor()

cur.execute('''
SELECT 
    name,
    COUNT(*) as count,
    MAX(last_seen) as last_heartbeat,
    EXTRACT(EPOCH FROM (NOW() - MAX(last_seen)))/60 as minutes_ago
FROM assets 
WHERE status = 'active' AND name LIKE '%Agent%'
GROUP BY name
''')

results = cur.fetchall()
print('📊 RESULTADO FINAL:')
print('=' * 40)

for name, count, last_heartbeat, minutes_ago in results:
    if count == 1:
        print(f'✅ {name}: ÚNICO asset')
        print(f'   Último heartbeat: {minutes_ago:.1f} minutos atrás')
        if minutes_ago <= 20:
            print('   🟢 Heartbeat reciente - CORRECTO')
        else:
            print('   🔴 Heartbeat antiguo - PROBLEMA')
    else:
        print(f'❌ {name}: {count} assets DUPLICADOS')

conn.close()
"
```

---

## ✅ **CRITERIOS DE ÉXITO**

### **Prueba EXITOSA si:**
- ✅ Solo 1 asset después de múltiples reinicios
- ✅ Heartbeat cada 15-20 minutos máximo
- ✅ No se crean duplicados
- ✅ Agente funciona como servicio

### **Prueba FALLIDA si:**
- ❌ Múltiples assets después de reinicios
- ❌ Heartbeat cada 24 horas (configuración antigua)
- ❌ Se crean duplicados
- ❌ Agente no funciona como servicio

---

## 🔧 **Troubleshooting**

### **Problema: Se crean duplicados**
```bash
# Verificar hardware fingerprinting
# Revisar logs del agente
# Verificar configuración de heartbeat
```

### **Problema: Heartbeat lento (24 horas)**
```bash
# El instalador tiene configuración antigua
# Recompilar con: python compile_agent.py
```

### **Problema: Agente no se conecta**
```bash
# Verificar token válido
# Verificar conectividad de red
# Revisar logs del servicio
```

---

## 📋 **Checklist Final**

- [ ] Base de datos limpia (0 assets, 0 tokens)
- [ ] Equipo limpio (sin agente instalado)
- [ ] Computadora reiniciada
- [ ] Token generado manualmente
- [ ] Agente instalado con nuevo instalador
- [ ] 1 asset creado en BD
- [ ] Reinicio 1 completado - sigue 1 asset
- [ ] Reinicio 2 completado - sigue 1 asset  
- [ ] Reinicio 3 completado - sigue 1 asset
- [ ] Heartbeat cada 15 minutos
- [ ] **PRUEBA EXITOSA** ✅

---

**Fecha:** 2025-07-30  
**Versión:** 1.0  
**Estado:** Listo para Producción ✅
