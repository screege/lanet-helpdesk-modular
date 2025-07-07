# 📋 **GUÍA COMPLETA: CONFIGURACIÓN SLA POR CLIENTE**
## LANET Helpdesk V3 - Sistema de Acuerdos de Nivel de Servicio

---

## 🎯 **¿CÓMO FUNCIONA EL SISTEMA SLA?**

### **1. JERARQUÍA DE APLICACIÓN DE POLÍTICAS SLA:**

El sistema aplica las políticas SLA en este orden de prioridad (de más específico a menos específico):

```
🎯 PRIORIDAD 1: SLA específico por CLIENTE + CATEGORÍA
   ↓ (si no existe)
🎯 PRIORIDAD 2: SLA específico por CLIENTE
   ↓ (si no existe)  
🎯 PRIORIDAD 3: SLA específico por CATEGORÍA
   ↓ (si no existe)
🎯 PRIORIDAD 4: SLA por DEFECTO (según prioridad del ticket)
```

### **2. EJEMPLO PRÁCTICO:**

**Ticket de "Industrias Tebi" con prioridad "Alta" y categoría "Hardware":**

1. ¿Existe SLA para "Industrias Tebi" + "Hardware"? → **SÍ** → Usar ese SLA
2. Si no, ¿existe SLA para "Industrias Tebi"? → **SÍ** → Usar ese SLA  
3. Si no, ¿existe SLA para categoría "Hardware"? → **NO** → Continuar
4. Si no, usar SLA por defecto para prioridad "Alta" → **4h respuesta / 24h resolución**

---

## 🔧 **CÓMO CONFIGURAR SLA POR CLIENTE**

### **MÉTODO 1: A TRAVÉS DE LA INTERFAZ WEB (RECOMENDADO)**

#### **Paso 1: Acceder a la Gestión SLA**
1. Inicia sesión en LANET Helpdesk V3
2. Ve al menú lateral → **"Gestión de SLA"**
3. O navega a: `http://localhost:5173/admin/sla-management`

#### **Paso 2: Crear Política SLA Específica para Cliente**
1. Haz clic en **"Nueva Política"**
2. Completa el formulario:

```
📝 FORMULARIO DE POLÍTICA SLA:
┌─────────────────────────────────────────┐
│ Nombre: "SLA Premium - Industrias Tebi" │
│ Prioridad: Alta                         │
│ Cliente: Industrias Tebi ← IMPORTANTE   │
│ Tiempo Respuesta: 2 horas               │
│ Tiempo Resolución: 8 horas              │
│ Solo horas laborales: ✓                 │
│ Escalación habilitada: ✓                │
│ Política activa: ✓                      │
└─────────────────────────────────────────┘
```

3. Haz clic en **"Crear Política"**

#### **Paso 3: Verificar la Configuración**
- La nueva política aparecerá en la tabla
- En la columna "Cliente" verás "Industrias Tebi"
- Los tickets de ese cliente usarán automáticamente esta política

---

### **MÉTODO 2: A TRAVÉS DE LA BASE DE DATOS**

#### **Consultar Clientes Disponibles:**
```sql
SELECT client_id, name FROM clients WHERE is_active = true;
```

#### **Crear SLA Específico para Cliente:**
```sql
INSERT INTO sla_policies (
    policy_id,
    name,
    description,
    priority,
    response_time_hours,
    resolution_time_hours,
    business_hours_only,
    escalation_enabled,
    client_id,  -- ← AQUÍ especificas el cliente
    is_active,
    is_default
) VALUES (
    gen_random_uuid(),
    'SLA Premium - Industrias Tebi',
    'SLA especial para cliente premium con tiempos reducidos',
    'alta',
    2,   -- 2 horas para respuesta
    8,   -- 8 horas para resolución
    true,
    true,
    'client-id-de-industrias-tebi',  -- ID real del cliente
    true,
    false
);
```

---

## 📊 **EJEMPLOS DE CONFIGURACIÓN SLA POR CLIENTE**

### **Ejemplo 1: Cliente Premium (Respuesta Rápida)**
```
Cliente: "Banco Nacional"
Prioridad: Todas
Respuesta: 30 minutos
Resolución: 2 horas
Horario: 24/7 (business_hours_only = false)
```

### **Ejemplo 2: Cliente Estándar (Horario Laboral)**
```
Cliente: "Ferretería López"
Prioridad: Todas  
Respuesta: 4 horas
Resolución: 24 horas
Horario: Solo horas laborales (8:00-17:00)
```

### **Ejemplo 3: Cliente Básico (Tiempos Extendidos)**
```
Cliente: "Consultorio Médico"
Prioridad: Todas
Respuesta: 8 horas
Resolución: 48 horas
Horario: Solo horas laborales
```

---

## 🎯 **CONFIGURACIONES AVANZADAS**

