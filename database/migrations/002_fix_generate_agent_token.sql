-- Fix generate_agent_token function
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
    -- Get client code (first 4 chars of name, uppercase, alphanumeric only)
    SELECT UPPER(REGEXP_REPLACE(SUBSTRING(name, 1, 4), '[^A-Z0-9]', '', 'g'))
    INTO client_code
    FROM clients
    WHERE client_id = p_client_id;
    
    -- Get site code (first 4 chars of name, uppercase, alphanumeric only)
    SELECT UPPER(REGEXP_REPLACE(SUBSTRING(name, 1, 4), '[^A-Z0-9]', '', 'g'))
    INTO site_code
    FROM sites
    WHERE site_id = p_site_id;
    
    -- Ensure codes are not empty
    IF client_code IS NULL OR LENGTH(client_code) = 0 THEN
        client_code := 'CLNT';
    END IF;
    
    IF site_code IS NULL OR LENGTH(site_code) = 0 THEN
        site_code := 'SITE';
    END IF;
    
    -- Generate unique token
    LOOP
        -- Generate random suffix (5 characters)
        random_suffix := UPPER(SUBSTRING(MD5(RANDOM()::TEXT), 1, 5));
        
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
