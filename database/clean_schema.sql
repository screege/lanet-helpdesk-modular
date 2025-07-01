-- =====================================================
-- LANET HELPDESK V3 - CLEAN DATABASE SCHEMA
-- Complete modular architecture implementation
-- Based on helpdesk_msp_architecture.md blueprint
-- =====================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =====================================================
-- ENUMS AND TYPES
-- =====================================================

-- User roles enum
CREATE TYPE user_role AS ENUM (
    'superadmin',
    'admin', 
    'technician',
    'client_admin',
    'solicitante'
);

-- Ticket priority enum
CREATE TYPE ticket_priority AS ENUM (
    'baja',
    'media', 
    'alta',
    'critica'
);

-- Ticket status enum
CREATE TYPE ticket_status AS ENUM (
    'nuevo',
    'asignado',
    'en_proceso',
    'espera_cliente',
    'resuelto',
    'cerrado',
    'cancelado',
    'pendiente_aprobacion',
    'reabierto'
);

-- Ticket channel enum
CREATE TYPE ticket_channel AS ENUM (
    'portal',
    'email',
    'agente',
    'telefono'
);

-- Asset type enum  
CREATE TYPE asset_type AS ENUM (
    'desktop',
    'laptop',
    'server',
    'printer',
    'network_device',
    'mobile_device',
    'software',
    'other'
);

-- Agent status enum
CREATE TYPE agent_status AS ENUM (
    'online',
    'offline',
    'maintenance',
    'error'
);

-- =====================================================
-- CORE TABLES
-- =====================================================

-- Clients table (Organizations)
CREATE TABLE clients (
    client_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    rfc VARCHAR(13),
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    allowed_emails TEXT[], -- Array of allowed email addresses/domains
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100) DEFAULT 'México',
    postal_code VARCHAR(10),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    
    CONSTRAINT clients_email_check CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT clients_rfc_check CHECK (rfc ~* '^[A-Z&Ñ]{3,4}[0-9]{6}[A-Z0-9]{3}$')
);

