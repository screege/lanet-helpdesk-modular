# LANET Agent V3 - Documentación Completa

## 📋 **Índice**
1. [Arquitectura del Sistema](#arquitectura)
2. [Códigos Fuente del Agente](#códigos-fuente)
3. [Compilación del Instalador](#compilación)
4. [Scripts de Limpieza](#scripts-limpieza)
5. [Desarrollo y Mantenimiento](#desarrollo)
6. [Troubleshooting](#troubleshooting)

---

## 🏗️ **Arquitectura del Sistema** {#arquitectura}

### **Estructura del Proyecto**
```
C:\lanet-helpdesk-v3\
├── production_installer\           # 🎯 DIRECTORIO PRINCIPAL DEL AGENTE
│   ├── agent_files\               # 📁 CÓDIGOS FUENTE DEL AGENTE
│   │   ├── main.py               # 🚀 Punto de entrada principal
│   │   ├── core\                 # 🧠 Núcleo del agente
│   │   │   ├── agent_core.py     # Orquestador principal
│   │   │   ├── config_manager.py # Gestión de configuración
│   │   │   ├── database.py       # Base de datos local SQLite
│   │   │   └── logger.py         # Sistema de logging
│   │   ├── modules\              # 🔧 Módulos funcionales
│   │   │   ├── registration.py   # Registro con servidor
│   │   │   ├── monitoring.py     # Monitoreo del sistema
│   │   │   ├── heartbeat.py      # Latidos al servidor
│   │   │   ├── bitlocker.py      # Datos de BitLocker
│   │   │   └── ticket_creator.py # Creación de tickets
│   │   ├── ui\                   # 🎨 Interfaz de usuario
│   │   │   ├── system_tray.py    # Icono en bandeja del sistema
│   │   │   ├── main_window.py    # Ventana principal
│   │   │   ├── installation_window.py # Ventana de instalación
│   │   │   └── ticket_window.py  # Ventana de tickets
│   │   ├── service\              # 🛠️ Servicio de Windows
│   │   │   ├── windows_service.py # Servicio principal
│   │   │   └── production_service.py # Servicio de producción
│   │   ├── config\               # ⚙️ Configuraciones
│   │   │   └── agent_config.json # Configuración del agente
│   │   └── requirements.txt      # Dependencias Python
│   ├── standalone_installer.py   # 🎯 INSTALADOR PRINCIPAL
│   ├── build_standalone_installer.py # 🔨 SCRIPT DE COMPILACIÓN
│   └── deployment\               # 📦 EJECUTABLE FINAL
│       └── LANET_Agent_Installer.exe # 🎯 INSTALADOR COMPILADO
```

### **Componentes Principales**

#### **1. Agent Core (`agent_core.py`)**
- **Función**: Orquestador principal del agente
- **Responsabilidades**:
  - Inicialización de módulos
  - Gestión del ciclo de vida
  - Coordinación entre componentes
  - Manejo de UI (system tray)

#### **2. Módulos Funcionales**
- **Registration**: Registro inicial con token
- **Monitoring**: Recolección de datos del sistema
- **Heartbeat**: Comunicación periódica con servidor
- **BitLocker**: Extracción de claves de cifrado
- **Ticket Creator**: Creación de tickets desde el agente

#### **3. Interfaz de Usuario**
- **System Tray**: Icono en bandeja del sistema
- **Main Window**: Ventana principal de estado
- **Installation Window**: Configuración inicial
- **Ticket Window**: Creación de tickets (futuro)

---

## 💻 **Códigos Fuente del Agente** {#códigos-fuente}

### **Ubicación Principal**
```
📁 C:\lanet-helpdesk-v3\production_installer\agent_files\
```

### **Archivos Clave**

#### **main.py** - Punto de Entrada
```python
# Funciones principales:
- main(): Punto de entrada principal
- Manejo de argumentos de línea de comandos
- Inicialización del AgentCore
- Gestión de modos (servicio, debug, UI)
```

#### **core/agent_core.py** - Núcleo del Agente
```python
# Clase principal: AgentCore
- __init__(config_manager, ui_enabled=True)
- start(): Inicia todos los módulos
- stop(): Detiene el agente limpiamente
- is_registered(): Verifica registro
- register_with_token(token): Registro con servidor
```

#### **modules/** - Módulos Funcionales
```python
# registration.py - Registro con servidor
# monitoring.py - Monitoreo del sistema
# heartbeat.py - Comunicación periódica
# bitlocker.py - Datos de BitLocker
# ticket_creator.py - Creación de tickets
```

#### **ui/** - Interfaz de Usuario
```python
# system_tray.py - Bandeja del sistema
# main_window.py - Ventana principal
# installation_window.py - Configuración inicial
# ticket_window.py - Creación de tickets
```

### **Configuración del Agente**
```json
// config/agent_config.json
{
  "server": {
    "base_url": "https://helpdesk.lanet.mx/api",
    "timeout": 30,
    "retry_attempts": 3
  },
  "agent": {
    "heartbeat_interval": 300,
    "monitoring_interval": 3600,
    "auto_register": true
  },
  "bitlocker": {
    "enabled": true,
    "collection_interval": 3600,
    "require_admin_privileges": false
  },
  "service": {
    "name": "LANETAgent",
    "display_name": "LANET Helpdesk Agent",
    "account": "LocalSystem"
  }
}
```

---

## 🔨 **Compilación del Instalador** {#compilación}

### **Script de Compilación**
```
📁 C:\lanet-helpdesk-v3\production_installer\build_standalone_installer.py
```

### **Proceso de Compilación**

#### **1. Preparación**
```bash
cd C:\lanet-helpdesk-v3\production_installer
```

#### **2. Ejecutar Compilación**
```bash
python build_standalone_installer.py
```

#### **3. Fuentes de Archivos**

##### **📄 Script Principal del Instalador:**
```
FUENTE: C:\lanet-helpdesk-v3\production_installer\standalone_installer.py
FUNCIÓN: Interfaz gráfica, lógica de instalación, validación de tokens
```

##### **📁 Archivos del Agente (Completos):**
```
FUENTE: C:\lanet-helpdesk-v3\production_installer\agent_files\
├── main.py                    # Punto de entrada del agente
├── core\
│   ├── agent_core.py         # Núcleo principal
│   ├── config_manager.py     # Gestión de configuración
│   ├── database.py           # Base de datos local
│   └── logger.py             # Sistema de logging
├── modules\
│   ├── registration.py       # Registro con servidor
│   ├── monitoring.py         # Monitoreo del sistema
│   ├── heartbeat.py          # Comunicación periódica
│   ├── bitlocker.py          # Datos de BitLocker
│   └── ticket_creator.py     # Creación de tickets
├── ui\
│   ├── system_tray.py        # Bandeja del sistema
│   ├── main_window.py        # Ventana principal
│   ├── installation_window.py # Configuración inicial
│   └── ticket_window.py      # Creación de tickets
├── service\
│   ├── windows_service.py    # Servicio principal
│   └── production_service.py # Servicio de producción
├── config\
│   └── agent_config.json     # Configuración del agente
└── requirements.txt          # Dependencias Python
```

#### **4. Proceso Automático Detallado**

##### **Paso 1: Verificación de Dependencias**
- PyInstaller
- Paquetes requeridos (requests, psycopg2-binary)

##### **Paso 2: Embedding Doble de Archivos**
```python
# El script hace DOBLE embedding para máxima compatibilidad:

# 1. EMBEDDING EN BASE64 (Líneas 70-115)
agent_files/ → ZIP → base64 → standalone_installer_embedded.py

# 2. EMBEDDING EN PYINSTALLER (Línea 206)
datas=[('agent_files', 'agent_files')]  # Archivos directos en bundle
```

**Detalles del proceso:**
1. **Compresión**: Todo `agent_files/` se comprime en ZIP
2. **Codificación**: ZIP se codifica en base64
3. **Inserción**: base64 se inserta en `standalone_installer.py`
4. **Creación**: Se genera `standalone_installer_embedded.py` (temporal)
5. **Bundle**: PyInstaller también incluye `agent_files/` directamente

##### **Paso 3: Creación de Metadatos**
- `version_info.txt` con información de LANET Systems
- Configuración de UAC para privilegios de administrador

##### **Paso 4: Generación de Spec PyInstaller**
```python
# Configuración completa (Líneas 202-240)
a = Analysis(
    ['standalone_installer_embedded.py'],  # Script con archivos embebidos
    pathex=[],
    binaries=[],
    datas=[('agent_files', 'agent_files')],  # Archivos también como datos
    hiddenimports=[
        'tkinter', 'tkinter.ttk', 'requests', 'psycopg2',
        'threading', 'subprocess', 'shutil', 'json'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='LANET_Agent_Installer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                    # Compresión UPX
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,               # Sin ventana de consola
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version_info.txt',  # Información de versión
    uac_admin=True,             # Requiere privilegios de administrador
)
```

##### **Paso 5: Compilación con PyInstaller**
- Crea ejecutable único autocontenido
- Incluye runtime de Python completo
- Aplica compresión UPX para reducir tamaño
- Configura UAC para solicitar permisos automáticamente

##### **Paso 6: Empaquetado Final**
- Copia resultado a `deployment/LANET_Agent_Installer.exe`
- Limpia archivos temporales
- Genera documentación de despliegue

#### **5. Estructura del Ejecutable Final**
```
📦 LANET_Agent_Installer.exe (~90MB)
├── 🐍 Python runtime completo embebido
├── 📄 standalone_installer_embedded.py
│   └── 📦 agent_files/ (como base64)
├── 📁 agent_files/ (como archivos directos de PyInstaller)
├── 🔧 Dependencias Python (tkinter, requests, psycopg2, etc.)
├── 📋 version_info.txt (metadatos de LANET Systems)
└── ⚙️ Configuración UAC (privilegios de administrador)
```

**¿Por qué doble embedding?**
- **Base64**: Permite extracción controlada y verificación
- **PyInstaller**: Fallback si el base64 falla
- **Redundancia**: Máxima compatibilidad en diferentes entornos

### **Resultado Final**
```
📁 C:\lanet-helpdesk-v3\production_installer\deployment\
└── LANET_Agent_Installer.exe  # ~90MB - Instalador completo
```

### **Características del Ejecutable**
- ✅ **Autocontenido**: No requiere Python en el sistema destino
- ✅ **Privilegios**: Solicita automáticamente permisos de administrador
- ✅ **Archivos Embebidos**: Incluye todos los archivos del agente
- ✅ **Interfaz Gráfica**: GUI para configuración de token
- ✅ **Validación**: Verificación en tiempo real del token
- ✅ **Instalación Completa**: Servicio de Windows + configuración

---

## 🧹 **Scripts de Limpieza** {#scripts-limpieza}

### **1. Limpieza Completa de Assets**

#### **Script Principal**
```
📁 C:\lanet-helpdesk-v3\ELIMINAR_TODOS_ASSETS.py
```

#### **Uso**
```bash
cd C:\lanet-helpdesk-v3
python ELIMINAR_TODOS_ASSETS.py
```

#### **Funcionalidad**
- Elimina TODOS los assets de la base de datos
- Limpia tablas relacionadas:
  - `agent_token_usage_history`
  - `asset_software`
  - `asset_hardware`
  - `asset_network`
  - `asset_bitlocker`
  - `asset_heartbeats`
  - `assets`
- Confirmación antes de eliminar
- Verificación post-limpieza

### **2. Limpieza de Agente Local**

#### **Script de Limpieza Manual**
```
📁 C:\lanet-helpdesk-v3\production_installer\LIMPIAR_AGENTE_MANUAL.bat
```

#### **Uso**
```bash
# Clic derecho → "Ejecutar como administrador"
C:\lanet-helpdesk-v3\production_installer\LIMPIAR_AGENTE_MANUAL.bat
```

#### **Funcionalidad**
- Detiene servicio LANETAgent
- Elimina servicio del sistema
- Borra archivos de instalación:
  - `C:\Program Files\LANET Agent`
  - `C:\ProgramData\LANET Agent`
  - Carpetas de usuario
- Limpia registro de Windows
- Instrucciones para limpieza de BD

### **3. Script de Limpieza de Tokens**

#### **Script Principal**
```
📁 C:\lanet-helpdesk-v3\LIMPIAR_TOKENS_AGENTE.py
```

#### **Uso**
```bash
cd C:\lanet-helpdesk-v3
python LIMPIAR_TOKENS_AGENTE.py
```

#### **Funcionalidades**
1. **Mostrar Tokens Existentes**
   - Lista todos los tokens con detalles
   - Estado (activo/inactivo)
   - Cliente y sitio asociado
   - Fechas de creación y uso

2. **Opciones de Limpieza**
   - Eliminar TODOS los tokens
   - Eliminar tokens específicos (selección)
   - Limpiar historial de uso
   - Limpieza completa (tokens + historial)

3. **Confirmaciones de Seguridad**
   - Confirmación antes de eliminar
   - Verificación post-limpieza
   - Manejo de errores con rollback

#### **Ejemplo de Uso**
```
📋 Tokens encontrados: 3
--------------------------------------------------------------------------------
 1. LANET-75F6-EC23-85DC9D
    Cliente: Test Client
    Sitio: Oficina Principal
    Estado: ✅ Activo
    Creado: 2025-07-29 15:30
    Usado: 2025-07-29 20:15

📋 Opciones de limpieza:
1. Eliminar TODOS los tokens
2. Eliminar tokens específicos
3. Limpiar historial de uso de tokens
4. Limpieza completa (tokens + historial)
5. Cancelar

Selecciona una opción (1-5): 2
Selección: 1,3
✅ Token eliminado: LANET-75F6-EC23-85DC9D
✅ Eliminados 2 tokens exitosamente
```

---

## 🚀 **Desarrollo y Mantenimiento** {#desarrollo}

### **Estructura de Desarrollo**

#### **Entorno de Desarrollo**
```bash
# Activar entorno virtual
cd C:\lanet-helpdesk-v3
.venv\Scripts\activate

# Instalar dependencias
pip install -r production_installer\agent_files\requirements.txt
```

#### **Dependencias del Agente**
```
# production_installer/agent_files/requirements.txt
requests>=2.28.0
psycopg2-binary>=2.9.0
pywin32>=305
psutil>=5.9.0
python-wmi>=1.5.1
pystray>=0.19.0
Pillow>=9.0.0
```

### **Flujo de Desarrollo**

#### **1. Modificar Código del Agente**
```bash
# Editar archivos en:
C:\lanet-helpdesk-v3\production_installer\agent_files\
```

#### **2. Probar en Desarrollo**
```bash
cd C:\lanet-helpdesk-v3\production_installer\agent_files
python main.py --debug --no-ui
```

#### **3. Compilar Nuevo Instalador**
```bash
cd C:\lanet-helpdesk-v3\production_installer
python build_standalone_installer.py
```

#### **4. Probar Instalador**
```bash
# Limpiar instalación anterior
LIMPIAR_AGENTE_MANUAL.bat

# Probar nuevo instalador
deployment\LANET_Agent_Installer.exe
```

### **Puntos de Extensión**

#### **Agregar Nuevo Módulo**
1. Crear archivo en `agent_files/modules/nuevo_modulo.py`
2. Implementar clase con métodos `start()` y `stop()`
3. Registrar en `agent_core.py`
4. Recompilar instalador

#### **Modificar UI**
1. Editar archivos en `agent_files/ui/`
2. Mantener compatibilidad con `system_tray.py`
3. Probar con `--debug` para ver errores
4. Recompilar instalador

#### **Agregar Configuración**
1. Modificar `agent_files/config/agent_config.json`
2. Actualizar `config_manager.py` si es necesario
3. Documentar nuevas opciones
4. Recompilar instalador

### **Testing**

#### **Pruebas Locales**
```bash
# Modo debug (sin servicio)
python main.py --debug --no-ui

# Modo test (con validaciones)
python main.py --test

# Registro manual
python main.py --register LANET-XXXX-XXXX-XXXXXX
```

#### **Pruebas de Instalación**
```bash
# Limpiar entorno
python ..\ELIMINAR_TODOS_ASSETS.py
LIMPIAR_AGENTE_MANUAL.bat

# Instalar y verificar
deployment\LANET_Agent_Installer.exe
```

---

## 🔧 **Troubleshooting** {#troubleshooting}

### **Problemas Comunes**

#### **1. Error de Compilación**
```
❌ PyInstaller not found
```
**Solución:**
```bash
pip install pyinstaller
```

#### **2. Archivos del Agente No Encontrados**
```
❌ Agent files not found
```
**Causas y Soluciones:**

**Causa A: Directorio agent_files/ no existe**
```bash
# Verificar estructura
ls production_installer/agent_files/
```
**Solución:** Asegurar que existe la estructura completa de `agent_files/`

**Causa B: Embedding falló durante la compilación**
```bash
# Verificar que se creó el archivo temporal
ls production_installer/standalone_installer_embedded.py
```
**Solución:** Recompilar completamente:
```bash
cd production_installer
rm -f standalone_installer_embedded.py  # Limpiar temporal
python build_standalone_installer.py    # Recompilar
```

**Causa C: PyInstaller no incluyó los archivos**
```bash
# Verificar configuración en build_standalone_installer.py línea 206
datas=[('agent_files', 'agent_files')]
```
**Solución:** Verificar que la línea 206 tenga la configuración correcta

#### **3. Instalador Muy Pequeño (< 50MB)**
```
⚠️ Instalador de solo 14MB - archivos no embebidos
```
**Diagnóstico:**
- Instalador sin archivos del agente: ~14MB
- Instalador completo con archivos: ~90MB

**Solución:**
```bash
# Verificar que agent_files/ tiene contenido
du -sh production_installer/agent_files/

# Recompilar forzando embedding
cd production_installer
python build_standalone_installer.py
```

#### **3. Servicio No Se Instala**
```
❌ Failed to start service: OpenService ERROR 1060
```
**Solución:**
- Ejecutar instalador como administrador
- Verificar que Python esté instalado en el sistema
- Revisar logs en `C:\ProgramData\LANET Agent\Logs\`

#### **4. Token No Válido**
```
❌ Token validation failed
```
**Solución:**
- Verificar formato: `LANET-XXXX-XXXX-XXXXXX`
- Confirmar que el token existe en la base de datos
- Verificar conectividad con `https://helpdesk.lanet.mx/api`

### **Logs y Diagnóstico**

#### **Ubicaciones de Logs**
```
# Instalador
C:\Users\[USER]\AppData\Local\Temp\LANET_Installer\

# Agente (después de instalación)
C:\ProgramData\LANET Agent\Logs\
C:\Program Files\LANET Agent\logs\
```

#### **Comandos de Diagnóstico**
```bash
# Verificar servicio
sc query LANETAgent

# Ver logs del servicio
Get-WinEvent -LogName System | Where-Object {$_.ProviderName -eq "Service Control Manager"}

# Verificar archivos instalados
dir "C:\Program Files\LANET Agent"
```

### **Limpieza para Reinstalación**

#### **Limpieza Completa**
```bash
# 1. Limpiar agente local
LIMPIAR_AGENTE_MANUAL.bat

# 2. Limpiar base de datos
python ELIMINAR_TODOS_ASSETS.py
python LIMPIAR_TOKENS_AGENTE.py

# 3. Reinstalar
deployment\LANET_Agent_Installer.exe
```

---

## 📝 **Notas Importantes**

### **Seguridad**
- El agente requiere privilegios SYSTEM para acceder a BitLocker
- Todas las comunicaciones usan HTTPS
- Los tokens tienen formato específico para validación

### **Compatibilidad**
- Windows 10/11 (64-bit)
- Python 3.8+ (para desarrollo)
- .NET Framework 4.7.2+ (para pywin32)

### **Rendimiento**
- Heartbeat cada 5 minutos
- Monitoreo completo cada hora
- Base de datos local SQLite para cache
- Compresión de datos antes de envío

### **Mantenimiento**
- Logs rotan automáticamente (7 días)
- Base de datos local se limpia periódicamente
- Actualizaciones via nuevo instalador

---

## 📋 **REFERENCIA RÁPIDA**

### **Comandos Esenciales**
```bash
# Compilar instalador
cd C:\lanet-helpdesk-v3\production_installer
python build_standalone_installer.py

# Herramientas maestras
cd C:\lanet-helpdesk-v3
python LANET_AGENT_TOOLS.py

# Limpiar para pruebas
python ELIMINAR_TODOS_ASSETS.py
python LIMPIAR_TOKENS_AGENTE.py

# Verificar estado
python VERIFICAR_ESTADO_AGENTE.py
```

### **Ubicaciones Críticas**
```
📁 Códigos Fuente:     production_installer/agent_files/
📁 Script Compilación: production_installer/build_standalone_installer.py
📁 Instalador Final:   production_installer/deployment/LANET_Agent_Installer.exe
📁 Documentación:      LANET_AGENT_V3_DOCUMENTATION.md
📁 Herramientas:       LANET_AGENT_TOOLS.py
```

### **Archivos de Configuración**
```
⚙️ Agente:     production_installer/agent_files/config/agent_config.json
⚙️ Build:      production_installer/build_standalone_installer.py (línea 206)
⚙️ PyInstaller: Generado automáticamente como .spec
```

### **Tamaños de Referencia**
```
📏 Instalador Completo:  ~90MB (con archivos del agente)
📏 Instalador Vacío:     ~14MB (sin archivos del agente)
📏 Agent Files:          ~5-10MB (código fuente)
```

### **Proceso de Desarrollo**
```
1. Modificar → production_installer/agent_files/
2. Probar    → python main.py --debug
3. Compilar  → python build_standalone_installer.py
4. Limpiar   → Scripts de limpieza
5. Instalar  → LANET_Agent_Installer.exe
6. Verificar → python VERIFICAR_ESTADO_AGENTE.py
```

---

**Documentación actualizada:** 30 de Julio, 2025
**Versión del Agente:** 3.0
**Estado:** Producción - Funcional ✅
**Ubicación:** `C:\lanet-helpdesk-v3\LANET_AGENT_V3_DOCUMENTATION.md`
