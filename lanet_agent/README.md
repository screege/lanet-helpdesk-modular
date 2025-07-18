# 🖥️ LANET Helpdesk V3 - Windows Client Agent

## 📋 Descripción

El **LANET Agent** es un cliente Windows que se integra completamente con el backend de LANET Helpdesk V3. Permite a los usuarios finales crear tickets directamente desde su equipo, además de proporcionar monitoreo automático del sistema y comunicación constante con el backend.

## ✨ Características Principales

- 🔐 **Registro automático** con token de instalación
- 💓 **Heartbeat periódico** con el backend (cada 60 segundos)
- 📊 **Monitoreo de sistema** en tiempo real (CPU, memoria, disco, red)
- 🎫 **Creación de tickets** directamente desde el agente
- 🖱️ **Interfaz de bandeja del sistema** con menú contextual
- 📈 **Información automática** del sistema incluida en tickets
- 🔄 **Sincronización automática** con el backend
- 🪟 **Ventanas de estado** y gestión de tickets

## 🛠️ Requisitos del Sistema

- **Sistema Operativo:** Windows 10/11 (64-bit)
- **Python:** 3.11+ (para desarrollo)
- **Memoria:** 100 MB RAM mínimo
- **Disco:** 50 MB espacio libre
- **Red:** Conexión a Internet para comunicación con backend

## 🚀 Instalación Rápida

### Para Usuarios Finales (Ejecutable)

1. **Descargar** el ejecutable `LANET_Agent.exe`
2. **Ejecutar** `install_agent.bat` como administrador
3. **Registrar** el agente con el token proporcionado:
   ```cmd
   "C:\Program Files\LANET Agent\LANET_Agent.exe" --register LANET-550E-660E-AEB0F9
   ```
4. **Iniciar** el agente desde el menú inicio o escritorio

### Para Desarrolladores (Código Fuente)

1. **Clonar** el repositorio
2. **Instalar** dependencias:
   ```bash
   cd lanet_agent
   pip install -r requirements.txt
   ```
3. **Configurar** el entorno (opcional):
   ```bash
   # Editar config/agent_config.json si es necesario
   ```
4. **Probar** el agente:
   ```bash
   python test_agent.py
   ```
5. **Registrar** con token:
   ```bash
   python main.py --register LANET-550E-660E-AEB0F9
   ```
6. **Ejecutar** el agente:
   ```bash
   python main.py
   ```

## 🔧 Configuración

### Archivo de Configuración

El agente utiliza `config/agent_config.json` para su configuración:

```json
{
  "server": {
    "base_url": "http://localhost:5001/api",
    "production_url": "https://helpdesk.lanet.mx/api",
    "environment": "development"
  },
  "agent": {
    "heartbeat_interval": 60,
    "inventory_interval": 3600,
    "version": "1.0.0"
  },
  "ui": {
    "show_notifications": true,
    "language": "es"
  }
}
```

### Variables de Entorno

Puedes sobrescribir configuraciones usando variables de entorno:

```bash
set LANET_AGENT_SERVER_ENVIRONMENT=production
set LANET_AGENT_AGENT_HEARTBEAT_INTERVAL=30
```

## 🎫 Token de Registro Verificado

**Token de Prueba:** `LANET-550E-660E-AEB0F9`

- **Cliente:** Cafe Mexico S.A. de C.V.
- **Sitio:** Oficina Principal CDMX
- **Estado:** ✅ Activo y verificado
- **Expira:** 13/9/2025

## 🖱️ Uso del Sistema Tray

Una vez iniciado, el agente aparece en la bandeja del sistema con un icono que cambia según el estado:

- 🟢 **Verde:** Agente online, sistema normal
- 🟡 **Amarillo:** Agente online, alertas menores
- 🔴 **Rojo:** Agente offline o errores críticos

### Menú Contextual

Click derecho en el icono para acceder a:

```
🖥️ LANET Helpdesk Agent
├── 📊 Estado del Equipo
├── 🎫 Crear Ticket
├── 📋 Mis Tickets
├── ⚙️ Configuración
├── 📄 Ver Logs
├── 🔄 Forzar Sincronización
├── ℹ️ Acerca de
└── ❌ Salir
```

## 🎫 Creación de Tickets

### Desde el Agente

1. **Click derecho** en el icono del agente
2. **Seleccionar** "🎫 Crear Ticket"
3. **Completar** el formulario:
   - Asunto (obligatorio)
   - Descripción (obligatorio)
   - Prioridad (baja/media/alta/crítica)
   - Incluir información del sistema (recomendado)
4. **Click** en "Crear Ticket"

