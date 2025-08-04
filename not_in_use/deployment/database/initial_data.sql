-- LANET Helpdesk V3 - Initial Data
-- Version: 3.0.0
-- Date: 2025-07-06

-- =====================================================
-- SYSTEM CONFIGURATION
-- =====================================================

INSERT INTO system_config (config_key, config_value, description) VALUES
('system_name', 'LANET Helpdesk V3', 'Nombre del sistema'),
('version', '3.0.0', 'Versión del sistema'),
('timezone', 'America/Mexico_City', 'Zona horaria del sistema'),
('date_format', 'DD/MM/YYYY', 'Formato de fecha'),
('tickets_per_page', '25', 'Tickets por página'),
('auto_assign_tickets', 'false', 'Asignación automática de tickets'),
('max_file_size_mb', '10', 'Tamaño máximo de archivos en MB'),
('allowed_file_types', 'pdf,doc,docx,xls,xlsx,txt,jpg,jpeg,png,gif', 'Tipos de archivo permitidos'),
('email_notifications', 'true', 'Habilitar notificaciones por email'),
('sla_monitoring', 'true', 'Habilitar monitoreo de SLA'),
('maintenance_mode', 'false', 'Modo de mantenimiento')
ON CONFLICT (config_key) DO NOTHING;

-- =====================================================
-- DEFAULT CATEGORIES
-- =====================================================

INSERT INTO categories (category_id, name, description, color, icon, sla_response_hours, sla_resolution_hours) VALUES
(uuid_generate_v4(), 'Hardware', 'Problemas relacionados con hardware', '#EF4444', 'monitor', 4, 24),
(uuid_generate_v4(), 'Software', 'Problemas relacionados con software', '#3B82F6', 'code', 8, 48),
(uuid_generate_v4(), 'Red', 'Problemas de conectividad y red', '#10B981', 'wifi', 2, 12),
(uuid_generate_v4(), 'Email', 'Problemas con correo electrónico', '#F59E0B', 'mail', 4, 24),
(uuid_generate_v4(), 'Impresoras', 'Problemas con impresoras', '#8B5CF6', 'printer', 8, 48),
(uuid_generate_v4(), 'Seguridad', 'Problemas de seguridad informática', '#DC2626', 'shield', 1, 4),
(uuid_generate_v4(), 'Respaldo', 'Problemas con respaldos', '#6B7280', 'database', 12, 72),
(uuid_generate_v4(), 'Acceso', 'Problemas de acceso y permisos', '#F97316', 'key', 4, 24),
(uuid_generate_v4(), 'Capacitación', 'Solicitudes de capacitación', '#06B6D4', 'book', 24, 120),
(uuid_generate_v4(), 'Otro', 'Otros problemas no clasificados', '#6B7280', 'help-circle', 8, 48)
ON CONFLICT DO NOTHING;

-- =====================================================
-- DEFAULT SLA POLICIES
-- =====================================================

INSERT INTO sla_policies (policy_id, name, description, priority, response_time_hours, resolution_time_hours, business_hours_only, escalation_enabled, is_active, is_default) VALUES
(uuid_generate_v4(), 'SLA Crítico', 'Para incidentes críticos que afectan operaciones', 'critica', 1, 4, true, true, true, false),
(uuid_generate_v4(), 'SLA Alto', 'Para incidentes de alta prioridad', 'alta', 4, 24, true, true, true, false),
(uuid_generate_v4(), 'SLA Medio', 'Para incidentes de prioridad media', 'media', 8, 48, true, true, true, true),
(uuid_generate_v4(), 'SLA Bajo', 'Para incidentes de baja prioridad', 'baja', 24, 120, true, false, true, false)
ON CONFLICT DO NOTHING;

-- =====================================================
-- DEFAULT EMAIL TEMPLATES
-- =====================================================

