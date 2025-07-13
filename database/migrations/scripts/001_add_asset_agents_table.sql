-- Migration: Add Asset Agents Table
-- Version: 001
-- Description: Create table for asset agents module

-- Create asset_agents table
CREATE TABLE IF NOT EXISTS asset_agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    site_id UUID NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
    agent_name VARCHAR(255) NOT NULL,
    computer_name VARCHAR(255) NOT NULL,
    ip_address INET,
    mac_address VARCHAR(17),
    operating_system VARCHAR(255),
    os_version VARCHAR(255),
    last_seen TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'offline' CHECK (status IN ('online', 'offline', 'error')),
    agent_version VARCHAR(50),
    installed_software JSONB DEFAULT '[]',
    hardware_info JSONB DEFAULT '{}',
    monitoring_enabled BOOLEAN DEFAULT true,
    auto_ticket_creation BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_asset_agents_client_id ON asset_agents(client_id);
CREATE INDEX IF NOT EXISTS idx_asset_agents_site_id ON asset_agents(site_id);
CREATE INDEX IF NOT EXISTS idx_asset_agents_status ON asset_agents(status);
CREATE INDEX IF NOT EXISTS idx_asset_agents_last_seen ON asset_agents(last_seen);

-- Create asset_agent_logs table for monitoring
CREATE TABLE IF NOT EXISTS asset_agent_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES asset_agents(id) ON DELETE CASCADE,
    log_type VARCHAR(50) NOT NULL CHECK (log_type IN ('info', 'warning', 'error', 'system')),
    message TEXT NOT NULL,
    details JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for logs
CREATE INDEX IF NOT EXISTS idx_asset_agent_logs_agent_id ON asset_agent_logs(agent_id);
CREATE INDEX IF NOT EXISTS idx_asset_agent_logs_type ON asset_agent_logs(log_type);
CREATE INDEX IF NOT EXISTS idx_asset_agent_logs_created_at ON asset_agent_logs(created_at);

-- Enable RLS for multi-tenant security
ALTER TABLE asset_agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE asset_agent_logs ENABLE ROW LEVEL SECURITY;

-- RLS Policies for asset_agents
CREATE POLICY asset_agents_superadmin_all ON asset_agents
    FOR ALL TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id = auth.uid() 
            AND users.role = 'superadmin'
        )
    );

CREATE POLICY asset_agents_technician_all ON asset_agents
    FOR ALL TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id = auth.uid() 
            AND users.role = 'technician'
        )
    );

CREATE POLICY asset_agents_client_admin_own ON asset_agents
    FOR ALL TO authenticated
    USING (
        client_id IN (
            SELECT users.client_id FROM users 
            WHERE users.id = auth.uid() 
            AND users.role = 'client_admin'
        )
    );

CREATE POLICY asset_agents_solicitante_own_site ON asset_agents
    FOR SELECT TO authenticated
    USING (
        site_id = ANY(
            SELECT unnest(users.site_ids) FROM users 
            WHERE users.id = auth.uid() 
            AND users.role = 'solicitante'
        )
    );

-- RLS Policies for asset_agent_logs
CREATE POLICY asset_agent_logs_superadmin_all ON asset_agent_logs
    FOR ALL TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id = auth.uid() 
            AND users.role = 'superadmin'
        )
    );

CREATE POLICY asset_agent_logs_technician_all ON asset_agent_logs
    FOR ALL TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id = auth.uid() 
            AND users.role = 'technician'
        )
    );

CREATE POLICY asset_agent_logs_client_access ON asset_agent_logs
    FOR SELECT TO authenticated
    USING (
        agent_id IN (
            SELECT asset_agents.id FROM asset_agents
            JOIN users ON (
                (users.role = 'client_admin' AND asset_agents.client_id = users.client_id) OR
                (users.role = 'solicitante' AND asset_agents.site_id = ANY(users.site_ids))
            )
            WHERE users.id = auth.uid()
        )
    );

-- Add trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_asset_agents_updated_at 
    BEFORE UPDATE ON asset_agents 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert initial data or configuration if needed
INSERT INTO configurations (key, value, description, category) VALUES
('asset_agents_enabled', 'true', 'Enable asset agents module', 'modules'),
('asset_agents_auto_discovery', 'true', 'Enable automatic agent discovery', 'asset_agents'),
('asset_agents_monitoring_interval', '300', 'Monitoring interval in seconds', 'asset_agents'),
('asset_agents_offline_threshold', '900', 'Offline threshold in seconds', 'asset_agents')
ON CONFLICT (key) DO NOTHING;
