-- LANET Helpdesk V3 - Azure Database Initialization
-- This script creates the complete database structure and test data

-- Drop existing tables if they exist
DROP TABLE IF EXISTS ticket_conversations CASCADE;
DROP TABLE IF EXISTS ticket_attachments CASCADE;
DROP TABLE IF EXISTS tickets CASCADE;
DROP TABLE IF EXISTS sla_policies CASCADE;
DROP TABLE IF EXISTS user_sites CASCADE;
DROP TABLE IF EXISTS sites CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS organizations CASCADE;

-- Create organizations table
CREATE TABLE organizations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(50),
    role VARCHAR(50) NOT NULL CHECK (role IN ('superadmin', 'technician', 'client_admin', 'solicitante')),
    organization_id INTEGER REFERENCES organizations(id),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create sites table
CREATE TABLE sites (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    contact_name VARCHAR(255),
    contact_phone VARCHAR(50),
    contact_email VARCHAR(255),
    organization_id INTEGER NOT NULL REFERENCES organizations(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create user_sites table (many-to-many relationship)
CREATE TABLE user_sites (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    site_id INTEGER NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, site_id)
);

-- Create SLA policies table
CREATE TABLE sla_policies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    priority VARCHAR(50) NOT NULL CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    response_time_hours INTEGER NOT NULL,
    resolution_time_hours INTEGER NOT NULL,
    organization_id INTEGER REFERENCES organizations(id),
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create tickets table
CREATE TABLE tickets (
    id SERIAL PRIMARY KEY,
    ticket_number VARCHAR(20) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'pending_customer', 'resolved', 'closed')),
    priority VARCHAR(50) NOT NULL DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    requester_id INTEGER NOT NULL REFERENCES users(id),
    assigned_to INTEGER REFERENCES users(id),
    organization_id INTEGER NOT NULL REFERENCES organizations(id),
    site_id INTEGER REFERENCES sites(id),
    sla_policy_id INTEGER REFERENCES sla_policies(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    closed_at TIMESTAMP
);

-- Create ticket conversations table
CREATE TABLE ticket_conversations (
    id SERIAL PRIMARY KEY,
    ticket_id INTEGER NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id),
    message TEXT NOT NULL,
    is_internal BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create ticket attachments table
CREATE TABLE ticket_attachments (
    id SERIAL PRIMARY KEY,
    ticket_id INTEGER NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
    conversation_id INTEGER REFERENCES ticket_conversations(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_size INTEGER NOT NULL,
    mime_type VARCHAR(100),
    uploaded_by INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert test organizations
INSERT INTO organizations (name, email, phone, address) VALUES
('LANET Comunicaciones', 'admin@lanet.mx', '+52 55 1234 5678', 'Ciudad de México, México'),
('Empresa Prueba', 'contacto@prueba.com', '+52 55 8765 4321', 'Guadalajara, Jalisco');

-- Insert test users with bcrypt hashed passwords
INSERT INTO users (email, password_hash, first_name, last_name, phone, role, organization_id) VALUES
('ba@lanet.mx', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.PmvlDO', 'Bruno', 'Admin', '+52 55 1111 1111', 'superadmin', NULL),
('tech@test.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Tech', 'Support', '+52 55 2222 2222', 'technician', NULL),
('prueba@prueba.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.PmvlDO', 'Admin', 'Prueba', '+52 55 3333 3333', 'client_admin', 2),
('prueba3@prueba.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.PmvlDO', 'Usuario', 'Solicitante', '+52 55 4444 4444', 'solicitante', 2);

-- Insert test sites
INSERT INTO sites (name, address, contact_name, contact_phone, contact_email, organization_id) VALUES
('Oficina Principal LANET', 'Av. Principal 123, CDMX', 'Bruno Admin', '+52 55 1111 1111', 'ba@lanet.mx', 1),
('Sucursal Prueba Norte', 'Calle Norte 456, Guadalajara', 'Admin Prueba', '+52 55 3333 3333', 'prueba@prueba.com', 2),
('Sucursal Prueba Sur', 'Calle Sur 789, Guadalajara', 'Usuario Solicitante', '+52 55 4444 4444', 'prueba3@prueba.com', 2);

-- Insert user-site relationships
INSERT INTO user_sites (user_id, site_id) VALUES
(4, 2), -- prueba3@prueba.com assigned to Sucursal Prueba Norte
(4, 3); -- prueba3@prueba.com assigned to Sucursal Prueba Sur

-- Insert default SLA policies
INSERT INTO sla_policies (name, priority, response_time_hours, resolution_time_hours, organization_id, is_default) VALUES
('SLA Estándar', 'medium', 4, 24, NULL, true),
('SLA Crítico', 'critical', 1, 8, NULL, false),
('SLA Bajo', 'low', 8, 72, NULL, false);

-- Create indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_organization ON users(organization_id);
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_organization ON tickets(organization_id);
CREATE INDEX idx_tickets_requester ON tickets(requester_id);
CREATE INDEX idx_tickets_assigned ON tickets(assigned_to);
CREATE INDEX idx_ticket_conversations_ticket ON ticket_conversations(ticket_id);
CREATE INDEX idx_sites_organization ON sites(organization_id);

-- Enable Row Level Security (RLS)
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE sites ENABLE ROW LEVEL SECURITY;
ALTER TABLE tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE ticket_conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE ticket_attachments ENABLE ROW LEVEL SECURITY;
ALTER TABLE sla_policies ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_sites ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (basic structure - will be enhanced later)
CREATE POLICY "Users can view their own organization data" ON organizations
    FOR ALL USING (true); -- Simplified for initial setup

CREATE POLICY "Users can view appropriate user data" ON users
    FOR ALL USING (true); -- Simplified for initial setup

CREATE POLICY "Users can view appropriate site data" ON sites
    FOR ALL USING (true); -- Simplified for initial setup

CREATE POLICY "Users can view appropriate ticket data" ON tickets
    FOR ALL USING (true); -- Simplified for initial setup

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- Create sequence for ticket numbers
CREATE SEQUENCE IF NOT EXISTS ticket_number_seq START 1;

-- Create function to generate ticket numbers
CREATE OR REPLACE FUNCTION generate_ticket_number()
RETURNS TEXT AS $$
BEGIN
    RETURN 'TKT-' || LPAD(nextval('ticket_number_seq')::TEXT, 6, '0');
END;
$$ LANGUAGE plpgsql;

-- Create trigger to auto-generate ticket numbers
CREATE OR REPLACE FUNCTION set_ticket_number()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.ticket_number IS NULL OR NEW.ticket_number = '' THEN
        NEW.ticket_number := generate_ticket_number();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_set_ticket_number
    BEFORE INSERT ON tickets
    FOR EACH ROW
    EXECUTE FUNCTION set_ticket_number();

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create updated_at triggers for all tables
CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_sites_updated_at BEFORE UPDATE ON sites FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_tickets_updated_at BEFORE UPDATE ON tickets FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_sla_policies_updated_at BEFORE UPDATE ON sla_policies FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Final success message
SELECT 'Database initialization completed successfully!' as status;