-- Template: Ticket Created
INSERT INTO email_templates (name, description, template_type, subject_template, body_template, is_html, is_active, is_default, available_variables) VALUES
('Ticket Creado - Notificación Cliente', 'Plantilla para notificar al cliente cuando se crea un nuevo ticket', 'ticket_created',
'[{{ticket_number}}] Nuevo Ticket Creado: {{subject}}',
'<h2>Ticket Creado Exitosamente</h2>
<p>Estimado/a {{client_name}},</p>
<p>Su ticket ha sido creado exitosamente con los siguientes detalles:</p>
<ul>
    <li><strong>Número de Ticket:</strong> {{ticket_number}}</li>
    <li><strong>Título:</strong> {{subject}}</li>
    <li><strong>Descripción:</strong> {{description}}</li>
    <li><strong>Prioridad:</strong> {{priority}}</li>
    <li><strong>Estado:</strong> {{status}}</li>
    <li><strong>Fecha de Creación:</strong> {{created_date}}</li>
</ul>
<p>Nuestro equipo técnico revisará su solicitud y le responderemos a la brevedad.</p>
<p>Puede revisar el estado de su ticket en cualquier momento a través de nuestro portal de soporte.</p>
<p><strong>Equipo de Soporte LANET</strong></p>',
true, true, true,
'["{{ticket_number}}", "{{client_name}}", "{{subject}}", "{{description}}", "{{priority}}", "{{status}}", "{{created_date}}"]'::jsonb)
ON CONFLICT DO NOTHING;

-- Template: Ticket Updated
INSERT INTO email_templates (name, description, template_type, subject_template, body_template, is_html, is_active, is_default, available_variables) VALUES
('Ticket Actualizado - Notificación Cliente', 'Plantilla para notificar al cliente cuando se actualiza un ticket', 'ticket_updated',
'[{{ticket_number}}] Ticket Actualizado: {{subject}}',
'<h2>Ticket Actualizado</h2>
<p>Estimado/a {{client_name}},</p>
<p>Su ticket <strong>{{ticket_number}}</strong> ha sido actualizado:</p>
<ul>
    <li><strong>Título:</strong> {{subject}}</li>
    <li><strong>Estado:</strong> {{status}}</li>
    <li><strong>Actualizado por:</strong> {{updated_by}}</li>
    <li><strong>Fecha de Actualización:</strong> {{update_date}}</li>
</ul>
<p>Puede revisar los detalles completos del ticket en nuestro portal de soporte.</p>
<p><strong>Equipo de Soporte LANET</strong></p>',
true, true, true,
'["{{ticket_number}}", "{{client_name}}", "{{subject}}", "{{status}}", "{{updated_by}}", "{{update_date}}"]'::jsonb)
ON CONFLICT DO NOTHING;

-- Template: Ticket Assigned
INSERT INTO email_templates (name, description, template_type, subject_template, body_template, is_html, is_active, is_default, available_variables) VALUES
('Ticket Asignado - Notificación Técnico', 'Plantilla para notificar al técnico cuando se le asigna un ticket', 'ticket_assigned',
'[{{ticket_number}}] Ticket Asignado: {{subject}}',
'<h2>Nuevo Ticket Asignado</h2>
<p>Hola {{technician_name}},</p>
<p>Se te ha asignado un nuevo ticket:</p>
<ul>
    <li><strong>Número de Ticket:</strong> {{ticket_number}}</li>
    <li><strong>Cliente:</strong> {{client_name}}</li>
    <li><strong>Título:</strong> {{subject}}</li>
    <li><strong>Prioridad:</strong> {{priority}}</li>
    <li><strong>Descripción:</strong> {{description}}</li>
    <li><strong>Fecha de Creación:</strong> {{created_date}}</li>
</ul>
<p>Por favor, revisa el ticket y proporciona una respuesta inicial lo antes posible.</p>
<p><strong>Sistema LANET Helpdesk</strong></p>',
true, true, true,
'["{{ticket_number}}", "{{technician_name}}", "{{client_name}}", "{{subject}}", "{{priority}}", "{{description}}", "{{created_date}}"]'::jsonb)
ON CONFLICT DO NOTHING;

