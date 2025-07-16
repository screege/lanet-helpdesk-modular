-- =====================================================
-- LANET HELPDESK V3 - AGENT INSTALLATION TOKENS
-- Migration: 002_add_agent_installation_tokens.sql
-- Purpose: Create token-based agent registration system
-- Date: 2025-07-15
-- =====================================================

-- Create agent_installation_tokens table
CREATE TABLE IF NOT EXISTS agent_installation_tokens (
    token_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL REFERENCES clients(client_id) ON DELETE CASCADE,
    site_id UUID NOT NULL REFERENCES sites(site_id) ON DELETE CASCADE,
    token_value VARCHAR(50) UNIQUE NOT NULL, -- Format: "LANET-{CLIENT_CODE}-{SITE_CODE}-{RANDOM}"
    is_active BOOLEAN DEFAULT true,
    created_by UUID NOT NULL REFERENCES users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE, -- Optional expiration
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMP WITH TIME ZONE,
    notes TEXT, -- Optional description/purpose
    
    -- Constraints
    CONSTRAINT token_value_format CHECK (token_value ~ '^LANET-[A-Z0-9]+-[A-Z0-9]+-[A-Z0-9]+$'),
    CONSTRAINT usage_count_positive CHECK (usage_count >= 0),
    CONSTRAINT expires_at_future CHECK (expires_at IS NULL OR expires_at > created_at)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_agent_tokens_client_site ON agent_installation_tokens(client_id, site_id);
CREATE INDEX IF NOT EXISTS idx_agent_tokens_token_value ON agent_installation_tokens(token_value);
CREATE INDEX IF NOT EXISTS idx_agent_tokens_active ON agent_installation_tokens(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_agent_tokens_created_by ON agent_installation_tokens(created_by);
CREATE INDEX IF NOT EXISTS idx_agent_tokens_expires_at ON agent_installation_tokens(expires_at) WHERE expires_at IS NOT NULL;

-- Create token usage history table
CREATE TABLE IF NOT EXISTS agent_token_usage_history (
    usage_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    token_id UUID NOT NULL REFERENCES agent_installation_tokens(token_id) ON DELETE CASCADE,
    used_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT,
    computer_name VARCHAR(255),
    hardware_fingerprint JSONB,
    registration_successful BOOLEAN DEFAULT false,
    asset_id UUID REFERENCES assets(asset_id), -- Set when registration is successful
    error_message TEXT -- Set when registration fails
);

-- Create index for usage history
CREATE INDEX IF NOT EXISTS idx_token_usage_token_id ON agent_token_usage_history(token_id);
CREATE INDEX IF NOT EXISTS idx_token_usage_used_at ON agent_token_usage_history(used_at);

-- =====================================================
-- ROW LEVEL SECURITY POLICIES
-- =====================================================

-- Enable RLS on agent_installation_tokens
ALTER TABLE agent_installation_tokens ENABLE ROW LEVEL SECURITY;

-- Policy for SELECT: Users can see tokens based on their role and client access
CREATE POLICY agent_tokens_select_policy ON agent_installation_tokens
    FOR SELECT
    USING (
        -- Superadmin and technician can see all tokens
        (current_user_role() = ANY (ARRAY['superadmin'::user_role, 'technician'::user_role]))
        OR
        -- Client admin can see only their organization's tokens
        (current_user_role() = 'client_admin'::user_role AND client_id = current_user_client_id())
    );

-- Policy for INSERT: Only superadmin and technician can create tokens
CREATE POLICY agent_tokens_insert_policy ON agent_installation_tokens
    FOR INSERT
    WITH CHECK (
        current_user_role() = ANY (ARRAY['superadmin'::user_role, 'technician'::user_role])
        AND created_by = current_user_id()
    );

-- Policy for UPDATE: Only superadmin and technician can update tokens
CREATE POLICY agent_tokens_update_policy ON agent_installation_tokens
    FOR UPDATE
    USING (
        current_user_role() = ANY (ARRAY['superadmin'::user_role, 'technician'::user_role])
    );

-- Policy for DELETE: Only superadmin can delete tokens
CREATE POLICY agent_tokens_delete_policy ON agent_installation_tokens
    FOR DELETE
    USING (
        current_user_role() = 'superadmin'::user_role
    );

-- Enable RLS on agent_token_usage_history
ALTER TABLE agent_token_usage_history ENABLE ROW LEVEL SECURITY;

-- Policy for SELECT: Users can see usage history based on token access
CREATE POLICY agent_token_usage_select_policy ON agent_token_usage_history
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM agent_installation_tokens t
            WHERE t.token_id = agent_token_usage_history.token_id
            AND (
                -- Superadmin and technician can see all
                (current_user_role() = ANY (ARRAY['superadmin'::user_role, 'technician'::user_role]))
                OR
                -- Client admin can see their organization's token usage
                (current_user_role() = 'client_admin'::user_role AND t.client_id = current_user_client_id())
            )
        )
    );

