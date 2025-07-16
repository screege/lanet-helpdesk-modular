-- Simple token generator using UUID-based codes
DROP FUNCTION IF EXISTS generate_agent_token(UUID, UUID);

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
    -- Generate fixed-length codes based on UUIDs to ensure consistency
    client_code := UPPER(SUBSTRING(REPLACE(p_client_id::TEXT, '-', ''), 1, 4));
    site_code := UPPER(SUBSTRING(REPLACE(p_site_id::TEXT, '-', ''), 1, 4));
    
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
