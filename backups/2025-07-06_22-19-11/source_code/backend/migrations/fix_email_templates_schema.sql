-- LANET Helpdesk V3 - Fix Email Templates Schema
-- Align database schema with frontend expectations

-- Add missing columns to match frontend expectations
ALTER TABLE email_templates 
ADD COLUMN IF NOT EXISTS description TEXT,
ADD COLUMN IF NOT EXISTS subject_template TEXT,
ADD COLUMN IF NOT EXISTS body_template TEXT,
ADD COLUMN IF NOT EXISTS is_html BOOLEAN DEFAULT true;

-- Drop the old constraint first
ALTER TABLE email_templates DROP CONSTRAINT IF EXISTS email_templates_type_check;

-- Copy existing data to new columns
UPDATE email_templates
SET
    subject_template = subject,
    body_template = body,
    description = 'Migrated template'
WHERE subject_template IS NULL;

-- Update template types to match frontend expectations
UPDATE email_templates
SET template_type = CASE
    WHEN template_type = 'new_ticket' THEN 'ticket_created'
    WHEN template_type = 'comment' THEN 'ticket_updated'
    WHEN template_type = 'closed' THEN 'ticket_closed'
    WHEN template_type = 'escalation' THEN 'sla_breach'
    WHEN template_type = 'password_reset' THEN 'auto_response'
    ELSE template_type
END;

-- Add new constraint with updated values
ALTER TABLE email_templates ADD CONSTRAINT email_templates_type_check
CHECK (template_type IN ('ticket_created', 'ticket_assigned', 'ticket_updated', 'ticket_resolved', 'ticket_closed', 'sla_breach', 'auto_response'));

-- Make old columns nullable since we're using new ones
ALTER TABLE email_templates ALTER COLUMN subject DROP NOT NULL;
ALTER TABLE email_templates ALTER COLUMN body DROP NOT NULL;

-- Update variables column to match frontend expectations
UPDATE email_templates 
SET variables = CASE template_type
    WHEN 'ticket_created' THEN '["{{ticket_number}}", "{{client_name}}", "{{site_name}}", "{{subject}}", "{{description}}", "{{priority}}", "{{affected_person}}", "{{created_date}}"]'::jsonb
    WHEN 'ticket_assigned' THEN '["{{ticket_number}}", "{{client_name}}", "{{technician_name}}", "{{subject}}", "{{priority}}", "{{assigned_date}}"]'::jsonb
    WHEN 'ticket_updated' THEN '["{{ticket_number}}", "{{client_name}}", "{{subject}}", "{{status}}", "{{updated_by}}", "{{update_date}}"]'::jsonb
    WHEN 'ticket_resolved' THEN '["{{ticket_number}}", "{{client_name}}", "{{subject}}", "{{resolution}}", "{{resolved_by}}", "{{resolved_date}}"]'::jsonb
    WHEN 'ticket_closed' THEN '["{{ticket_number}}", "{{client_name}}", "{{subject}}", "{{closed_by}}", "{{closed_date}}"]'::jsonb
    WHEN 'sla_breach' THEN '["{{ticket_number}}", "{{client_name}}", "{{subject}}", "{{priority}}", "{{breach_type}}", "{{time_elapsed}}"]'::jsonb
    WHEN 'auto_response' THEN '["{{sender_name}}", "{{ticket_number}}", "{{subject}}", "{{original_subject}}", "{{client_name}}"]'::jsonb
    ELSE variables
END
WHERE variables IS NULL;

-- Insert sample templates if none exist
INSERT INTO email_templates (name, description, template_type, subject_template, body_template, is_html, is_active, is_default, variables)
SELECT 
    'Ticket Creado - Notificación Cliente',
    'Plantilla para notificar al cliente cuando se crea un nuevo ticket',
    'ticket_created',
    '[{{ticket_number}}] Nuevo Ticket Creado: {{subject}}',
    '<h2>Ticket Creado Exitosamente</h2>
<p>Estimado/a {{client_name}},</p>
<p>Su ticket ha sido creado exitosamente con los siguientes detalles:</p>
<ul>
    <li><strong>Número de Ticket:</strong> {{ticket_number}}</li>
    <li><strong>Título:</strong> {{subject}}</li>
    <li><strong>Descripción:</strong> {{description}}</li>
    <li><strong>Prioridad:</strong> {{priority}}</li>
    <li><strong>Persona Afectada:</strong> {{affected_person}}</li>
    <li><strong>Fecha de Creación:</strong> {{created_date}}</li>
</ul>
<p>Nuestro equipo técnico revisará su solicitud y se pondrá en contacto con usted pronto.</p>
<p>Gracias por contactarnos.</p>
<p><strong>Equipo de Soporte LANET</strong></p>',
    true,
    true,
    true,
    '["{{ticket_number}}", "{{client_name}}", "{{site_name}}", "{{subject}}", "{{description}}", "{{priority}}", "{{affected_person}}", "{{created_date}}"]'::jsonb
WHERE NOT EXISTS (SELECT 1 FROM email_templates WHERE template_type = 'ticket_created' AND is_default = true);

INSERT INTO email_templates (name, description, template_type, subject_template, body_template, is_html, is_active, is_default, variables)
SELECT 
    'Ticket Actualizado - Notificación Cliente',
    'Plantilla para notificar al cliente cuando se actualiza un ticket',
    'ticket_updated',
    '[{{ticket_number}}] Actualización de Ticket: {{subject}}',
    '<h2>Ticket Actualizado</h2>
<p>Estimado/a {{client_name}},</p>
<p>Su ticket {{ticket_number}} ha sido actualizado:</p>
<ul>
    <li><strong>Título:</strong> {{subject}}</li>
    <li><strong>Nuevo Estado:</strong> {{status}}</li>
    <li><strong>Actualizado por:</strong> {{updated_by}}</li>
    <li><strong>Fecha de Actualización:</strong> {{update_date}}</li>
</ul>
<p>Puede revisar los detalles completos del ticket en nuestro portal de soporte.</p>
<p><strong>Equipo de Soporte LANET</strong></p>',
    true,
    true,
    true,
    '["{{ticket_number}}", "{{client_name}}", "{{subject}}", "{{status}}", "{{updated_by}}", "{{update_date}}"]'::jsonb
WHERE NOT EXISTS (SELECT 1 FROM email_templates WHERE template_type = 'ticket_updated' AND is_default = true);

-- Create view for easier frontend access
CREATE OR REPLACE VIEW email_templates_view AS
SELECT 
    template_id,
    name,
    description,
    template_type,
    subject_template,
    body_template,
    is_html,
    is_active,
    is_default,
    variables,
    created_at,
    updated_at,
    client_id,
    created_by
FROM email_templates
WHERE is_active = true
ORDER BY template_type, name;