### **1. SLA por Cliente + Categoría:**
```sql
-- SLA específico para "Industrias Tebi" + categoría "Servidores"
INSERT INTO sla_policies (
    policy_id, name, priority, 
    response_time_hours, resolution_time_hours,
    client_id, category_id,  -- ← Ambos especificados
    is_active
) VALUES (
    gen_random_uuid(),
    'SLA Crítico - Industrias Tebi - Servidores',
    'critica',
    15/60,  -- 15 minutos
    2,      -- 2 horas
    'client-id-industrias-tebi',
    'category-id-servidores',
    true
);
```

### **2. SLA con Escalación Personalizada:**
```sql
-- SLA con 5 niveles de escalación
INSERT INTO sla_policies (
    policy_id, name, priority,
    response_time_hours, resolution_time_hours,
    escalation_enabled, escalation_levels,
    client_id, is_active
) VALUES (
    gen_random_uuid(),
    'SLA Escalación Múltiple - Cliente VIP',
    'critica',
    1, 4,
    true, 5,  -- 5 niveles de escalación
    'client-id-vip',
    true
);
```

---

## 📈 **MONITOREO Y VERIFICACIÓN**

### **1. Verificar Qué SLA se Aplica a un Ticket:**
```sql
SELECT 
    t.ticket_number,
    t.priority,
    c.name as client_name,
    sp.name as sla_policy_name,
    sp.response_time_hours,
    sp.resolution_time_hours,
    st.response_deadline,
    st.resolution_deadline
FROM tickets t
JOIN clients c ON t.client_id = c.client_id
JOIN sla_tracking st ON t.ticket_id = st.ticket_id
JOIN sla_policies sp ON st.policy_id = sp.policy_id
WHERE t.ticket_number = 'TKT-000094';
```

### **2. Ver Todas las Políticas SLA por Cliente:**
```sql
SELECT 
    sp.name,
    sp.priority,
    c.name as client_name,
    sp.response_time_hours,
    sp.resolution_time_hours,
    sp.is_active
FROM sla_policies sp
LEFT JOIN clients c ON sp.client_id = c.client_id
ORDER BY c.name, sp.priority;
```

### **3. Monitorear Cumplimiento SLA por Cliente:**
```sql
SELECT 
    c.name as client_name,
    COUNT(*) as total_tickets,
    SUM(CASE WHEN st.response_status = 'met' THEN 1 ELSE 0 END) as response_met,
    SUM(CASE WHEN st.resolution_status = 'met' THEN 1 ELSE 0 END) as resolution_met,
    ROUND(
        (SUM(CASE WHEN st.response_status = 'met' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 2
    ) as response_compliance_rate
FROM tickets t
JOIN clients c ON t.client_id = c.client_id
JOIN sla_tracking st ON t.ticket_id = st.ticket_id
WHERE t.created_at >= NOW() - INTERVAL '30 days'
GROUP BY c.client_id, c.name
ORDER BY response_compliance_rate DESC;
```

---

## 🚀 **PASOS PARA IMPLEMENTAR SLA POR CLIENTE**

### **1. PLANIFICACIÓN:**
- [ ] Identifica qué clientes necesitan SLA específicos
- [ ] Define los tiempos de respuesta y resolución por cliente
- [ ] Decide si usarás solo horas laborales o 24/7

### **2. CONFIGURACIÓN:**
- [ ] Accede a "Gestión de SLA" en el frontend
- [ ] Crea políticas específicas para cada cliente
- [ ] Verifica que las políticas estén activas

### **3. PRUEBAS:**
- [ ] Crea tickets de prueba para cada cliente
- [ ] Verifica que se aplique el SLA correcto
- [ ] Monitorea las notificaciones de SLA

### **4. MONITOREO:**
- [ ] Configura el monitor SLA: `python run_sla_monitor.py`
- [ ] Revisa las estadísticas en la pestaña "Estadísticas"
- [ ] Ajusta las políticas según sea necesario

---

## ❓ **PREGUNTAS FRECUENTES**

### **P: ¿Puedo tener diferentes SLA para diferentes prioridades del mismo cliente?**
**R:** Sí, crea múltiples políticas para el mismo cliente con diferentes prioridades.

### **P: ¿Qué pasa si un cliente no tiene SLA específico?**
**R:** Se usa el SLA por defecto según la prioridad del ticket.

### **P: ¿Puedo cambiar el SLA de un ticket ya creado?**
**R:** Sí, pero requiere actualización manual en la base de datos.

### **P: ¿Cómo funciona la escalación?**
**R:** El sistema envía notificaciones automáticas cuando se acerca el vencimiento del SLA.

---

## 🎯 **RESUMEN RÁPIDO**

1. **Accede a**: Gestión de SLA → Nueva Política
2. **Selecciona**: Cliente específico en el formulario
3. **Configura**: Tiempos de respuesta y resolución
4. **Activa**: La política para que se aplique automáticamente
5. **Monitorea**: A través de las estadísticas y alertas

**¡El sistema SLA por cliente está listo para usar!** 🚀
