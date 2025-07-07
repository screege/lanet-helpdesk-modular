-- Migration: Add auto-close configuration for resolved tickets
-- Date: 2025-07-03
-- Purpose: Add system configuration to control automatic closure of resolved tickets

-- Add auto-close configuration setting
INSERT INTO system_config (config_key, config_value, description) VALUES
('auto_close_resolved_tickets', 'true', 'Automatically close tickets when resolved by technicians (true/false)')
ON CONFLICT (config_key) DO UPDATE SET
    config_value = EXCLUDED.config_value,
    description = EXCLUDED.description,
    updated_at = CURRENT_TIMESTAMP;

-- Add comment to document the setting
COMMENT ON TABLE system_config IS 'System-wide configuration settings for LANET Helpdesk V3';
