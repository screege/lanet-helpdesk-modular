# LANET HELPDESK AGENT - DOCUMENTACIÓN COMPLETA Y CONTEXTO

## 📁 1. UBICACIÓN DEL CÓDIGO FUENTE DEL AGENTE

### Agente Principal (FUNCIONANDO):
```
C:\lanet-helpdesk-v3\production_installer\agent_files\
├── main.py                           # Ejecutable principal del agente (FUNCIONA)
├── modules\
│   ├── bitlocker.py                  # Recolección de datos BitLocker
│   ├── monitoring.py                 # Monitoreo del sistema e inventario
│   ├── hardware.py                   # Detección de hardware
│   ├── software.py                   # Inventario de software
│   └── network.py                    # Utilidades de red
├── core\
│   ├── agent_core.py                 # Funcionalidad principal del agente
│   ├── config_manager.py             # Gestión de configuración
│   ├── database.py                   # Operaciones de base de datos
│   └── heartbeat.py                  # Heartbeat y comunicación
├── ui\
│   └── main_window.py                # Interfaz gráfica (opcional)
└── config\
    └── agent_config.json             # Plantilla de configuración
```

**Estado:** ✅ COMPLETAMENTE FUNCIONAL - Recolecta hardware, software y datos de BitLocker cuando se ejecuta con privilegios de administrador.

## 📦 2. UBICACIONES DE PAQUETES DE DESPLIEGUE

### Despliegue Empresarial (Más Reciente):
```
C:\lanet-helpdesk-v3\enterprise_deployment\
├── Install_LANET_Agent.bat                    # Instalador de un clic para técnicos
├── LANET_Agent_Professional_Installer.ps1     # Instalador GUI con validación de token
├── LANET_Agent_Silent_Enterprise.ps1          # Script de despliegue silencioso
├── Deploy_Mass_Installation.ps1               # Herramienta de despliegue masivo
├── ENTERPRISE_DEPLOYMENT_GUIDE.md             # Documentación completa
└── TECHNICIAN_QUICK_START.md                  # Referencia rápida
```

### Despliegue de Producción (Anterior):
```
C:\lanet-helpdesk-v3\production_deployment\
├── LANET_Agent_Enterprise_Installer.bat       # Instalador batch
├── LANET_Agent_Enterprise_Installer.ps1       # Instalador PowerShell
├── Deploy_LANET_Agent_Silent.bat             # Despliegue silencioso
├── DEPLOYMENT_GUIDE.md                       # Documentación
└── TECHNICIAN_INSTRUCTIONS.md                # Guía rápida
```

## 🗄️ 3. ESQUEMA DE BASE DE DATOS Y DETALLES DE CONEXIÓN

### Detalles de Conexión:
```
Host: localhost
Base de datos: lanet_helpdesk
Usuario: postgres
Contraseña: Poikl55+*
Cadena de conexión: postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk
```

### Tablas Clave para Operaciones del Agente:

#### Tabla assets:
```sql
CREATE TABLE assets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    asset_type VARCHAR(50) DEFAULT 'computer',
    client_id INTEGER REFERENCES clients(id),
    site_id INTEGER REFERENCES sites(id),
    specifications JSONB,           -- Datos de hardware, software, BitLocker
    last_seen TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### Tabla agent_tokens:
```sql
CREATE TABLE agent_tokens (
    id SERIAL PRIMARY KEY,
    token VARCHAR(255) UNIQUE NOT NULL,
    client_id INTEGER REFERENCES clients(id),
    site_id INTEGER REFERENCES sites(id),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);
