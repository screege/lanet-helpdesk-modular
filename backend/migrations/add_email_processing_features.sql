-- LANET Helpdesk V3 - Email Processing Features Migration
-- Phase 2.2: Email Cleanup and Atomic Processing

-- Add email processing configuration to email_configurations table
ALTER TABLE email_configurations 
ADD COLUMN IF NOT EXISTS check_interval_minutes INTEGER DEFAULT 5,
ADD COLUMN IF NOT EXISTS auto_delete_processed BOOLEAN DEFAULT true,
ADD COLUMN IF NOT EXISTS unknown_sender_client_id UUID REFERENCES clients(client_id);

-- Create email processing tracking table
CREATE TABLE IF NOT EXISTS email_processing_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email_message_id TEXT UNIQUE NOT NULL,
    sender_email TEXT NOT NULL,
    subject TEXT,
    processed_at TIMESTAMP DEFAULT NOW(),
    ticket_id UUID REFERENCES tickets(ticket_id),
    status TEXT CHECK (status IN ('processed', 'failed', 'duplicate', 'pending')) DEFAULT 'pending',
    error_message TEXT,
    email_size_bytes INTEGER,
    attachments_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create email templates system for notifications
CREATE TABLE IF NOT EXISTS email_templates (
    template_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    template_type TEXT NOT NULL, -- 'ticket_created', 'status_changed', 'comment_added', etc.
    subject_template TEXT NOT NULL,
    body_html TEXT NOT NULL,
    body_plain TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    variables_json TEXT, -- JSON array of available variables
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create notification queue for reliable email delivery
CREATE TABLE IF NOT EXISTS notification_queue (
    queue_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticket_id UUID REFERENCES tickets(ticket_id),
    template_type TEXT NOT NULL,
    recipient_email TEXT NOT NULL,
    recipient_name TEXT,
    subject TEXT NOT NULL,
    body_html TEXT NOT NULL,
    body_plain TEXT NOT NULL,
    status TEXT CHECK (status IN ('pending', 'sent', 'failed', 'retry')) DEFAULT 'pending',
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    next_retry_at TIMESTAMP,
    sent_at TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Add indexes for performance (using existing column names)
CREATE INDEX IF NOT EXISTS idx_email_processing_log_message_id ON email_processing_log(message_id);
CREATE INDEX IF NOT EXISTS idx_email_processing_log_sender ON email_processing_log(from_email);
CREATE INDEX IF NOT EXISTS idx_email_processing_log_status ON email_processing_log(processing_status);
-- processed_at index already exists

CREATE INDEX IF NOT EXISTS idx_notification_queue_status ON notification_queue(status);
CREATE INDEX IF NOT EXISTS idx_notification_queue_next_retry ON notification_queue(next_retry_at);
CREATE INDEX IF NOT EXISTS idx_notification_queue_ticket_id ON notification_queue(ticket_id);

-- Insert default email templates (using existing column names)
INSERT INTO email_templates (name, template_type, subject, body, variables) VALUES
('Ticket Created - Client Notification', 'new_ticket',
 'Nuevo Ticket Creado: {{ticket_number}}',
 '<h2>Ticket Creado Exitosamente</h2>
  <p>Estimado/a {{client_name}},</p>
  <p>Su ticket ha sido creado exitosamente con los siguientes detalles:</p>
  <ul>
    <li><strong>Número de Ticket:</strong> {{ticket_number}}</li>
    <li><strong>Título:</strong> {{ticket_title}}</li>
    <li><strong>Prioridad:</strong> {{priority}}</li>
    <li><strong>Estado:</strong> {{status}}</li>
    <li><strong>Técnico Asignado:</strong> {{technician_name}}</li>
  </ul>
  <p>Puede dar seguimiento a su ticket en: <a href="{{ticket_url}}">{{ticket_url}}</a></p>
  <p>Gracias por contactarnos.</p>
  <p>Equipo de Soporte LANET</p>',
 '["ticket_number", "ticket_title", "priority", "status", "client_name", "technician_name", "ticket_url"]'::jsonb
),
('Ticket Status Changed', 'comment',
 'Actualización de Ticket: {{ticket_number}} - {{new_status}}',
 '<h2>Estado de Ticket Actualizado</h2>
  <p>Estimado/a {{client_name}},</p>
  <p>El estado de su ticket {{ticket_number}} ha sido actualizado:</p>
  <ul>
    <li><strong>Estado Anterior:</strong> {{old_status}}</li>
    <li><strong>Nuevo Estado:</strong> {{new_status}}</li>
    <li><strong>Actualizado por:</strong> {{updated_by}}</li>
    <li><strong>Fecha:</strong> {{update_date}}</li>
  </ul>
  <p><strong>Comentario:</strong></p>
  <p>{{comment}}</p>
  <p>Ver ticket: <a href="{{ticket_url}}">{{ticket_url}}</a></p>',
 '["ticket_number", "client_name", "old_status", "new_status", "updated_by", "update_date", "comment", "ticket_url"]'::jsonb
)
ON CONFLICT (name) DO NOTHING;

-- Add trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_email_processing_log_updated_at BEFORE UPDATE ON email_processing_log FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_email_templates_updated_at BEFORE UPDATE ON email_templates FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_notification_queue_updated_at BEFORE UPDATE ON notification_queue FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
