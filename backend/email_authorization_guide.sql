-- LANET Helpdesk V3 - Email Authorization Configuration Guide
-- Use these queries to add email authorization for incoming emails

-- ============================================================================
-- METHOD 1: EMAIL-BASED AUTHORIZATION (Exact Match - Highest Priority)
-- ============================================================================
-- Use this for specific individual email addresses
-- Location: sites.authorized_emails array

-- Add screege@gmail.com to Industrias Tebi's primary site
UPDATE sites 
SET authorized_emails = authorized_emails || ARRAY['screege@gmail.com']
WHERE client_id = (SELECT client_id FROM clients WHERE name = 'Industrias Tebi')
  AND is_primary_site = true;

-- Add multiple emails at once
UPDATE sites 
SET authorized_emails = authorized_emails || ARRAY['user1@gmail.com', 'user2@gmail.com']
WHERE client_id = (SELECT client_id FROM clients WHERE name = 'Industrias Tebi')
  AND is_primary_site = true;

-- ============================================================================
-- METHOD 2: DOMAIN-BASED AUTHORIZATION (Domain Match - Secondary Priority)
-- ============================================================================
-- Use this for entire domains (all emails from @domain.com)
-- Location: clients.authorized_domains array

-- Add @gmail.com domain to Industrias Tebi client
UPDATE clients 
SET authorized_domains = authorized_domains || ARRAY['@gmail.com']
WHERE name = 'Industrias Tebi';

-- Add multiple domains at once
UPDATE clients 
SET authorized_domains = authorized_domains || ARRAY['@gmail.com', '@hotmail.com']
WHERE name = 'Industrias Tebi';

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Check current email authorization for Industrias Tebi
SELECT 
    c.name as client_name,
    c.authorized_domains,
    s.name as site_name,
    s.authorized_emails,
    s.is_primary_site
FROM clients c
JOIN sites s ON c.client_id = s.client_id
WHERE c.name = 'Industrias Tebi'
ORDER BY s.is_primary_site DESC;

-- Test email routing for a specific email
-- (This shows what the routing system will decide)
SELECT 
    'screege@gmail.com' as test_email,
    CASE 
        WHEN 'screege@gmail.com' = ANY(s.authorized_emails) THEN 'EXACT_MATCH'
        WHEN '@gmail.com' = ANY(c.authorized_domains) THEN 'DOMAIN_MATCH'
        ELSE 'UNAUTHORIZED'
    END as routing_decision,
    c.name as client_name,
    s.name as site_name
FROM clients c
JOIN sites s ON c.client_id = s.client_id
WHERE c.name = 'Industrias Tebi' AND s.is_primary_site = true;

-- ============================================================================
-- REMOVAL QUERIES (if needed)
-- ============================================================================

-- Remove specific email from site authorization
UPDATE sites 
SET authorized_emails = array_remove(authorized_emails, 'screege@gmail.com')
WHERE client_id = (SELECT client_id FROM clients WHERE name = 'Industrias Tebi');

-- Remove domain from client authorization
UPDATE clients 
SET authorized_domains = array_remove(authorized_domains, '@gmail.com')
WHERE name = 'Industrias Tebi';