```

#### Tabla agent_token_usage_history:
```sql
CREATE TABLE agent_token_usage_history (
    id SERIAL PRIMARY KEY,
    token_id INTEGER REFERENCES agent_tokens(id),
    asset_id INTEGER REFERENCES assets(id),
    used_at TIMESTAMP DEFAULT NOW(),
    computer_name VARCHAR(255),
    ip_address INET
);
```

### Políticas RLS:
- **Superadmin/Técnico:** Acceso completo a todos los datos
- **Admin Cliente:** Acceso solo a los datos de su organización
- **Solicitante:** Acceso solo a sitios asignados

## 🏗️ 4. DOCUMENTACIÓN DE ARQUITECTURA DEL AGENTE

### Proceso de Registro del Agente:
1. **Validación de Token:** El agente envía token a `/api/agents/register-with-token`
2. **Respuesta del Servidor:** Devuelve client_id, site_id y configuración
3. **Creación de Asset:** Crea o actualiza registro de asset en base de datos
4. **Configuración de Heartbeat:** Establece horario de comunicación regular

### Requisitos para Recolección de Datos BitLocker:
- **CRÍTICO:** El agente DEBE ejecutarse con privilegios **SYSTEM** (no solo Administrador)
- **Servicio de Windows:** Requerido para acceso con privilegios SYSTEM
- **Cuenta de Servicio:** Debe configurarse como `LocalSystem`
- **Acceso PowerShell:** Requiere acceso al cmdlet `Get-BitLockerVolume`
- **Datos Recolectados:** Claves de recuperación, estado de cifrado, información de volúmenes

### Configuración del Servicio de Windows:
```
Nombre del Servicio: LANETAgent
Nombre para Mostrar: LANET Helpdesk Agent
Cuenta: LocalSystem (privilegios SYSTEM)
Tipo de Inicio: Automático
Dependencias: Ninguna
Ruta Binaria: "python.exe" "C:\Program Files\LANET Agent\service_wrapper.py"
```

### Endpoints de API:
- **Registro:** `POST /api/agents/register-with-token`
- **Heartbeat:** `POST /api/agents/heartbeat`
- **Verificación de Salud:** `GET /api/health`
- **Validación de Token:** `POST /api/agents/validate-token`

### Estructura de Datos Enviada al Servidor:
```json
{
    "token": "LANET-CLIENT-SITE-TOKEN",
    "computer_name": "NOMBRE-COMPUTADORA",
    "hardware_info": {
        "cpu": {...},
        "memory": {...},
        "disks": [...],
        "bitlocker": {
            "supported": true,
            "total_volumes": 1,
            "protected_volumes": 1,
            "volumes": [
                {
                    "volume_letter": "C:",
                    "protection_status": "Protected",
                    "recovery_key": "190443-417890-133936..."
                }
            ]
        }
    },
    "software_info": [...],
    "system_metrics": {...}
}
```

## ⚠️ 5. PROBLEMAS ACTUALES Y CONTEXTO

### Problemas de Instalación del Servicio:
1. **Problemas de Ruta de Python:** El servicio no puede encontrar el ejecutable de Python
2. **Directorio de Trabajo:** El servicio inicia en directorio incorrecto
3. **Fallas de Importación de Módulos:** La ruta de Python no está configurada correctamente
4. **Escalación de Privilegios:** El servicio no se ejecuta con privilegios SYSTEM

### Lo que Funciona:
- **Ejecución Directa:** `python main.py --register TOKEN` funciona perfectamente cuando se ejecuta como Administrador
- **Recolección de Datos:** Todos los módulos (hardware, software, BitLocker) funcionan correctamente
- **Comunicación con Servidor:** Las llamadas API y heartbeat funcionan correctamente

### Lo que No Funciona:
- **Servicio de Windows:** La creación del servicio tiene éxito pero el servicio no inicia
- **Inicio Automático:** El servicio no inicia automáticamente al arrancar
- **Privilegios SYSTEM:** El servicio actual no se ejecuta con privilegios apropiados para BitLocker

### Configuración Requerida del Servicio de Windows:
```python
# El wrapper del servicio necesita:
import sys
import os
from pathlib import Path

# Configuración apropiada de rutas
agent_dir = Path("C:/Program Files/LANET Agent")
sys.path.insert(0, str(agent_dir))
sys.path.insert(0, str(agent_dir / "modules"))
sys.path.insert(0, str(agent_dir / "core"))

# Cambiar directorio de trabajo
os.chdir(str(agent_dir))

# Importar y ejecutar agente
from main import main as agent_main
sys.argv = ['main.py', '--register', 'TOKEN']
agent_main()
```

## 📋 6. MANIFIESTO COMPLETO DE ARCHIVOS

### Archivos del Agente Principal (FUNCIONANDO):
```
C:\lanet-helpdesk-v3\production_installer\agent_files\
├── main.py                           # ✅ Ejecutable principal
├── modules\
│   ├── __init__.py
│   ├── bitlocker.py                  # ✅ Recolección BitLocker
│   ├── monitoring.py                 # ✅ Monitoreo del sistema
│   ├── hardware.py                   # ✅ Detección de hardware
│   ├── software.py                   # ✅ Inventario de software
│   ├── network.py                    # ✅ Utilidades de red
│   └── system_info.py               # ✅ Información del sistema
├── core\
│   ├── __init__.py
│   ├── agent_core.py                 # ✅ Funcionalidad principal
│   ├── config_manager.py             # ✅ Configuración
│   ├── database.py                   # ✅ Operaciones de base de datos
│   └── heartbeat.py                  # ✅ Comunicación
├── ui\
│   ├── __init__.py
│   └── main_window.py                # ✅ Interfaz gráfica
└── config\
    └── agent_config.json             # ✅ Plantilla de configuración
