# 🚀 LANET Helpdesk V3 - Frontend

Sistema profesional de mesa de ayuda MSP con interfaz completamente en español (México).

## 📋 Descripción

Frontend React completamente funcional para el sistema MSP LANET Helpdesk V3. Incluye autenticación JWT, gestión de tickets, clientes, y panel de control en tiempo real con integración completa al backend PostgreSQL.

## 🛠️ Tecnologías

- **React 18** con TypeScript
- **Vite** para desarrollo rápido
- **Tailwind CSS** para estilos
- **React Router** para navegación
- **Axios** para llamadas API
- **Lucide React** para iconos

## 🌐 Características Principales

### ✅ Sistema de Autenticación
- Inicio de sesión con JWT
- Renovación automática de tokens
- Control de acceso basado en roles
- Cierre de sesión seguro

### ✅ Panel Principal (Dashboard)
- Métricas en tiempo real
- Acciones rápidas funcionales
- Estado del sistema
- Cumplimiento SLA

### ✅ Gestión de Tickets
- Formulario completo de creación
- Búsqueda y filtrado en tiempo real
- Estados y prioridades en español
- Selección de cliente/sitio/dispositivo

### ✅ Gestión de Clientes
- Formulario completo de creación
- Información de contacto y dirección
- Estados activo/inactivo
- Búsqueda funcional

### ✅ Localización Española (México)
- Interfaz 100% en español
- Formato de fechas mexicano
- Terminología profesional MSP
- Mensajes de error localizados

## 🚀 Instalación y Configuración

### Prerrequisitos
- Node.js 18+ 
- npm o yarn
- Backend Flask ejecutándose en puerto 5000

### Instalación
```bash
cd frontend
npm install
```

### Desarrollo
```bash
npm run dev
```
La aplicación estará disponible en http://localhost:5173/

### Construcción para Producción
```bash
npm run build
```

## 🔐 Credenciales de Demostración

| Rol | Email | Contraseña |
|-----|-------|------------|
| Administrador | `admin@test.com` | `TestAdmin123!` |
| Técnico | `tech@test.com` | `TestTech123!` |
| Admin Cliente | `admin@richardsoninc.com` | `TestClient123!` |
| Contacto Cliente | `contact1@richardsoninc.com` | `TestContact123!` |

## 📁 Estructura del Proyecto

```
src/
├── components/
│   ├── auth/
│   │   └── ProtectedRoute.tsx
│   └── layout/
│       └── DashboardLayout.tsx
├── contexts/
│   ├── ApiContext.tsx
│   └── AuthContext.tsx
├── pages/
│   ├── Dashboard.tsx
│   ├── LoginPage.tsx
│   ├── TicketsPage.tsx
│   ├── CreateTicketPage.tsx
│   ├── ClientsPage.tsx
│   ├── CreateClientPage.tsx
│   ├── UsersPage.tsx
│   └── SettingsPage.tsx
├── App.tsx
└── main.tsx
```

## 🔧 Configuración de API

El frontend se conecta automáticamente al backend en `http://localhost:5000`. Para cambiar la URL:

1. Editar `src/contexts/ApiContext.tsx`
2. Modificar la variable `API_BASE_URL`

## 🎨 Personalización

### Colores y Temas
Los colores principales se definen en `tailwind.config.js`:
- Primary: Azul profesional
- Secondary: Gris neutro
- Success: Verde
- Warning: Amarillo
- Error: Rojo

### Componentes
Todos los componentes siguen el patrón de diseño consistente con:
- Tarjetas (cards) para contenido
- Botones primarios y secundarios
- Campos de entrada estandarizados
- Estados de carga y error

## 🌍 Internacionalización

El sistema está completamente localizado para **español (México)**:
- Formato de fechas: `dd/mm/yyyy`
- Zona horaria: `America/Mexico_City`
- Moneda: Peso mexicano (MXN)
- Terminología MSP profesional

## 🔄 Estado de Desarrollo

### ✅ Completado
- [x] Autenticación y autorización
- [x] Dashboard con datos reales
- [x] Gestión de tickets funcional
- [x] Gestión de clientes funcional
- [x] Localización española completa
- [x] Navegación y rutas
- [x] Manejo de errores
- [x] Diseño responsivo

### 🚧 En Desarrollo
- [ ] Gestión de usuarios completa
- [ ] Configuraciones avanzadas
- [ ] Reportes y analytics
- [ ] Notificaciones en tiempo real

## 🐛 Solución de Problemas

### Página en Blanco
Si la aplicación muestra una página en blanco:
1. Verificar que el backend esté ejecutándose
2. Revisar la consola del navegador para errores
3. Confirmar que las credenciales de API sean correctas

### Errores de CORS
Si hay errores de CORS:
1. Verificar que el backend tenga configurado CORS para `http://localhost:5173`
2. Revisar la configuración en `backend/app.py`

### Problemas de Autenticación
Si el login no funciona:
1. Verificar que el backend esté respondiendo en `/api/auth/login`
2. Confirmar que las credenciales sean correctas
3. Revisar los logs del backend para errores

## 📞 Soporte

Para soporte técnico o preguntas sobre el desarrollo, contactar al equipo de desarrollo de Lanet Systems.

## 🔄 Historial de Cambios

### Versión Actual (Junio 2025)
- ✅ Sistema completamente funcional con backend real
- ✅ Localización española completa
- ✅ Gestión de tickets y clientes operativa
- ✅ Autenticación JWT con renovación automática
- ✅ Dashboard con métricas en tiempo real
- ✅ Diseño responsivo y profesional

### Próximas Funcionalidades
- 🚧 Gestión completa de usuarios
- 🚧 Sistema de notificaciones
- 🚧 Reportes avanzados
- 🚧 Configuraciones del sistema
