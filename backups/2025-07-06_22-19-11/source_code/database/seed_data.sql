-- =====================================================
-- LANET HELPDESK V3 - SEED DATA
-- Essential test data for development and testing
-- Based on helpdesk_msp_architecture.md blueprint
-- =====================================================

-- Disable RLS temporarily for data insertion
SET row_security = off;

-- =====================================================
-- SYSTEM CONFIGURATION
-- =====================================================

INSERT INTO system_config (config_key, config_value, description) VALUES
('system_name', 'LANET Helpdesk V3', 'System name displayed in UI'),
('system_logo', '/assets/lanet-logo.png', 'Path to system logo'),
('primary_color', '#1e40af', 'LANET corporate blue color'),
('max_attachment_size_mb', '10', 'Maximum file attachment size in MB'),
('allowed_attachment_types', 'pdf,png,jpg,jpeg,docx,xlsx,txt', 'Allowed file types for attachments'),
('session_timeout_minutes', '480', 'Session timeout in minutes (8 hours)'),
('ticket_auto_close_days', '30', 'Days after resolution to auto-close tickets'),
('smtp_host', 'mail.compushop.com.mx', 'SMTP server host'),
('smtp_port', '587', 'SMTP server port'),
('smtp_username', 'webmaster@compushop.com.mx', 'SMTP username'),
('smtp_password', 'Iyhnbsfg26', 'SMTP password'),
('smtp_use_tls', 'true', 'Use TLS for SMTP'),
('imap_host', 'mail.compushop.com.mx', 'IMAP server host'),
('imap_port', '993', 'IMAP server port'),
('imap_username', 'it@compushop.com.mx', 'IMAP username'),
('imap_password', 'Iyhnbsfg26+*', 'IMAP password'),
('imap_use_ssl', 'true', 'Use SSL for IMAP');

-- =====================================================
-- EMAIL TEMPLATES
-- =====================================================

INSERT INTO email_templates (name, subject, body, template_type, is_default, variables) VALUES
('new_ticket_default', 'Nuevo Ticket Creado: {{ticket_number}}', 
'<h2>Nuevo Ticket Creado</h2>
<p>Estimado/a {{contact_name}},</p>
<p>Se ha creado un nuevo ticket con los siguientes detalles:</p>
<ul>
<li><strong>Número de Ticket:</strong> {{ticket_number}}</li>
<li><strong>Asunto:</strong> {{subject}}</li>
<li><strong>Prioridad:</strong> {{priority}}</li>
<li><strong>Estado:</strong> {{status}}</li>
<li><strong>Técnico Asignado:</strong> {{assigned_technician}}</li>
</ul>
<p>Descripción: {{description}}</p>
<p>Puede dar seguimiento a su ticket en: <a href="{{portal_url}}">Portal de Clientes LANET</a></p>
<p>Saludos cordiales,<br>Equipo de Soporte LANET</p>', 
'new_ticket', true, '["ticket_number", "subject", "priority", "status", "assigned_technician", "contact_name", "description", "portal_url"]'),

('comment_default', 'Actualización de Ticket: {{ticket_number}}',
'<h2>Actualización de Ticket</h2>
<p>Estimado/a {{contact_name}},</p>
<p>Su ticket {{ticket_number}} ha sido actualizado:</p>
<p><strong>Comentario del técnico:</strong></p>
<div style="background-color: #f5f5f5; padding: 10px; margin: 10px 0;">{{comment_text}}</div>
<p>Estado actual: {{status}}</p>
<p>Puede responder a este correo o acceder al portal: <a href="{{portal_url}}">Portal de Clientes LANET</a></p>
<p>Saludos cordiales,<br>{{technician_name}}<br>Equipo de Soporte LANET</p>',
'comment', true, '["ticket_number", "contact_name", "comment_text", "status", "portal_url", "technician_name"]'),

('password_reset_default', 'Restablecimiento de Contraseña - LANET Helpdesk',
'<h2>Restablecimiento de Contraseña</h2>
<p>Estimado/a {{user_name}},</p>
<p>Ha solicitado restablecer su contraseña para el sistema LANET Helpdesk.</p>
<p>Haga clic en el siguiente enlace para crear una nueva contraseña:</p>
<p><a href="{{reset_url}}" style="background-color: #1e40af; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Restablecer Contraseña</a></p>
<p>Este enlace expirará en 15 minutos por seguridad.</p>
<p>Si no solicitó este cambio, ignore este correo.</p>
<p>Saludos cordiales,<br>Equipo de Soporte LANET</p>',
'password_reset', true, '["user_name", "reset_url"]');