### Información Automática Incluida

Cuando se marca "Incluir información del sistema", el agente añade automáticamente:

- Nombre del equipo
- Usuario actual
- Sistema operativo y versión
- Métricas actuales (CPU, memoria, disco)
- Estado de la red
- Procesos con alto uso de CPU
- Eventos recientes del sistema

## 📊 Monitoreo del Sistema

El agente recopila métricas cada 5 minutos:

- **CPU:** Porcentaje de uso
- **Memoria:** Porcentaje de uso y total
- **Disco:** Porcentaje de uso y espacio libre
- **Red:** Estado de conectividad
- **Procesos:** Cantidad de procesos activos
- **Usuarios:** Sesiones activas
- **Antivirus:** Estado (Windows Defender)
- **Actualizaciones:** Pendientes de Windows

## 🔧 Desarrollo y Compilación

### Estructura del Proyecto

```
lanet_agent/
├── main.py                    # Punto de entrada
├── core/                      # Módulos principales
│   ├── agent_core.py         # Servicio principal
│   ├── config_manager.py     # Gestión de configuración
│   ├── database.py           # Base de datos local
│   └── logger.py             # Sistema de logging
├── modules/                   # Módulos funcionales
│   ├── registration.py       # Registro con token
│   ├── heartbeat.py          # Comunicación periódica
│   ├── monitoring.py         # Monitoreo del sistema
│   └── ticket_creator.py     # Creación de tickets
├── ui/                       # Interfaz de usuario
│   ├── system_tray.py        # Bandeja del sistema
│   ├── ticket_window.py      # Ventana de tickets
│   ├── status_window.py      # Ventana de estado
│   └── tickets_list.py       # Lista de tickets
├── config/                   # Configuración
├── assets/                   # Iconos y recursos
└── requirements.txt          # Dependencias
```

### Compilar Ejecutable

```bash
# Instalar PyInstaller
pip install pyinstaller

# Compilar agente
python build_agent.py
```

Esto genera:
- `dist/LANET_Agent.exe` - Ejecutable principal
- `dist/install_agent.bat` - Script de instalación
- `dist/README.txt` - Documentación

### Ejecutar Tests

```bash
# Tests completos
python test_agent.py

# Test específico
python main.py --test

# Modo debug
python main.py --debug
```

## 🔗 Integración con Backend

### APIs Utilizadas

- `POST /api/agents/register-with-token` - Registro inicial
- `POST /api/agents/heartbeat` - Heartbeat periódico
- `POST /api/tickets/create-from-agent` - Crear tickets
- `POST /api/tickets/` - Fallback para tickets

### Autenticación

1. **Registro:** Token de instalación → JWT del agente
2. **Comunicación:** JWT en header `Authorization: Bearer {token}`
3. **Renovación:** Automática antes de expiración

## 📝 Logs y Debugging

### Ubicación de Logs

- **Desarrollo:** `logs/agent.log`
- **Producción:** `C:\Program Files\LANET Agent\logs\agent.log`

### Niveles de Log

- **INFO:** Operaciones normales
- **WARNING:** Alertas y problemas menores
- **ERROR:** Errores que requieren atención
- **DEBUG:** Información detallada para debugging

### Ver Logs

```bash
# Desde el agente
Click derecho → "📄 Ver Logs"

# Desde línea de comandos
tail -f logs/agent.log
```

## 🚨 Solución de Problemas

### Problemas Comunes

1. **Agente no se registra**
   - Verificar conectividad de red
   - Verificar que el backend esté ejecutándose
   - Verificar que el token sea válido

2. **Heartbeat falla**
   - Verificar configuración del servidor
   - Verificar certificados SSL
   - Verificar firewall/proxy

3. **No aparece en bandeja del sistema**
   - Verificar que pystray esté instalado
   - Verificar permisos de Windows
   - Ejecutar como administrador

### Comandos de Diagnóstico

```bash
# Test completo
python main.py --test

# Verificar configuración
python -c "from core.config_manager import ConfigManager; c=ConfigManager(); print(c.get_server_url())"

# Test de conectividad
python -c "import requests; print(requests.get('http://localhost:5001/api/health').status_code)"
```

## 📞 Soporte

Para soporte técnico:

1. **Crear ticket** desde el agente
2. **Contactar** a LANET Systems
3. **Revisar logs** para información detallada
4. **Ejecutar tests** para diagnóstico

---

## 📄 Licencia

© 2025 LANET Systems. Todos los derechos reservados.

---

**¡El agente está listo para usar con el token verificado `LANET-550E-660E-AEB0F9`!**