```

### Scripts de Despliegue:
```
C:\lanet-helpdesk-v3\enterprise_deployment\
├── Install_LANET_Agent.bat                    # ❌ Necesita arreglo
├── LANET_Agent_Professional_Installer.ps1     # ❌ Problemas de servicio
├── LANET_Agent_Silent_Enterprise.ps1          # ❌ Problemas de servicio
└── Deploy_Mass_Installation.ps1               # ❌ Problemas de servicio
```

### Archivos de Configuración:
```
C:\lanet-helpdesk-v3\
├── .env                              # ✅ Variables de entorno
├── backend\config\database.py        # ✅ Configuración de base de datos
└── frontend\src\config\api.js        # ✅ Configuración de API
```

### Archivos de API del Backend:
```
C:\lanet-helpdesk-v3\backend\
├── app.py                            # ✅ Aplicación Flask principal
├── routes\
│   ├── agents.py                     # ✅ Endpoints de API del agente
│   └── assets.py                     # ✅ Gestión de assets
└── models\
    ├── asset.py                      # ✅ Modelo de asset
    └── agent_token.py                # ✅ Modelo de token
```

## 🎯 FACTORES CRÍTICOS DE ÉXITO PARA NUEVA IMPLEMENTACIÓN

### Debe Tener:
1. **Privilegios SYSTEM:** El servicio DEBE ejecutarse como cuenta LocalSystem
2. **Ruta de Python Apropiada:** El servicio debe encontrar Python y todos los módulos
3. **Directorio de Trabajo:** El servicio debe iniciar en directorio correcto
4. **Importaciones de Módulos:** Todos los módulos del agente deben ser importables
5. **Validación de Token:** Pruebas de conectividad del servidor en tiempo real

### Comando Comprobado que Funciona:
```cmd
# Este comando funciona perfectamente:
python "C:\lanet-helpdesk-v3\production_installer\agent_files\main.py" --register LANET-75F6-EC23-85DC9D
```

### Plantilla de Wrapper del Servicio:
```python
import sys
import os
import logging
from pathlib import Path

# Configurar rutas
agent_dir = Path(r"C:\Program Files\LANET Agent")
sys.path.insert(0, str(agent_dir))
sys.path.insert(0, str(agent_dir / "modules"))
sys.path.insert(0, str(agent_dir / "core"))

# Cambiar directorio de trabajo
os.chdir(str(agent_dir))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(r"C:\ProgramData\LANET Agent\Logs\service.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('lanet_service')

def main():
    try:
        logger.info('🚀 Servicio LANET Agent iniciando con privilegios SYSTEM')

        # Importar y ejecutar agente
        from main import main as agent_main

        # Establecer token de registro
        sys.argv = ['main.py', '--register', 'LANET-75F6-EC23-85DC9D']

        # Ejecutar agente
        agent_main()

    except Exception as e:
        logger.error(f'Error del servicio: {e}', exc_info=True)

if __name__ == '__main__':
    main()
```

## 📞 PRÓXIMOS PASOS PARA NUEVO AGENTE AI

1. **Enfocarse en Creación de Servicio de Windows:** El código del agente funciona perfectamente, solo necesita arreglar la instalación del servicio
2. **Usar Archivos de Agente Existentes:** No recrear el agente, usar los archivos que funcionan en `production_installer\agent_files\`
3. **Implementar Wrapper de Servicio Apropiado:** Crear un wrapper de servicio Python que maneje rutas e importaciones correctamente
4. **Probar con Privilegios SYSTEM:** Asegurar que el servicio se ejecute como LocalSystem para acceso BitLocker
5. **Validar Instalación:** Verificar que el servicio inicie automáticamente y recolecte datos BitLocker

**El agente es 100% funcional - solo el proceso de instalación del servicio de Windows necesita ser arreglado.**

## 🔧 COMANDO DE INSTALACIÓN MANUAL QUE FUNCIONA

Para instalar manualmente el agente que funciona:

1. **Abrir PowerShell como Administrador**
2. **Ejecutar:**
```powershell
cd "C:\lanet-helpdesk-v3\production_installer\agent_files"
python main.py --register LANET-75F6-EC23-85DC9D
```
3. **El agente se registrará y comenzará a recolectar datos**
4. **Aparecerá en el frontend en 2-3 minutos con datos completos de BitLocker**

## 📊 DATOS QUE RECOLECTA EL AGENTE

- **Hardware:** CPU, RAM, discos, placa madre, BIOS
- **Software:** Lista completa de programas instalados
- **BitLocker:** Claves de recuperación y estado de cifrado
- **Métricas:** Uso de CPU, memoria, espacio en disco, estado de red
- **Tiempo Real:** Monitoreo continuo con heartbeats cada 5 minutos

## 🏁 RESULTADO ESPERADO

Después del despliegue exitoso:
- ✅ Servicio ejecutándose como SYSTEM con auto-inicio
- ✅ Computadora aparece en helpdesk en 5-10 minutos
- ✅ Inventario completo de hardware recolectado
- ✅ Inventario completo de software con todos los programas
- ✅ Datos BitLocker incluyendo claves de recuperación
- ✅ Monitoreo en tiempo real con heartbeats cada 5 minutos
```