-- =====================================================
-- TEST CLIENTS
-- =====================================================

INSERT INTO clients (client_id, name, rfc, email, phone, allowed_emails, address, city, state, country, postal_code, is_active) VALUES
('550e8400-e29b-41d4-a716-446655440001', 'Cafe Mexico S.A. de C.V.', 'CAF950101ABC', 'contacto@cafemexico.mx', '5555551234', ARRAY['@cafemexico.mx', 'admin@cafemexico.mx'], 'Av. Insurgentes Sur 1234', 'Ciudad de Mexico', 'CDMX', 'Mexico', '03100', true),
('550e8400-e29b-41d4-a716-446655440002', 'Diseno Nono Creativo', 'DIS960202DEF', 'info@disenonono.com', '5555555678', ARRAY['@disenonono.com'], 'Calle Revolucion 567', 'Guadalajara', 'Jalisco', 'Mexico', '44100', true),
('550e8400-e29b-41d4-a716-446655440003', 'Tecnico Aguila Servicios', 'TEC970303GHI', 'soporte@tecnicoaguila.mx', '5555559012', ARRAY['@tecnicoaguila.mx', 'admin@tecnicoaguila.mx'], 'Blvd. Diaz Ordaz 890', 'Monterrey', 'Nuevo Leon', 'Mexico', '64000', true),
('550e8400-e29b-41d4-a716-446655440004', 'Solucion Facil Consulting', 'SOL980404JKL', 'contacto@solucionfacil.com.mx', '5555553456', ARRAY['@solucionfacil.com.mx'], 'Av. Universidad 321', 'Ciudad de Mexico', 'CDMX', 'Mexico', '04510', true),
('550e8400-e29b-41d4-a716-446655440005', 'Innovacion Movil Tech', 'INN990505MNO', 'info@innovacionmovil.mx', '5555557890', ARRAY['@innovacionmovil.mx'], 'Calle Tecnologico 654', 'Guadalajara', 'Jalisco', 'Mexico', '44630', true);

-- =====================================================
-- TEST SITES
-- =====================================================

INSERT INTO sites (site_id, client_id, name, address, city, state, country, postal_code, latitude, longitude, is_active) VALUES
-- Cafe Mexico sites
('660e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440001', 'Oficina Principal CDMX', 'Av. Insurgentes Sur 1234', 'Ciudad de Mexico', 'CDMX', 'Mexico', '03100', 19.3910, -99.1426, true),
('660e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440001', 'Sucursal Polanco', 'Av. Presidente Masaryk 111', 'Ciudad de Mexico', 'CDMX', 'Mexico', '11560', 19.4326, -99.1949, true),

-- Diseno Nono sites
('660e8400-e29b-41d4-a716-446655440003', '550e8400-e29b-41d4-a716-446655440002', 'Estudio Creativo GDL', 'Calle Revolucion 567', 'Guadalajara', 'Jalisco', 'Mexico', '44100', 20.6597, -103.3496, true),

-- Tecnico Aguila sites
('660e8400-e29b-41d4-a716-446655440004', '550e8400-e29b-41d4-a716-446655440003', 'Centro de Servicios MTY', 'Blvd. Diaz Ordaz 890', 'Monterrey', 'Nuevo Leon', 'Mexico', '64000', 25.6866, -100.3161, true),
('660e8400-e29b-41d4-a716-446655440005', '550e8400-e29b-41d4-a716-446655440003', 'Taller Especializado', 'Av. Constitucion 234', 'Monterrey', 'Nuevo Leon', 'Mexico', '64720', 25.6751, -100.3185, true),

-- Solucion Facil sites
('660e8400-e29b-41d4-a716-446655440006', '550e8400-e29b-41d4-a716-446655440004', 'Oficina Corporativa', 'Av. Universidad 321', 'Ciudad de Mexico', 'CDMX', 'Mexico', '04510', 19.3370, -99.1804, true),

