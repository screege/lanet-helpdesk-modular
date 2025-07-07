-- LANET Helpdesk V3 - Complete Database Schema
-- Version: 3.0.0
-- Date: 2025-07-06

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- ENUMS AND TYPES
-- =====================================================

-- User roles enum
CREATE TYPE user_role AS ENUM ('superadmin', 'admin', 'technician', 'client_admin', 'solicitante');

-- Ticket status enum
CREATE TYPE ticket_status AS ENUM ('abierto', 'en_progreso', 'espera_cliente', 'resuelto', 'cerrado');

-- Ticket priority enum
CREATE TYPE ticket_priority AS ENUM ('critica', 'alta', 'media', 'baja');

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
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100) DEFAULT 'México',
    postal_code VARCHAR(10),
    phone VARCHAR(20),
    contact_person VARCHAR(255),
    contact_email VARCHAR(255),
    authorized_emails TEXT[], -- Individual email authorizations
    is_primary BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    
    CONSTRAINT sites_contact_email_check CHECK (contact_email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
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

-- User site assignments (for solicitante users)
CREATE TABLE user_site_assignments (
    assignment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    site_id UUID NOT NULL REFERENCES sites(site_id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    
    UNIQUE(user_id, site_id)
);

-- Categories table for ticket classification
CREATE TABLE categories (
    category_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    parent_id UUID REFERENCES categories(category_id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    color VARCHAR(7) DEFAULT '#6B7280',
    icon VARCHAR(50) DEFAULT 'folder',
    is_active BOOLEAN DEFAULT true,
    sort_order INTEGER DEFAULT 0,
    auto_assign_to UUID REFERENCES users(user_id),
    sla_response_hours INTEGER DEFAULT 24,
    sla_resolution_hours INTEGER DEFAULT 72,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Assets table (Equipment/devices)
CREATE TABLE assets (
    asset_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL REFERENCES clients(client_id) ON DELETE CASCADE,
    site_id UUID NOT NULL REFERENCES sites(site_id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    asset_type VARCHAR(100),
    brand VARCHAR(100),
    model VARCHAR(100),
    serial_number VARCHAR(100),
    purchase_date DATE,
    warranty_expiry DATE,
    status VARCHAR(50) DEFAULT 'active',
    location TEXT,
    notes TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID
);

-- Ticket number sequence
CREATE SEQUENCE IF NOT EXISTS ticket_number_seq START 1;

-- Function to generate ticket numbers
CREATE OR REPLACE FUNCTION generate_ticket_number()
RETURNS VARCHAR(20) AS $$
BEGIN
    RETURN 'TKT-' || LPAD(nextval('ticket_number_seq')::TEXT, 6, '0');
END;
$$ LANGUAGE plpgsql;

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
    category_id UUID REFERENCES categories(category_id),
    priority ticket_priority DEFAULT 'media',
    status ticket_status DEFAULT 'abierto',

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    first_response_at TIMESTAMP WITH TIME ZONE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    closed_at TIMESTAMP WITH TIME ZONE,

    -- Resolution
    resolution TEXT,
    resolution_time_minutes INTEGER,
    customer_satisfaction INTEGER CHECK (customer_satisfaction BETWEEN 1 AND 5),

    -- Internal tracking
    internal_notes TEXT,
    estimated_hours DECIMAL(5,2),
    actual_hours DECIMAL(5,2),

    -- Email tracking
    email_thread_id VARCHAR(255),
    last_email_at TIMESTAMP WITH TIME ZONE
);

-- Ticket comments table
CREATE TABLE ticket_comments (
    comment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_id UUID NOT NULL REFERENCES tickets(ticket_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(user_id),
    comment_text TEXT NOT NULL,
    is_internal BOOLEAN DEFAULT false,
    is_resolution BOOLEAN DEFAULT false,
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

-- =====================================================
-- SLA TABLES
-- =====================================================

-- SLA policies table
CREATE TABLE sla_policies (
    policy_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    priority ticket_priority NOT NULL,
    response_time_hours INTEGER NOT NULL,
    resolution_time_hours INTEGER NOT NULL,
    business_hours_only BOOLEAN DEFAULT true,
    escalation_enabled BOOLEAN DEFAULT false,
    escalation_levels JSONB DEFAULT '1',
    client_id UUID REFERENCES clients(client_id),
    category_id UUID REFERENCES categories(category_id),
    is_active BOOLEAN DEFAULT true,
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- SLA tracking table
CREATE TABLE sla_tracking (
    tracking_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_id UUID NOT NULL REFERENCES tickets(ticket_id) ON DELETE CASCADE,
    policy_id UUID NOT NULL REFERENCES sla_policies(policy_id),
    response_deadline TIMESTAMP WITH TIME ZONE NOT NULL,
    resolution_deadline TIMESTAMP WITH TIME ZONE NOT NULL,
    response_status VARCHAR(20) DEFAULT 'pending',
    resolution_status VARCHAR(20) DEFAULT 'pending',
    first_response_at TIMESTAMP WITH TIME ZONE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    escalation_level INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT sla_tracking_response_status_check CHECK (response_status IN ('pending', 'met', 'breached')),
    CONSTRAINT sla_tracking_resolution_status_check CHECK (resolution_status IN ('pending', 'met', 'breached'))
);

-- =====================================================
-- EMAIL SYSTEM TABLES
-- =====================================================

-- Email configuration table
CREATE TABLE email_config (
    config_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,

    -- SMTP settings
    smtp_host VARCHAR(255) NOT NULL,
    smtp_port INTEGER NOT NULL DEFAULT 587,
    smtp_username VARCHAR(255) NOT NULL,
    smtp_password TEXT NOT NULL,
    smtp_use_tls BOOLEAN DEFAULT true,
    smtp_use_ssl BOOLEAN DEFAULT false,

    -- IMAP settings
    imap_host VARCHAR(255),
    imap_port INTEGER DEFAULT 993,
    imap_username VARCHAR(255),
    imap_password TEXT,
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
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Email templates table
CREATE TABLE email_templates (
    template_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    template_type VARCHAR(50) NOT NULL,
    subject_template TEXT NOT NULL,
    body_template TEXT NOT NULL,
    is_html BOOLEAN DEFAULT true,
    available_variables TEXT[],
    is_active BOOLEAN DEFAULT true,
    is_default BOOLEAN DEFAULT false,
    client_id UUID REFERENCES clients(client_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(user_id),

    CONSTRAINT email_templates_type_check CHECK (template_type IN (
        'ticket_created', 'ticket_updated', 'ticket_assigned', 'ticket_resolved',
        'ticket_closed', 'sla_breach', 'sla_warning', 'password_reset'
    ))
);

-- Email queue table
CREATE TABLE email_queue (
    queue_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    to_email VARCHAR(255) NOT NULL,
    cc_emails TEXT[],
    bcc_emails TEXT[],
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    is_html BOOLEAN DEFAULT true,
    template_id UUID REFERENCES email_templates(template_id),
    ticket_id UUID REFERENCES tickets(ticket_id),
    priority INTEGER DEFAULT 5,
    status VARCHAR(20) DEFAULT 'pending',
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    error_message TEXT,
    scheduled_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT email_queue_status_check CHECK (status IN ('pending', 'sent', 'failed', 'cancelled')),
    CONSTRAINT email_queue_priority_check CHECK (priority BETWEEN 1 AND 10)
);

-- =====================================================
-- SYSTEM CONFIGURATION
-- =====================================================

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

-- =====================================================
-- FUNCTIONS AND TRIGGERS
-- =====================================================

-- Function to set ticket number
CREATE OR REPLACE FUNCTION set_ticket_number()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.ticket_number IS NULL OR NEW.ticket_number = '' THEN
        NEW.ticket_number := generate_ticket_number();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Ticket number trigger
CREATE TRIGGER set_ticket_number_trigger
    BEFORE INSERT ON tickets
    FOR EACH ROW
    EXECUTE FUNCTION set_ticket_number();

-- Updated at triggers
CREATE TRIGGER update_clients_updated_at BEFORE UPDATE ON clients FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_sites_updated_at BEFORE UPDATE ON sites FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_tickets_updated_at BEFORE UPDATE ON tickets FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ticket_comments_updated_at BEFORE UPDATE ON ticket_comments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_sla_policies_updated_at BEFORE UPDATE ON sla_policies FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_sla_tracking_updated_at BEFORE UPDATE ON sla_tracking FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_email_config_updated_at BEFORE UPDATE ON email_config FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_email_templates_updated_at BEFORE UPDATE ON email_templates FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Ticket indexes
CREATE INDEX idx_tickets_client_id ON tickets(client_id);
CREATE INDEX idx_tickets_site_id ON tickets(site_id);
CREATE INDEX idx_tickets_assigned_to ON tickets(assigned_to);
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_priority ON tickets(priority);
CREATE INDEX idx_tickets_created_at ON tickets(created_at);
CREATE INDEX idx_tickets_number ON tickets(ticket_number);

-- User indexes
CREATE INDEX idx_users_client_id ON users(client_id);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_email ON users(email);

-- SLA indexes
CREATE INDEX idx_sla_tracking_ticket_id ON sla_tracking(ticket_id);
CREATE INDEX idx_sla_tracking_response_deadline ON sla_tracking(response_deadline);
CREATE INDEX idx_sla_tracking_resolution_deadline ON sla_tracking(resolution_deadline);

-- Email indexes
CREATE INDEX idx_email_queue_status ON email_queue(status);
CREATE INDEX idx_email_queue_scheduled_at ON email_queue(scheduled_at);

-- Audit indexes
CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_log_timestamp ON audit_log(timestamp);
CREATE INDEX idx_audit_log_table_name ON audit_log(table_name);

-- =====================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE sites ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE ticket_comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE file_attachments ENABLE ROW LEVEL SECURITY;
ALTER TABLE assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE sla_tracking ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_queue ENABLE ROW LEVEL SECURITY;

-- Function to get current user info
CREATE OR REPLACE FUNCTION get_current_user_info()
RETURNS TABLE(user_id UUID, role TEXT, client_id UUID) AS $$
BEGIN
    RETURN QUERY
    SELECT
        u.user_id,
        u.role::TEXT,
        u.client_id
    FROM users u
    WHERE u.user_id = current_setting('app.current_user_id', true)::UUID;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Clients RLS Policies
CREATE POLICY clients_superadmin_all ON clients
    FOR ALL TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM get_current_user_info()
            WHERE role IN ('superadmin', 'admin', 'technician')
        )
    );

CREATE POLICY clients_client_own ON clients
    FOR SELECT TO authenticated
    USING (
        client_id = (SELECT client_id FROM get_current_user_info())
    );

-- Sites RLS Policies
CREATE POLICY sites_superadmin_all ON sites
    FOR ALL TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM get_current_user_info()
            WHERE role IN ('superadmin', 'admin', 'technician')
        )
    );

CREATE POLICY sites_client_own ON sites
    FOR SELECT TO authenticated
    USING (
        client_id = (SELECT client_id FROM get_current_user_info())
    );

-- Users RLS Policies
CREATE POLICY users_superadmin_all ON users
    FOR ALL TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM get_current_user_info()
            WHERE role IN ('superadmin', 'admin')
        )
    );

CREATE POLICY users_technician_view ON users
    FOR SELECT TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM get_current_user_info()
            WHERE role = 'technician'
        )
    );

CREATE POLICY users_client_own ON users
    FOR SELECT TO authenticated
    USING (
        client_id = (SELECT client_id FROM get_current_user_info())
        OR user_id = (SELECT user_id FROM get_current_user_info())
    );

-- Tickets RLS Policies
CREATE POLICY tickets_superadmin_all ON tickets
    FOR ALL TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM get_current_user_info()
            WHERE role IN ('superadmin', 'admin', 'technician')
        )
    );

