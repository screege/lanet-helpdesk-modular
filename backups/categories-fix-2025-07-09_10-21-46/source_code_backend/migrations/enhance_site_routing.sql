-- LANET Helpdesk V3 - Enhanced Site-Level Email Routing
-- Implements hierarchical email-to-site routing with primary site fallback

-- Add primary site designation to sites table
ALTER TABLE sites 
ADD COLUMN IF NOT EXISTS is_primary_site BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS site_email_routing_enabled BOOLEAN DEFAULT true,
ADD COLUMN IF NOT EXISTS authorized_emails TEXT[] DEFAULT '{}';

-- Ensure each client has exactly one primary site
CREATE OR REPLACE FUNCTION ensure_single_primary_site()
RETURNS TRIGGER AS $$
BEGIN
    -- If setting a site as primary, unset all other primary sites for this client
    IF NEW.is_primary_site = true THEN
        UPDATE sites 
        SET is_primary_site = false 
        WHERE client_id = NEW.client_id 
        AND site_id != NEW.site_id;
    END IF;
    
    -- If no primary site exists for client, make this one primary
    IF NOT EXISTS (
        SELECT 1 FROM sites 
        WHERE client_id = NEW.client_id 
        AND is_primary_site = true 
        AND site_id != NEW.site_id
    ) THEN
        NEW.is_primary_site = true;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for primary site management
DROP TRIGGER IF EXISTS trigger_ensure_single_primary_site ON sites;
CREATE TRIGGER trigger_ensure_single_primary_site
    BEFORE INSERT OR UPDATE ON sites
    FOR EACH ROW
    EXECUTE FUNCTION ensure_single_primary_site();

-- Set existing first site as primary for each client (migration)
WITH first_sites AS (
    SELECT DISTINCT ON (client_id) 
        site_id, client_id
    FROM sites 
    WHERE is_active = true
    ORDER BY client_id, created_at ASC
)
UPDATE sites 
SET is_primary_site = true 
WHERE site_id IN (SELECT site_id FROM first_sites)
AND NOT EXISTS (
    SELECT 1 FROM sites s2 
    WHERE s2.client_id = sites.client_id 
    AND s2.is_primary_site = true
);

-- Create index for faster routing lookups
CREATE INDEX IF NOT EXISTS idx_sites_authorized_emails ON sites USING GIN (authorized_emails);
CREATE INDEX IF NOT EXISTS idx_sites_primary_routing ON sites (client_id, is_primary_site, site_email_routing_enabled);
CREATE INDEX IF NOT EXISTS idx_email_routing_rules_lookup ON email_routing_rules (rule_type, rule_value, is_active);

-- Create view for email routing optimization
CREATE OR REPLACE VIEW email_routing_sites_view AS
SELECT 
    s.site_id,
    s.client_id,
    s.name as site_name,
    s.is_primary_site,
    s.site_email_routing_enabled,
    s.authorized_emails,
    c.name as client_name,
    c.authorized_domains,
    c.email_routing_enabled,
    c.default_priority
FROM sites s
JOIN clients c ON s.client_id = c.client_id
WHERE s.is_active = true 
AND c.is_active = true;

-- Insert sample email routing rules for demonstration
INSERT INTO email_routing_rules (client_id, site_id, rule_type, rule_value, priority)
SELECT 
    c.client_id,
    s.site_id,
    'email',
    'support-' || LOWER(REPLACE(s.name, ' ', '')) || '@' || SUBSTRING(c.email FROM '@(.*)'),
    10
FROM clients c
JOIN sites s ON c.client_id = s.client_id
WHERE c.email_routing_enabled = true
AND s.site_email_routing_enabled = true
ON CONFLICT DO NOTHING;

-- Create function to get routing recommendation
CREATE OR REPLACE FUNCTION get_email_routing_recommendation(sender_email TEXT)
RETURNS TABLE (
    site_id UUID,
    client_id UUID,
    routing_type TEXT,
    confidence DECIMAL,
    explanation TEXT
) AS $$
BEGIN
    -- Step 1: Exact email match in site authorized_emails
    RETURN QUERY
    SELECT 
        s.site_id,
        s.client_id,
        'exact_email_match'::TEXT,
        1.0::DECIMAL,
        'Email found in site authorized emails'::TEXT
    FROM email_routing_sites_view s
    WHERE sender_email = ANY(s.authorized_emails)
    AND s.site_email_routing_enabled = true
    AND s.email_routing_enabled = true
    ORDER BY s.is_primary_site DESC
    LIMIT 1;
    
    -- If found, return
    IF FOUND THEN
        RETURN;
    END IF;
    
    -- Step 2: Email routing rules match
    RETURN QUERY
    SELECT 
        err.site_id,
        err.client_id,
        'routing_rule_match'::TEXT,
        0.9::DECIMAL,
        'Matched email routing rule'::TEXT
    FROM email_routing_rules err
    JOIN email_routing_sites_view s ON err.site_id = s.site_id
    WHERE err.rule_type = 'email' 
    AND err.rule_value = sender_email
    AND err.is_active = true
    AND s.site_email_routing_enabled = true
    AND s.email_routing_enabled = true
    ORDER BY err.priority ASC
    LIMIT 1;
    
    -- If found, return
    IF FOUND THEN
        RETURN;
    END IF;
    
    -- Step 3: Domain match to client's primary site
    RETURN QUERY
    SELECT 
        s.site_id,
        s.client_id,
        'domain_to_primary_site'::TEXT,
        0.8::DECIMAL,
        'Domain matched, routed to primary site'::TEXT
    FROM email_routing_sites_view s
    WHERE SUBSTRING(sender_email FROM '@(.*)') = ANY(
        SELECT SUBSTRING(domain FROM '@(.*)') 
        FROM unnest(s.authorized_domains) AS domain
    )
    AND s.is_primary_site = true
    AND s.site_email_routing_enabled = true
    AND s.email_routing_enabled = true
    LIMIT 1;
    
    -- If found, return
    IF FOUND THEN
        RETURN;
    END IF;
    
    -- Step 4: Fallback to "Unknown Senders" client primary site
    RETURN QUERY
    SELECT 
        s.site_id,
        s.client_id,
        'fallback_unknown'::TEXT,
        0.1::DECIMAL,
        'No match found, routed to fallback client'::TEXT
    FROM email_routing_sites_view s
    WHERE s.client_name = 'Unknown Senders'
    AND s.is_primary_site = true
    LIMIT 1;
    
END;
$$ LANGUAGE plpgsql;
