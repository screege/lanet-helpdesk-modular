-- Rollback Migration: Remove Asset Agents Table
-- Version: 001
-- Description: Rollback asset agents module tables and policies

-- Drop triggers
DROP TRIGGER IF EXISTS update_asset_agents_updated_at ON asset_agents;

-- Drop function
DROP FUNCTION IF EXISTS update_updated_at_column();

-- Drop RLS policies
DROP POLICY IF EXISTS asset_agent_logs_client_access ON asset_agent_logs;
DROP POLICY IF EXISTS asset_agent_logs_technician_all ON asset_agent_logs;
DROP POLICY IF EXISTS asset_agent_logs_superadmin_all ON asset_agent_logs;

DROP POLICY IF EXISTS asset_agents_solicitante_own_site ON asset_agents;
DROP POLICY IF EXISTS asset_agents_client_admin_own ON asset_agents;
DROP POLICY IF EXISTS asset_agents_technician_all ON asset_agents;
DROP POLICY IF EXISTS asset_agents_superadmin_all ON asset_agents;

-- Drop tables (logs first due to foreign key)
DROP TABLE IF EXISTS asset_agent_logs;
DROP TABLE IF EXISTS asset_agents;

-- Remove configuration entries
DELETE FROM configurations WHERE key IN (
    'asset_agents_enabled',
    'asset_agents_auto_discovery',
    'asset_agents_monitoring_interval',
    'asset_agents_offline_threshold'
);