-- Innovacion Movil sites
('660e8400-e29b-41d4-a716-446655440007', '550e8400-e29b-41d4-a716-446655440005', 'Lab de Desarrollo', 'Calle Tecnologico 654', 'Guadalajara', 'Jalisco', 'Mexico', '44630', 20.6668, -103.3918, true),
('660e8400-e29b-41d4-a716-446655440008', '550e8400-e29b-41d4-a716-446655440005', 'Centro de Innovacion', 'Av. Lopez Mateos 987', 'Guadalajara', 'Jalisco', 'Mexico', '45050', 20.6534, -103.4070, true);

-- =====================================================
-- TEST USERS
-- =====================================================

-- Superadmin user
INSERT INTO users (user_id, client_id, name, email, password_hash, role, phone, is_active) VALUES
('770e8400-e29b-41d4-a716-446655440001', NULL, 'Administrador Sistema', 'ba@lanet.mx', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsxq5S/kS', 'superadmin', '5555550001', true);

-- Admin users
INSERT INTO users (user_id, client_id, name, email, password_hash, role, phone, is_active) VALUES
('770e8400-e29b-41d4-a716-446655440002', NULL, 'Juan Pérez Admin', 'admin@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsxq5S/kS', 'admin', '5555550002', true);

-- Technician users
INSERT INTO users (user_id, client_id, name, email, password_hash, role, phone, is_active) VALUES
('770e8400-e29b-41d4-a716-446655440003', NULL, 'Maria Gonzalez Tech', 'tech@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsxq5S/kS', 'technician', '5555550003', true),
('770e8400-e29b-41d4-a716-446655440004', NULL, 'Carlos Rodriguez Tech', 'carlos.tech@lanet.mx', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsxq5S/kS', 'technician', '5555550004', true);

-- Client admin users
INSERT INTO users (user_id, client_id, name, email, password_hash, role, phone, is_active) VALUES
('770e8400-e29b-41d4-a716-446655440005', '550e8400-e29b-41d4-a716-446655440001', 'Ana Cafe Admin', 'prueba@prueba.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsxq5S/kS', 'client_admin', '5555551001', true),
('770e8400-e29b-41d4-a716-446655440006', '550e8400-e29b-41d4-a716-446655440002', 'Luis Diseno Admin', 'admin@disenonono.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsxq5S/kS', 'client_admin', '5555552001', true),
('770e8400-e29b-41d4-a716-446655440007', '550e8400-e29b-41d4-a716-446655440003', 'Roberto Aguila Admin', 'admin@tecnicoaguila.mx', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsxq5S/kS', 'client_admin', '5555553001', true);

-- Solicitante users
INSERT INTO users (user_id, client_id, name, email, password_hash, role, phone, is_active) VALUES
('770e8400-e29b-41d4-a716-446655440008', '550e8400-e29b-41d4-a716-446655440001', 'Patricia Cafe User', 'prueba3@prueba.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsxq5S/kS', 'solicitante', '5555551002', true),
('770e8400-e29b-41d4-a716-446655440009', '550e8400-e29b-41d4-a716-446655440002', 'Miguel Diseno User', 'usuario@disenonono.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsxq5S/kS', 'solicitante', '5555552002', true),
('770e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440004', 'Carmen Solucion User', 'usuario@solucionfacil.com.mx', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsxq5S/kS', 'solicitante', '5555554001', true);

-- =====================================================
-- USER SITE ASSIGNMENTS
-- =====================================================

-- Assign solicitante users to their respective sites
INSERT INTO user_site_assignments (user_id, site_id, assigned_by) VALUES
('770e8400-e29b-41d4-a716-446655440008', '660e8400-e29b-41d4-a716-446655440001', '770e8400-e29b-41d4-a716-446655440005'), -- Patricia to Cafe Mexico Principal
('770e8400-e29b-41d4-a716-446655440008', '660e8400-e29b-41d4-a716-446655440002', '770e8400-e29b-41d4-a716-446655440005'), -- Patricia to Cafe Mexico Polanco
('770e8400-e29b-41d4-a716-446655440009', '660e8400-e29b-41d4-a716-446655440003', '770e8400-e29b-41d4-a716-446655440006'), -- Miguel to Diseno Nono
('770e8400-e29b-41d4-a716-446655440010', '660e8400-e29b-41d4-a716-446655440006', '770e8400-e29b-41d4-a716-446655440002'); -- Carmen to Solucion Facil

-- =====================================================
-- TECHNICIAN ASSIGNMENTS
-- =====================================================

INSERT INTO technician_assignments (technician_id, client_id, priority, is_primary, created_by) VALUES
('770e8400-e29b-41d4-a716-446655440003', '550e8400-e29b-41d4-a716-446655440001', 1, true, '770e8400-e29b-41d4-a716-446655440002'),  -- Maria -> Cafe Mexico (Primary)
('770e8400-e29b-41d4-a716-446655440004', '550e8400-e29b-41d4-a716-446655440001', 2, false, '770e8400-e29b-41d4-a716-446655440002'), -- Carlos -> Cafe Mexico (Secondary)
('770e8400-e29b-41d4-a716-446655440003', '550e8400-e29b-41d4-a716-446655440002', 1, true, '770e8400-e29b-41d4-a716-446655440002'),  -- Maria -> Diseno Nono
('770e8400-e29b-41d4-a716-446655440004', '550e8400-e29b-41d4-a716-446655440003', 1, true, '770e8400-e29b-41d4-a716-446655440002'),  -- Carlos -> Tecnico Aguila
('770e8400-e29b-41d4-a716-446655440003', '550e8400-e29b-41d4-a716-446655440004', 1, true, '770e8400-e29b-41d4-a716-446655440002'),  -- Maria -> Solucion Facil
('770e8400-e29b-41d4-a716-446655440004', '550e8400-e29b-41d4-a716-446655440005', 1, true, '770e8400-e29b-41d4-a716-446655440002');  -- Carlos -> Innovacion Movil

-- =====================================================
-- SLA POLICIES
-- =====================================================

INSERT INTO slas (sla_id, client_id, name, working_days, working_hours_start, working_hours_end, priority_response_time, priority_resolution_time, client_report_recipients, created_by) VALUES
('880e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440001', 'SLA Cafe Mexico Estandar', '{1,2,3,4,5}', '09:00:00', '19:00:00',
 '{"critica": 30, "alta": 120, "media": 240, "baja": 480}',
 '{"critica": 240, "alta": 480, "media": 1440, "baja": 2880}',
 ARRAY['prueba@prueba.com', 'contacto@cafemexico.mx'], '770e8400-e29b-41d4-a716-446655440002'),

('880e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440002', 'SLA Diseno Nono Premium', '{1,2,3,4,5}', '08:00:00', '20:00:00',
 '{"critica": 15, "alta": 60, "media": 120, "baja": 240}',
 '{"critica": 120, "alta": 240, "media": 720, "baja": 1440}',
 ARRAY['admin@disenonono.com'], '770e8400-e29b-41d4-a716-446655440002'),

('880e8400-e29b-41d4-a716-446655440003', '550e8400-e29b-41d4-a716-446655440003', 'SLA Tecnico Aguila 24/7', '{1,2,3,4,5,6,7}', '00:00:00', '23:59:59',
 '{"critica": 15, "alta": 30, "media": 60, "baja": 120}',
 '{"critica": 60, "alta": 120, "media": 480, "baja": 960}',
 ARRAY['admin@tecnicoaguila.mx'], '770e8400-e29b-41d4-a716-446655440002');

-- =====================================================
-- TICKET CATEGORIES
-- =====================================================

-- System-wide categories
INSERT INTO ticket_categories (category_id, client_id, name, parent_category_id, visibility, sort_order) VALUES
('990e8400-e29b-41d4-a716-446655440001', NULL, 'Hardware', NULL, 'all', 1),
('990e8400-e29b-41d4-a716-446655440002', NULL, 'Software', NULL, 'all', 2),
('990e8400-e29b-41d4-a716-446655440003', NULL, 'Red y Conectividad', NULL, 'all', 3),
('990e8400-e29b-41d4-a716-446655440004', NULL, 'Seguridad', NULL, 'all', 4),
('990e8400-e29b-41d4-a716-446655440005', NULL, 'Solicitudes de Usuario', NULL, 'all', 5);

-- Hardware subcategories
INSERT INTO ticket_categories (category_id, client_id, name, parent_category_id, visibility, sort_order) VALUES
('990e8400-e29b-41d4-a716-446655440011', NULL, 'Computadoras', '990e8400-e29b-41d4-a716-446655440001', 'all', 1),
('990e8400-e29b-41d4-a716-446655440012', NULL, 'Impresoras', '990e8400-e29b-41d4-a716-446655440001', 'all', 2),
('990e8400-e29b-41d4-a716-446655440013', NULL, 'Dispositivos Móviles', '990e8400-e29b-41d4-a716-446655440001', 'all', 3);

-- Software subcategories
INSERT INTO ticket_categories (category_id, client_id, name, parent_category_id, visibility, sort_order) VALUES
('990e8400-e29b-41d4-a716-446655440021', NULL, 'Sistema Operativo', '990e8400-e29b-41d4-a716-446655440002', 'all', 1),
('990e8400-e29b-41d4-a716-446655440022', NULL, 'Aplicaciones', '990e8400-e29b-41d4-a716-446655440002', 'all', 2),
('990e8400-e29b-41d4-a716-446655440023', NULL, 'Licencias', '990e8400-e29b-41d4-a716-446655440002', 'all', 3);

-- =====================================================
-- SAMPLE ASSETS
-- =====================================================

INSERT INTO assets (asset_id, client_id, site_id, asset_type, name, serial_number, specifications, status, created_by) VALUES
-- Cafe Mexico assets
('aa0e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440001', '660e8400-e29b-41d4-a716-446655440001', 'desktop', 'Dell OptiPlex 7090 - Recepcion', 'DL7090001', '{"cpu": "Intel i5-11500", "ram": "16GB", "storage": "512GB SSD"}', 'active', '770e8400-e29b-41d4-a716-446655440002'),
('aa0e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440001', '660e8400-e29b-41d4-a716-446655440001', 'laptop', 'HP EliteBook 840 G8 - Gerencia', 'HP840G8001', '{"cpu": "Intel i7-1165G7", "ram": "32GB", "storage": "1TB SSD"}', 'active', '770e8400-e29b-41d4-a716-446655440002'),
('aa0e8400-e29b-41d4-a716-446655440003', '550e8400-e29b-41d4-a716-446655440001', '660e8400-e29b-41d4-a716-446655440001', 'printer', 'HP LaserJet Pro M404dn', 'HPM404001', '{"type": "Laser", "color": false, "duplex": true}', 'active', '770e8400-e29b-41d4-a716-446655440002'),

-- Diseno Nono assets
('aa0e8400-e29b-41d4-a716-446655440004', '550e8400-e29b-41d4-a716-446655440002', '660e8400-e29b-41d4-a716-446655440003', 'desktop', 'iMac 27" 2021 - Diseno', 'IMAC27001', '{"cpu": "Apple M1", "ram": "32GB", "storage": "1TB SSD", "gpu": "M1 8-core"}', 'active', '770e8400-e29b-41d4-a716-446655440002'),
('aa0e8400-e29b-41d4-a716-446655440005', '550e8400-e29b-41d4-a716-446655440002', '660e8400-e29b-41d4-a716-446655440003', 'laptop', 'MacBook Pro 16" M1 Max', 'MBP16001', '{"cpu": "Apple M1 Max", "ram": "64GB", "storage": "2TB SSD"}', 'active', '770e8400-e29b-41d4-a716-446655440002'),

-- Tecnico Aguila assets
('aa0e8400-e29b-41d4-a716-446655440006', '550e8400-e29b-41d4-a716-446655440003', '660e8400-e29b-41d4-a716-446655440004', 'server', 'Dell PowerEdge R740', 'DLR740001', '{"cpu": "2x Intel Xeon Silver 4214", "ram": "128GB", "storage": "4x 2TB SAS"}', 'active', '770e8400-e29b-41d4-a716-446655440002'),
('aa0e8400-e29b-41d4-a716-446655440007', '550e8400-e29b-41d4-a716-446655440003', '660e8400-e29b-41d4-a716-446655440004', 'network_device', 'Cisco Catalyst 2960-X', 'CSC2960001', '{"ports": 48, "type": "Managed Switch", "poe": true}', 'active', '770e8400-e29b-41d4-a716-446655440002');

-- Re-enable RLS
SET row_security = on;