CREATE POLICY tickets_client_own ON tickets
    FOR ALL TO authenticated
    USING (
        client_id = (SELECT client_id FROM get_current_user_info())
    );

-- Ticket Comments RLS Policies
CREATE POLICY ticket_comments_superadmin_all ON ticket_comments
    FOR ALL TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM get_current_user_info()
            WHERE role IN ('superadmin', 'admin', 'technician')
        )
    );

CREATE POLICY ticket_comments_client_own ON ticket_comments
    FOR ALL TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM tickets t
            WHERE t.ticket_id = ticket_comments.ticket_id
            AND t.client_id = (SELECT client_id FROM get_current_user_info())
        )
    );

-- File Attachments RLS Policies
CREATE POLICY file_attachments_superadmin_all ON file_attachments
    FOR ALL TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM get_current_user_info()
            WHERE role IN ('superadmin', 'admin', 'technician')
        )
    );

CREATE POLICY file_attachments_client_own ON file_attachments
    FOR ALL TO authenticated
    USING (
        (ticket_id IS NOT NULL AND EXISTS (
            SELECT 1 FROM tickets t
            WHERE t.ticket_id = file_attachments.ticket_id
            AND t.client_id = (SELECT client_id FROM get_current_user_info())
        ))
        OR
        (comment_id IS NOT NULL AND EXISTS (
            SELECT 1 FROM ticket_comments tc
            JOIN tickets t ON t.ticket_id = tc.ticket_id
            WHERE tc.comment_id = file_attachments.comment_id
            AND t.client_id = (SELECT client_id FROM get_current_user_info())
        ))
    );

-- Assets RLS Policies
CREATE POLICY assets_superadmin_all ON assets
    FOR ALL TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM get_current_user_info()
            WHERE role IN ('superadmin', 'admin', 'technician')
        )
    );

CREATE POLICY assets_client_own ON assets
    FOR SELECT TO authenticated
    USING (
        client_id = (SELECT client_id FROM get_current_user_info())
    );

-- SLA Tracking RLS Policies
CREATE POLICY sla_tracking_superadmin_all ON sla_tracking
    FOR ALL TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM get_current_user_info()
            WHERE role IN ('superadmin', 'admin', 'technician')
        )
    );

CREATE POLICY sla_tracking_client_own ON sla_tracking
    FOR SELECT TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM tickets t
            WHERE t.ticket_id = sla_tracking.ticket_id
            AND t.client_id = (SELECT client_id FROM get_current_user_info())
        )
    );

-- Email Queue RLS Policies (Admin only)
CREATE POLICY email_queue_admin_only ON email_queue
    FOR ALL TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM get_current_user_info()
            WHERE role IN ('superadmin', 'admin')
        )
    );