-- Template: Ticket Resolved
INSERT INTO email_templates (name, description, template_type, subject_template, body_template, is_html, is_active, is_default, available_variables) VALUES
('Ticket Resuelto - Notificación Cliente', 'Plantilla para notificar al cliente cuando se resuelve un ticket', 'ticket_resolved',
'[{{ticket_number}}] Ticket Resuelto: {{subject}}',
'<h2>Ticket Resuelto</h2>
<p>Estimado/a {{client_name}},</p>
<p>Nos complace informarle que su ticket <strong>{{ticket_number}}</strong> ha sido resuelto:</p>
<ul>
    <li><strong>Título:</strong> {{subject}}</li>
    <li><strong>Resolución:</strong> {{resolution}}</li>
    <li><strong>Resuelto por:</strong> {{resolved_by}}</li>
    <li><strong>Fecha de Resolución:</strong> {{resolution_date}}</li>
</ul>
<p>Si considera que el problema no ha sido resuelto completamente, puede responder a este correo para reabrir el ticket.</p>
<p>Agradecemos su confianza en nuestros servicios.</p>
<p><strong>Equipo de Soporte LANET</strong></p>',
true, true, true,
'["{{ticket_number}}", "{{client_name}}", "{{subject}}", "{{resolution}}", "{{resolved_by}}", "{{resolution_date}}"]'::jsonb)
ON CONFLICT DO NOTHING;

-- Template: SLA Breach Warning
INSERT INTO email_templates (name, description, template_type, subject_template, body_template, is_html, is_active, is_default, available_variables) VALUES
('Alerta SLA - Violación Inminente', 'Plantilla para alertar sobre violaciones de SLA', 'sla_warning',
'🚨 ALERTA SLA: {{ticket_number}} - Vencimiento Próximo',
'<h2 style="color: #DC2626;">⚠️ Alerta de SLA</h2>
<p><strong>ATENCIÓN:</strong> El siguiente ticket está próximo a violar el SLA:</p>
<ul>
    <li><strong>Número de Ticket:</strong> {{ticket_number}}</li>
    <li><strong>Cliente:</strong> {{client_name}}</li>
    <li><strong>Título:</strong> {{subject}}</li>
    <li><strong>Prioridad:</strong> {{priority}}</li>
    <li><strong>Tipo de Vencimiento:</strong> {{breach_type}}</li>
    <li><strong>Tiempo Restante:</strong> {{time_remaining}}</li>
    <li><strong>Fecha Límite:</strong> {{deadline}}</li>
</ul>
<p><strong>Acción requerida inmediata.</strong></p>
<p><strong>Sistema de Monitoreo SLA - LANET Helpdesk</strong></p>',
true, true, true,
'["{{ticket_number}}", "{{client_name}}", "{{subject}}", "{{priority}}", "{{breach_type}}", "{{time_remaining}}", "{{deadline}}"]'::jsonb)
ON CONFLICT DO NOTHING;

-- Template: SLA Breach
INSERT INTO email_templates (name, description, template_type, subject_template, body_template, is_html, is_active, is_default, available_variables) VALUES
('Violación SLA - Notificación Crítica', 'Plantilla para notificar violaciones de SLA', 'sla_breach',
'🚨 VIOLACIÓN SLA: {{ticket_number}} - Acción Inmediata Requerida',
'<h2 style="color: #DC2626;">🚨 VIOLACIÓN DE SLA DETECTADA</h2>
<p><strong>CRÍTICO:</strong> El siguiente ticket ha violado el SLA establecido:</p>
<ul>
    <li><strong>Número de Ticket:</strong> {{ticket_number}}</li>
    <li><strong>Cliente:</strong> {{client_name}}</li>
    <li><strong>Título:</strong> {{subject}}</li>
    <li><strong>Prioridad:</strong> {{priority}}</li>
    <li><strong>Tipo de Violación:</strong> {{breach_type}}</li>
    <li><strong>Tiempo Excedido:</strong> {{time_exceeded}}</li>
    <li><strong>Fecha Límite:</strong> {{deadline}}</li>
    <li><strong>Asignado a:</strong> {{assigned_to}}</li>
</ul>
<p><strong>Se requiere escalación inmediata y acción correctiva.</strong></p>
<p><strong>Sistema de Monitoreo SLA - LANET Helpdesk</strong></p>',
true, true, true,
'["{{ticket_number}}", "{{client_name}}", "{{subject}}", "{{priority}}", "{{breach_type}}", "{{time_exceeded}}", "{{deadline}}", "{{assigned_to}}"]'::jsonb)
ON CONFLICT DO NOTHING;