-- Policy for INSERT: System can insert usage records (no user restriction)
CREATE POLICY agent_token_usage_insert_policy ON agent_token_usage_history
    FOR INSERT
    WITH CHECK (true);

-- =====================================================
-- HELPER FUNCTIONS
-- =====================================================

-- Function to generate token value
CREATE OR REPLACE FUNCTION generate_agent_token(p_client_id UUID, p_site_id UUID)
RETURNS VARCHAR(50) AS $$
DECLARE
    client_code VARCHAR(10);
    site_code VARCHAR(10);
    random_suffix VARCHAR(10);
    token_value VARCHAR(50);
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
        token_value := 'LANET-' || client_code || '-' || site_code || '-' || random_suffix;
        
        -- Check if token already exists
        IF NOT EXISTS (SELECT 1 FROM agent_installation_tokens WHERE token_value = token_value) THEN
            EXIT;
        END IF;
        
        attempt_count := attempt_count + 1;
        IF attempt_count >= max_attempts THEN
            RAISE EXCEPTION 'Unable to generate unique token after % attempts', max_attempts;
        END IF;
    END LOOP;
    
    RETURN token_value;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to validate token and get client/site info
CREATE OR REPLACE FUNCTION validate_agent_token(p_token_value VARCHAR(50))
RETURNS TABLE(
    token_id UUID,
    client_id UUID,
    site_id UUID,
    client_name VARCHAR(255),
    site_name VARCHAR(255),
    is_valid BOOLEAN,
    error_message TEXT
) AS $$
DECLARE
    token_record RECORD;
BEGIN
    -- Get token record with client and site info
    SELECT 
        t.token_id,
        t.client_id,
        t.site_id,
        t.is_active,
        t.expires_at,
        c.name as client_name,
        s.name as site_name
    INTO token_record
    FROM agent_installation_tokens t
    JOIN clients c ON t.client_id = c.client_id
    JOIN sites s ON t.site_id = s.site_id
    WHERE t.token_value = p_token_value;
    
    -- Check if token exists
    IF NOT FOUND THEN
        RETURN QUERY SELECT 
            NULL::UUID, NULL::UUID, NULL::UUID, 
            NULL::VARCHAR(255), NULL::VARCHAR(255),
            false, 'Token not found'::TEXT;
        RETURN;
    END IF;
    
    -- Check if token is active
    IF NOT token_record.is_active THEN
        RETURN QUERY SELECT 
            token_record.token_id, token_record.client_id, token_record.site_id,
            token_record.client_name, token_record.site_name,
            false, 'Token is inactive'::TEXT;
        RETURN;
    END IF;
    
    -- Check if token is expired
    IF token_record.expires_at IS NOT NULL AND token_record.expires_at < NOW() THEN
        RETURN QUERY SELECT 
            token_record.token_id, token_record.client_id, token_record.site_id,
            token_record.client_name, token_record.site_name,
            false, 'Token has expired'::TEXT;
        RETURN;
    END IF;
    
    -- Token is valid
    RETURN QUERY SELECT 
        token_record.token_id, token_record.client_id, token_record.site_id,
        token_record.client_name, token_record.site_name,
        true, NULL::TEXT;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- SAMPLE DATA (Optional - for development)
-- =====================================================

-- Insert sample configuration using system_config table
INSERT INTO system_config (config_key, config_value, description, category) VALUES
('agent_tokens_enabled', 'true', 'Enable agent installation tokens', 'agents'),
('agent_tokens_default_expiry_days', '30', 'Default expiry days for agent tokens (0 = no expiry)', 'agents'),
('agent_tokens_max_usage', '0', 'Maximum usage count per token (0 = unlimited)', 'agents')
ON CONFLICT (config_key) DO NOTHING;

-- Add audit log entry (simplified)
INSERT INTO audit_log (user_id, action, table_name, record_id, details, ip_address)
VALUES (
    '00000000-0000-0000-0000-000000000000',
    'CREATE',
    'agent_installation_tokens',
    NULL,
    'Created agent installation tokens system',
    '127.0.0.1'
);

COMMIT;