-- Sites table (Client locations)
CREATE TABLE sites (
    site_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL REFERENCES clients(client_id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    address TEXT NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    country VARCHAR(100) DEFAULT 'México',
    postal_code VARCHAR(10) NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    
    CONSTRAINT sites_postal_code_check CHECK (LENGTH(postal_code) = 5),
    CONSTRAINT sites_latitude_check CHECK (latitude BETWEEN -90 AND 90),
    CONSTRAINT sites_longitude_check CHECK (longitude BETWEEN -180 AND 180)
);

-- Users table (All system users)
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID REFERENCES clients(client_id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role user_role NOT NULL,
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    
    CONSTRAINT users_email_check CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- User site assignments (Many-to-many relationship)
CREATE TABLE user_site_assignments (
    assignment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    site_id UUID NOT NULL REFERENCES sites(site_id) ON DELETE CASCADE,
    assigned_by UUID REFERENCES users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, site_id)
);

-- Assets table (Devices and software)
CREATE TABLE assets (
    asset_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL REFERENCES clients(client_id) ON DELETE CASCADE,
    site_id UUID NOT NULL REFERENCES sites(site_id) ON DELETE CASCADE,
    asset_type asset_type NOT NULL,
    name VARCHAR(255) NOT NULL,
    serial_number VARCHAR(255),
    purchase_date DATE,
    warranty_expiry DATE,
    specifications JSONB,
    license_key VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active',
    agent_status agent_status DEFAULT 'offline',
    last_seen TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(user_id)
);

-- Ticket categories table
CREATE TABLE ticket_categories (
    category_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID REFERENCES clients(client_id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    parent_category_id UUID REFERENCES ticket_categories(category_id),
    visibility VARCHAR(20) DEFAULT 'all', -- 'all', 'client', 'internal'
    is_active BOOLEAN DEFAULT true,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(name, parent_category_id, client_id)
);

-- Tickets table (Main ticket entity)
CREATE TABLE tickets (
    ticket_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_number VARCHAR(20) UNIQUE NOT NULL,
    client_id UUID NOT NULL REFERENCES clients(client_id) ON DELETE CASCADE,
    site_id UUID NOT NULL REFERENCES sites(site_id) ON DELETE CASCADE,
    asset_id UUID REFERENCES assets(asset_id),
    created_by UUID NOT NULL REFERENCES users(user_id),
    assigned_to UUID REFERENCES users(user_id),

    -- Ticket content
    subject TEXT NOT NULL,
    description TEXT NOT NULL,
    affected_person VARCHAR(255) NOT NULL,
    affected_person_contact VARCHAR(255) NOT NULL,
    additional_emails TEXT[],

    -- Classification
    priority ticket_priority NOT NULL DEFAULT 'media',
    category_id UUID REFERENCES ticket_categories(category_id),
    status ticket_status NOT NULL DEFAULT 'nuevo',
    channel ticket_channel NOT NULL DEFAULT 'portal',

    -- Email integration
    is_email_originated BOOLEAN DEFAULT false,
    from_email VARCHAR(255),
    email_message_id VARCHAR(255),
    email_thread_id UUID,

    -- Approval workflow
    approval_status VARCHAR(20) DEFAULT 'no_required', -- 'no_required', 'pending', 'approved', 'rejected'
    approved_by UUID REFERENCES users(user_id),
    approved_at TIMESTAMP WITH TIME ZONE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    assigned_at TIMESTAMP WITH TIME ZONE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    closed_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT tickets_email_check CHECK (from_email IS NULL OR from_email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Ticket comments table
CREATE TABLE ticket_comments (
    comment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_id UUID NOT NULL REFERENCES tickets(ticket_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(user_id),
    comment_text TEXT NOT NULL,
    is_internal BOOLEAN DEFAULT false,
    is_email_reply BOOLEAN DEFAULT false,
    email_message_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- File attachments table
CREATE TABLE file_attachments (
    attachment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_id UUID REFERENCES tickets(ticket_id) ON DELETE CASCADE,
    comment_id UUID REFERENCES ticket_comments(comment_id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100),
    file_hash VARCHAR(64),
    uploaded_by UUID NOT NULL REFERENCES users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT file_attachments_size_check CHECK (file_size > 0),
    CONSTRAINT file_attachments_ticket_or_comment CHECK (
        (ticket_id IS NOT NULL AND comment_id IS NULL) OR
        (ticket_id IS NULL AND comment_id IS NOT NULL)
    )
);

-- Ticket activities table (for audit trail)
CREATE TABLE ticket_activities (
    activity_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_id UUID NOT NULL REFERENCES tickets(ticket_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(user_id),
    action VARCHAR(50) NOT NULL, -- 'created', 'updated', 'assigned', 'commented', 'status_changed', etc.
    description TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Categories table for ticket classification
CREATE TABLE categories (
    category_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    parent_id UUID REFERENCES categories(category_id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    color VARCHAR(7) DEFAULT '#6B7280', -- Hex color for UI
    icon VARCHAR(50) DEFAULT 'folder', -- Icon name for UI
    is_active BOOLEAN DEFAULT true,
    sort_order INTEGER DEFAULT 0,
    auto_assign_to UUID REFERENCES users(user_id), -- Auto-assign tickets to specific technician
    sla_response_hours INTEGER DEFAULT 24, -- Default SLA response time
    sla_resolution_hours INTEGER DEFAULT 72, -- Default SLA resolution time
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT categories_name_unique UNIQUE (name, parent_id),
    CONSTRAINT categories_no_self_parent CHECK (category_id != parent_id)
);

-- Email configurations table for SMTP/IMAP settings
CREATE TABLE email_configurations (
    config_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,

    -- SMTP Configuration
    smtp_host VARCHAR(255) NOT NULL,
    smtp_port INTEGER NOT NULL DEFAULT 587,
    smtp_username VARCHAR(255) NOT NULL,
    smtp_password_encrypted TEXT NOT NULL,
    smtp_use_tls BOOLEAN DEFAULT true,
    smtp_use_ssl BOOLEAN DEFAULT false,

    -- IMAP Configuration for email-to-ticket
    imap_host VARCHAR(255),
    imap_port INTEGER DEFAULT 993,
    imap_username VARCHAR(255),
    imap_password_encrypted TEXT,
    imap_use_ssl BOOLEAN DEFAULT true,
    imap_folder VARCHAR(100) DEFAULT 'INBOX',

    -- Email-to-ticket settings
    enable_email_to_ticket BOOLEAN DEFAULT false,
    default_client_id UUID REFERENCES clients(client_id),
    default_category_id UUID REFERENCES categories(category_id),
    default_priority VARCHAR(20) DEFAULT 'media',
    auto_assign_to UUID REFERENCES users(user_id),

    -- Email parsing settings
    subject_prefix VARCHAR(50) DEFAULT '[LANET]',
    ticket_number_regex VARCHAR(255) DEFAULT '\[LANET-(\d+)\]',

    is_active BOOLEAN DEFAULT true,
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT email_config_one_default CHECK (
        NOT is_default OR (
            SELECT COUNT(*) FROM email_configurations
            WHERE is_default = true AND config_id != email_configurations.config_id
        ) = 0
    )
);

-- Email templates table for notifications and auto-responses
CREATE TABLE email_templates (
    template_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    template_type VARCHAR(50) NOT NULL, -- 'ticket_created', 'ticket_updated', 'ticket_assigned', 'auto_response', etc.

    subject_template TEXT NOT NULL,
    body_template TEXT NOT NULL,
    is_html BOOLEAN DEFAULT true,

    -- Template variables available: {{ticket_number}}, {{client_name}}, {{technician_name}}, etc.
    available_variables TEXT[], -- JSON array of available variables

    is_active BOOLEAN DEFAULT true,
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Email queue table for outgoing emails
CREATE TABLE email_queue (
    queue_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    config_id UUID NOT NULL REFERENCES email_configurations(config_id),

    to_email VARCHAR(255) NOT NULL,
    cc_emails TEXT[], -- Array of CC emails
    bcc_emails TEXT[], -- Array of BCC emails

    subject TEXT NOT NULL,
    body_text TEXT,
    body_html TEXT,

    -- Related entities
    ticket_id UUID REFERENCES tickets(ticket_id),
    user_id UUID REFERENCES users(user_id),

    -- Queue status
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'sending', 'sent', 'failed', 'cancelled'
    priority INTEGER DEFAULT 5, -- 1 (highest) to 10 (lowest)

    -- Retry logic
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    next_attempt_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Results
    sent_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Email processing log for incoming emails
CREATE TABLE email_processing_log (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    config_id UUID NOT NULL REFERENCES email_configurations(config_id),

    -- Email details
    message_id VARCHAR(255) NOT NULL,
    from_email VARCHAR(255) NOT NULL,
    to_email VARCHAR(255) NOT NULL,
    subject TEXT NOT NULL,
    body_text TEXT,
    body_html TEXT,

    -- Processing results
    processing_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'processed', 'failed', 'ignored'
    ticket_id UUID REFERENCES tickets(ticket_id),
    action_taken VARCHAR(50), -- 'created_ticket', 'updated_ticket', 'added_comment', 'ignored'

    -- Error handling
    error_message TEXT,

    processed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- SLA MANAGEMENT TABLES
-- =====================================================

-- SLA policies table
CREATE TABLE slas (
    sla_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL REFERENCES clients(client_id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,

    -- Working schedule
    working_days INTEGER[] DEFAULT '{1,2,3,4,5}', -- Monday=1 to Sunday=7
    working_hours_start TIME DEFAULT '09:00:00',
    working_hours_end TIME DEFAULT '19:00:00',
    timezone VARCHAR(50) DEFAULT 'America/Mexico_City',

    -- Response times by priority (in minutes)
    priority_response_time JSONB DEFAULT '{
        "critica": 30,
        "alta": 120,
        "media": 240,
        "baja": 480
    }',

    -- Resolution times by priority (in minutes)
    priority_resolution_time JSONB DEFAULT '{
        "critica": 240,
        "alta": 480,
        "media": 1440,
        "baja": 2880
    }',

    -- Reporting
    client_report_recipients TEXT[],
    client_report_frequency VARCHAR(20) DEFAULT 'monthly', -- 'weekly', 'monthly', 'quarterly'

    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(user_id)
);

-- SLA compliance tracking
CREATE TABLE sla_compliance (
    compliance_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_id UUID NOT NULL REFERENCES tickets(ticket_id) ON DELETE CASCADE,
    sla_id UUID NOT NULL REFERENCES slas(sla_id),

    -- Response tracking
    response_due_at TIMESTAMP WITH TIME ZONE,
    response_time_met BOOLEAN,
    response_time_actual INTEGER, -- minutes

    -- Resolution tracking
    resolution_due_at TIMESTAMP WITH TIME ZONE,
    resolution_time_met BOOLEAN,
    resolution_time_actual INTEGER, -- minutes

    -- Escalation
    escalated_to_admin BOOLEAN DEFAULT false,
    escalation_timestamp TIMESTAMP WITH TIME ZONE,
    escalation_reason TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- EMAIL SYSTEM TABLES
-- =====================================================

-- Email templates table
CREATE TABLE email_templates (
    template_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    template_type VARCHAR(50) NOT NULL, -- 'new_ticket', 'comment', 'closed', 'escalation', 'password_reset', 'sla_report', 'license_alert'
    client_id UUID REFERENCES clients(client_id), -- NULL for system-wide templates
    is_default BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    variables JSONB, -- Available template variables
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(user_id),

    UNIQUE(name, client_id),
    CONSTRAINT email_templates_type_check CHECK (template_type IN (
        'new_ticket', 'comment', 'closed', 'escalation', 'password_reset',
        'sla_report', 'license_alert', 'client_confirmation'
    ))
);

-- System configuration table
CREATE TABLE system_config (
    config_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT,
    description TEXT,
    is_encrypted BOOLEAN DEFAULT false,
    updated_by UUID REFERENCES users(user_id),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- TECHNICIAN ASSIGNMENT TABLES
-- =====================================================

-- Technician assignments table
CREATE TABLE technician_assignments (
    assignment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    technician_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    client_id UUID NOT NULL REFERENCES clients(client_id) ON DELETE CASCADE,
    priority INTEGER DEFAULT 1, -- Lower number = higher priority
    is_primary BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(user_id),

    UNIQUE(technician_id, client_id)
);

-- =====================================================
-- AUDIT AND SECURITY TABLES
-- =====================================================

-- Audit log table
CREATE TABLE audit_log (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(user_id),
    action VARCHAR(100) NOT NULL,
    table_name VARCHAR(100),
    record_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    details TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Password reset tokens table
CREATE TABLE password_reset_tokens (
    token_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    used_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT password_reset_tokens_expiry_check CHECK (expires_at > created_at)
);

-- =====================================================
-- SOFTWARE LICENSES TABLE
-- =====================================================

-- Software licenses table
CREATE TABLE software_licenses (
    license_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL REFERENCES clients(client_id) ON DELETE CASCADE,
    software_name VARCHAR(255) NOT NULL,
    total_licenses INTEGER NOT NULL DEFAULT 1,
    assigned_licenses INTEGER DEFAULT 0,
    license_key TEXT,
    purchase_date DATE,
    expiration_date DATE,
    vendor VARCHAR(255),
    cost DECIMAL(10,2),
    notes TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(user_id),

    CONSTRAINT software_licenses_count_check CHECK (assigned_licenses <= total_licenses),
    CONSTRAINT software_licenses_total_check CHECK (total_licenses > 0)
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Clients indexes
CREATE INDEX idx_clients_active ON clients(is_active);
CREATE INDEX idx_clients_name ON clients(name);

-- Sites indexes
CREATE INDEX idx_sites_client_id ON sites(client_id);
CREATE INDEX idx_sites_active ON sites(is_active);

-- Users indexes
CREATE INDEX idx_users_client_id ON users(client_id);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active);

-- User site assignments indexes
CREATE INDEX idx_user_site_assignments_user_id ON user_site_assignments(user_id);
CREATE INDEX idx_user_site_assignments_site_id ON user_site_assignments(site_id);

-- Assets indexes
CREATE INDEX idx_assets_client_id ON assets(client_id);
CREATE INDEX idx_assets_site_id ON assets(site_id);
CREATE INDEX idx_assets_status ON assets(status);
CREATE INDEX idx_assets_agent_status ON assets(agent_status);

-- Tickets indexes
CREATE INDEX idx_tickets_client_id ON tickets(client_id);
CREATE INDEX idx_tickets_site_id ON tickets(site_id);
CREATE INDEX idx_tickets_assigned_to ON tickets(assigned_to);
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_priority ON tickets(priority);
CREATE INDEX idx_tickets_created_at ON tickets(created_at);
CREATE INDEX idx_tickets_number ON tickets(ticket_number);

-- Ticket comments indexes
CREATE INDEX idx_ticket_comments_ticket_id ON ticket_comments(ticket_id);

-- SLA indexes
CREATE INDEX idx_slas_client_id ON slas(client_id);
CREATE INDEX idx_slas_active ON slas(is_active);

-- SLA compliance indexes
CREATE INDEX idx_sla_compliance_ticket_id ON sla_compliance(ticket_id);
CREATE INDEX idx_sla_compliance_escalated ON sla_compliance(escalated_to_admin);

-- Technician assignments indexes
CREATE INDEX idx_technician_assignments_technician_id ON technician_assignments(technician_id);
CREATE INDEX idx_technician_assignments_client_id ON technician_assignments(client_id);
CREATE INDEX idx_technician_assignments_active ON technician_assignments(is_active);

-- Audit log indexes
CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_log_timestamp ON audit_log(timestamp);
CREATE INDEX idx_audit_log_action ON audit_log(action);

-- Password reset tokens indexes
CREATE INDEX idx_password_reset_tokens_user_id ON password_reset_tokens(user_id);
CREATE INDEX idx_password_reset_tokens_token ON password_reset_tokens(token);
CREATE INDEX idx_password_reset_tokens_expires_at ON password_reset_tokens(expires_at);

-- Software licenses indexes
CREATE INDEX idx_software_licenses_client_id ON software_licenses(client_id);
CREATE INDEX idx_software_licenses_expiration_date ON software_licenses(expiration_date);
CREATE INDEX idx_software_licenses_active ON software_licenses(is_active);

-- =====================================================
-- SEQUENCES AND FUNCTIONS
-- =====================================================

-- Ticket number sequence
CREATE SEQUENCE ticket_number_seq START 1;

-- Function to generate ticket numbers
CREATE OR REPLACE FUNCTION generate_ticket_number()
RETURNS VARCHAR(20) AS $$
BEGIN
    RETURN 'TKT-' || LPAD(nextval('ticket_number_seq')::TEXT, 6, '0');
END;
$$ LANGUAGE plpgsql;

-- Function to set ticket number automatically
CREATE OR REPLACE FUNCTION set_ticket_number()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.ticket_number IS NULL THEN
        NEW.ticket_number := generate_ticket_number();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function for audit logging
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log (user_id, action, table_name, record_id, old_values, timestamp)
        VALUES (
            current_setting('app.current_user_id', true)::UUID,
            'DELETE',
            TG_TABLE_NAME,
            OLD.client_id, -- Assuming most tables have client_id
            row_to_json(OLD),
            CURRENT_TIMESTAMP
        );
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_log (user_id, action, table_name, record_id, old_values, new_values, timestamp)
        VALUES (
            current_setting('app.current_user_id', true)::UUID,
            'UPDATE',
            TG_TABLE_NAME,
            NEW.client_id, -- Assuming most tables have client_id
            row_to_json(OLD),
            row_to_json(NEW),
            CURRENT_TIMESTAMP
        );
        RETURN NEW;
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO audit_log (user_id, action, table_name, record_id, new_values, timestamp)
        VALUES (
            current_setting('app.current_user_id', true)::UUID,
            'INSERT',
            TG_TABLE_NAME,
            NEW.client_id, -- Assuming most tables have client_id
            row_to_json(NEW),
            CURRENT_TIMESTAMP
        );
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Ticket number trigger
CREATE TRIGGER set_ticket_number_trigger
    BEFORE INSERT ON tickets
    FOR EACH ROW
    EXECUTE FUNCTION set_ticket_number();

-- Updated_at triggers
CREATE TRIGGER update_clients_updated_at
    BEFORE UPDATE ON clients
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sites_updated_at
    BEFORE UPDATE ON sites
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_assets_updated_at
    BEFORE UPDATE ON assets
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tickets_updated_at
    BEFORE UPDATE ON tickets
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ticket_comments_updated_at
    BEFORE UPDATE ON ticket_comments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_slas_updated_at
    BEFORE UPDATE ON slas
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sla_compliance_updated_at
    BEFORE UPDATE ON sla_compliance
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_software_licenses_updated_at
    BEFORE UPDATE ON software_licenses
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Audit triggers
CREATE TRIGGER audit_clients_trigger
    AFTER INSERT OR UPDATE OR DELETE ON clients
    FOR EACH ROW
    EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_users_trigger
    AFTER INSERT OR UPDATE OR DELETE ON users
    FOR EACH ROW
    EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_tickets_trigger
    AFTER INSERT OR UPDATE OR DELETE ON tickets
    FOR EACH ROW
    EXECUTE FUNCTION audit_trigger_function();