-- =====================================================
-- SUPERADMIN USER
-- =====================================================

-- Create superadmin user (password: Admin123!)
INSERT INTO users (user_id, email, password_hash, name, role, is_active, created_at) 
VALUES (
    uuid_generate_v4(),
    'admin@lanet.mx',
    '$2b$12$LQv3c1yqBwlVHpPjrh8upe5TJVUXQVqUPAuVBFVo.OQ9jLjDO8/Gy',
    'Administrador del Sistema',
    'superadmin',
    true,
    CURRENT_TIMESTAMP
) ON CONFLICT (email) DO NOTHING;

-- =====================================================
-- DEMO CLIENT DATA (OPTIONAL)
-- =====================================================

-- Demo client
INSERT INTO clients (client_id, name, email, phone, address, city, state, is_active) 
VALUES (
    uuid_generate_v4(),
    'Industrias Tebi S.A. de C.V.',
    'contacto@industriastebi.com',
    '+52 (55) 1234-5678',
    'Av. Insurgentes Sur 123',
    'Ciudad de México',
    'CDMX',
    true
) ON CONFLICT DO NOTHING;

-- Demo site for the client
INSERT INTO sites (site_id, client_id, name, address, contact_person, contact_email, is_primary, is_active)
SELECT 
    uuid_generate_v4(),
    c.client_id,
    'Oficina Principal',
    'Av. Insurgentes Sur 123, Col. Roma Norte',
    'Juan Pérez',
    'juan.perez@industriastebi.com',
    true,
    true
FROM clients c 
WHERE c.name = 'Industrias Tebi S.A. de C.V.'
AND NOT EXISTS (SELECT 1 FROM sites s WHERE s.client_id = c.client_id);

-- Demo users for the client
INSERT INTO users (user_id, client_id, email, password_hash, name, role, phone, is_active)
SELECT 
    uuid_generate_v4(),
    c.client_id,
    'admin@industriastebi.com',
    '$2b$12$LQv3c1yqBwlVHpPjrh8upe5TJVUXQVqUPAuVBFVo.OQ9jLjDO8/Gy',
    'Administrador Tebi',
    'client_admin',
    '+52 (55) 1234-5679',
    true
FROM clients c 
WHERE c.name = 'Industrias Tebi S.A. de C.V.'
AND NOT EXISTS (SELECT 1 FROM users u WHERE u.email = 'admin@industriastebi.com');

INSERT INTO users (user_id, client_id, email, password_hash, name, role, phone, is_active)
SELECT 
    uuid_generate_v4(),
    c.client_id,
    'usuario@industriastebi.com',
    '$2b$12$LQv3c1yqBwlVHpPjrh8upe5TJVUXQVqUPAuVBFVo.OQ9jLjDO8/Gy',
    'Usuario Tebi',
    'solicitante',
    '+52 (55) 1234-5680',
    true
FROM clients c 
WHERE c.name = 'Industrias Tebi S.A. de C.V.'
AND NOT EXISTS (SELECT 1 FROM users u WHERE u.email = 'usuario@industriastebi.com');

-- =====================================================
-- COMPLETION MESSAGE
-- =====================================================

-- Insert completion log
INSERT INTO audit_log (action, details, timestamp) VALUES
('INITIAL_DATA_LOADED', 'LANET Helpdesk V3 initial data loaded successfully', CURRENT_TIMESTAMP);
