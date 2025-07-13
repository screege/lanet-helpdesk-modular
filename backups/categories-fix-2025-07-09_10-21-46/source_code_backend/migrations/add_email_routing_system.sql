-- LANET Helpdesk V3 - Intelligent Email-to-Ticket Routing System
-- Phase 3: Email Domain Authorization & Client Mapping

-- Add email authorization to clients table
ALTER TABLE clients 
ADD COLUMN IF NOT EXISTS authorized_domains TEXT[], -- Array of authorized domains like ['@company.com', '@organization.mx']
ADD COLUMN IF NOT EXISTS email_routing_enabled BOOLEAN DEFAULT true,
ADD COLUMN IF NOT EXISTS default_priority TEXT DEFAULT 'media' CHECK (default_priority IN ('baja', 'media', 'alta', 'critica'));

-- Add email authorization to sites table
ALTER TABLE sites 
ADD COLUMN IF NOT EXISTS authorized_emails TEXT[], -- Array of authorized email addresses
ADD COLUMN IF NOT EXISTS is_primary_site BOOLEAN DEFAULT false, -- For fallback routing
ADD COLUMN IF NOT EXISTS site_email_routing_enabled BOOLEAN DEFAULT true;

-- Create email routing rules table for advanced routing logic
CREATE TABLE IF NOT EXISTS email_routing_rules (
    rule_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(client_id) ON DELETE CASCADE,
    site_id UUID REFERENCES sites(site_id) ON DELETE CASCADE,
    rule_type TEXT NOT NULL CHECK (rule_type IN ('domain', 'email', 'pattern')),
    rule_value TEXT NOT NULL, -- Domain, email, or regex pattern
    priority INTEGER DEFAULT 100, -- Lower number = higher priority
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create email routing log for tracking routing decisions
CREATE TABLE IF NOT EXISTS email_routing_log (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email_message_id TEXT NOT NULL,
    sender_email TEXT NOT NULL,
    sender_domain TEXT NOT NULL,
    matched_rule_id UUID REFERENCES email_routing_rules(rule_id),
    routed_client_id UUID REFERENCES clients(client_id),
    routed_site_id UUID REFERENCES sites(site_id),
    routing_decision TEXT NOT NULL, -- 'exact_match', 'domain_match', 'fallback', 'unauthorized'
    routing_confidence DECIMAL(3,2) DEFAULT 0.00, -- 0.00 to 1.00
    created_ticket_id UUID REFERENCES tickets(ticket_id),
    processing_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_email_routing_rules_client_id ON email_routing_rules(client_id);
CREATE INDEX IF NOT EXISTS idx_email_routing_rules_site_id ON email_routing_rules(site_id);
CREATE INDEX IF NOT EXISTS idx_email_routing_rules_type_value ON email_routing_rules(rule_type, rule_value);
CREATE INDEX IF NOT EXISTS idx_email_routing_rules_active ON email_routing_rules(is_active);

CREATE INDEX IF NOT EXISTS idx_email_routing_log_sender_email ON email_routing_log(sender_email);
CREATE INDEX IF NOT EXISTS idx_email_routing_log_sender_domain ON email_routing_log(sender_domain);
CREATE INDEX IF NOT EXISTS idx_email_routing_log_decision ON email_routing_log(routing_decision);

-- Add trigger for updated_at
CREATE TRIGGER update_email_routing_rules_updated_at 
    BEFORE UPDATE ON email_routing_rules 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample email routing rules for testing
INSERT INTO email_routing_rules (client_id, site_id, rule_type, rule_value, priority) 
SELECT 
    c.client_id,
    s.site_id,
    'domain',
    '@' || LOWER(REPLACE(c.name, ' ', '')) || '.com',
    100
FROM clients c
JOIN sites s ON c.client_id = s.client_id
WHERE s.is_active = true
LIMIT 5
ON CONFLICT DO NOTHING;

-- Update existing clients with sample authorized domains
UPDATE clients 
SET authorized_domains = ARRAY['@' || LOWER(REPLACE(name, ' ', '')) || '.com', '@' || LOWER(REPLACE(name, ' ', '')) || '.mx']
WHERE authorized_domains IS NULL;

-- Set primary sites for each client (first active site)
WITH primary_sites AS (
    SELECT DISTINCT ON (client_id) 
        client_id, 
        site_id
    FROM sites 
    WHERE is_active = true 
    ORDER BY client_id, created_at ASC
)
UPDATE sites 
SET is_primary_site = true 
WHERE site_id IN (SELECT site_id FROM primary_sites);

-- Add sample authorized emails to sites
UPDATE sites 
SET authorized_emails = ARRAY[
    'soporte@' || LOWER(REPLACE((SELECT name FROM clients WHERE client_id = sites.client_id), ' ', '')) || '.com',
    'admin@' || LOWER(REPLACE((SELECT name FROM clients WHERE client_id = sites.client_id), ' ', '')) || '.com',
    'helpdesk@' || LOWER(REPLACE((SELECT name FROM clients WHERE client_id = sites.client_id), ' ', '')) || '.com'
]
WHERE authorized_emails IS NULL;

-- Create view for email routing analysis
CREATE OR REPLACE VIEW email_routing_analysis AS
SELECT 
    c.name as client_name,
    c.authorized_domains,
    s.name as site_name,
    s.authorized_emails,
    s.is_primary_site,
    COUNT(erl.log_id) as total_routed_emails,
    COUNT(CASE WHEN erl.routing_decision = 'exact_match' THEN 1 END) as exact_matches,
    COUNT(CASE WHEN erl.routing_decision = 'domain_match' THEN 1 END) as domain_matches,
    COUNT(CASE WHEN erl.routing_decision = 'fallback' THEN 1 END) as fallback_routes,
    COUNT(CASE WHEN erl.routing_decision = 'unauthorized' THEN 1 END) as unauthorized_emails
FROM clients c
LEFT JOIN sites s ON c.client_id = s.client_id
LEFT JOIN email_routing_log erl ON s.site_id = erl.routed_site_id
WHERE c.is_active = true AND (s.is_active = true OR s.is_active IS NULL)
GROUP BY c.client_id, c.name, c.authorized_domains, s.site_id, s.name, s.authorized_emails, s.is_primary_site
ORDER BY c.name, s.name;

-- Add configuration for unknown sender handling
UPDATE email_configurations 
SET unknown_sender_client_id = (
    SELECT client_id 
    FROM clients 
    WHERE name ILIKE '%unknown%' OR name ILIKE '%default%' 
    LIMIT 1
)
WHERE unknown_sender_client_id IS NULL;

-- If no unknown client exists, create one
INSERT INTO clients (client_id, name, email, phone, address, is_active, created_at)
SELECT 
    gen_random_uuid(),
    'Remitentes No Autorizados',
    'unknown@lanet.mx',
    'N/A',
    'Sistema - Emails no autorizados',
    true,
    NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM clients WHERE name ILIKE '%unknown%' OR name ILIKE '%no autorizado%'
);

-- Update email_configurations with the unknown sender client
UPDATE email_configurations 
SET unknown_sender_client_id = (
    SELECT client_id 
    FROM clients 
    WHERE name = 'Remitentes No Autorizados'
    LIMIT 1
)
WHERE unknown_sender_client_id IS NULL;
