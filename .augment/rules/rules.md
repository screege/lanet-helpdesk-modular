---
type: "always_apply"
---

# Reglas Generales - Helpdesk MSP Lanet Systems

## Contexto
Helpdesk MSP es un sistema de soporte técnico bajo demanda para Lanet Systems (~160 clientes, ~2,000 activos, <10 tickets diarios en México), diseñado desde cero con arquitectura propia, inspirado en NinjaOne (simplicidad), ServiceDesk Plus (robustez), y GLPI (personalización). Este documento define las reglas generales para la generación de código con Augmented Code, asegurando un sistema modular, seguro, y accesible para no programadores. Desarrollo en Windows 11, producción en Ubuntu, base de datos `helpdesk_lanet_bh` (usuario `postgres`, contraseña `Poikl55+*`). Los módulos incluyen frontend (React), app móvil (React Native, solo SuperAdmin/Técnicos), agente (Python), backend (Flask), y notificaciones (Web Push con VAPID, SMTP/IMAP).


### Reglas Generales

you can have the access credentials from the web portal login instead of guessing everytime
the posgresql user is postgres and password is Poikl55+*
DATABASE_URL=postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk
you must have all code, workflow, database associations, api calls and frontend calls present before making changes and see if other modules get affected by new code implementation
you must always act as a full stack developer
you must always commit to github and before creating new modules which after tests work create a new branch
you must establish 1 shell connection and on it execute commands needed in the remote server

CHECKLIST PARA DESARROLLO → DOCKER:
✅ ANTES DE HACER COMMIT:
¿Creaste nuevos directorios?
Agrégalos al Dockerfile: RUN mkdir -p ...
¿Instalaste nuevas dependencias?
Agrégalas a requirements.txt
¿Usas nuevas variables de entorno?
Agrégalas a deployment/docker/.env
¿Cambiaste la base de datos?
Crea script de migración
¿Funciona en desarrollo?
Prueba todo antes del commit
✅ DESPUÉS DEL PUSH:
GitHub Actions se ejecuta automáticamente (5-10 minutos)
Verifica que el deployment fue exitoso
Prueba la funcionalidad en el VPS