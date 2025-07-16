-- Fix generate_agent_token function to ensure proper token format
CREATE OR REPLACE FUNCTION generate_agent_token(p_client_id UUID, p_site_id UUID)
RETURNS VARCHAR(50) AS $$
DECLARE
    client_code VARCHAR(10);
    site_code VARCHAR(10);
    random_suffix VARCHAR(10);
    new_token_value VARCHAR(50);
    attempt_count INTEGER := 0;
    max_attempts INTEGER := 100;
BEGIN
    -- Get client code (first 6 chars of name, uppercase, alphanumeric only)
    SELECT UPPER(REGEXP_REPLACE(SUBSTRING(name, 1, 6), '[^A-Z0-9]', '', 'g'))
    INTO client_code
    FROM clients
    WHERE client_id = p_client_id;
    
    -- Get site code (first 6 chars of name, uppercase, alphanumeric only)
    SELECT UPPER(REGEXP_REPLACE(SUBSTRING(name, 1, 6), '[^A-Z0-9]', '', 'g'))
    INTO site_code
    FROM sites
    WHERE site_id = p_site_id;
    
    -- Ensure codes have minimum length and are not empty
    IF client_code IS NULL OR LENGTH(client_code) = 0 THEN
        client_code := 'CLIENT';
    ELSIF LENGTH(client_code) = 1 THEN
        client_code := client_code || 'C';
    END IF;
    
    IF site_code IS NULL OR LENGTH(site_code) = 0 THEN
        site_code := 'SITE';
    ELSIF LENGTH(site_code) = 1 THEN
        site_code := site_code || 'S';
    END IF;
    
    -- Truncate to max 6 characters
    client_code := SUBSTRING(client_code, 1, 6);
    site_code := SUBSTRING(site_code, 1, 6);
    
    -- Generate unique token
    LOOP
        -- Generate random suffix (6 characters)
        random_suffix := UPPER(SUBSTRING(MD5(RANDOM()::TEXT), 1, 6));
        
        -- Construct token
        new_token_value := 'LANET-' || client_code || '-' || site_code || '-' || random_suffix;
        
        -- Check if token already exists
        IF NOT EXISTS (SELECT 1 FROM agent_installation_tokens WHERE token_value = new_token_value) THEN
            EXIT;
        END IF;
        
        attempt_count := attempt_count + 1;
        IF attempt_count >= max_attempts THEN
            RAISE EXCEPTION 'Unable to generate unique token after % attempts', max_attempts;
        END IF;
    END LOOP;
    
    RETURN new_token_value;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
