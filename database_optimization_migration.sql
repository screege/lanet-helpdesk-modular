-- =====================================================
-- LANET HELPDESK V3 - TIERED DATA COLLECTION MIGRATION
-- Optimized schema for 2000+ assets with 4GB VPS
-- =====================================================

-- 1. CURRENT STATUS TABLE (Updated in place - no history)
CREATE TABLE IF NOT EXISTS assets_status_optimized (
    asset_id UUID PRIMARY KEY REFERENCES assets(asset_id) ON DELETE CASCADE,
    agent_status VARCHAR(20) NOT NULL DEFAULT 'offline',
    cpu_percent DECIMAL(5,2),
    memory_percent DECIMAL(5,2), 
    disk_percent DECIMAL(5,2),
    last_seen TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_heartbeat TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    alert_count INTEGER DEFAULT 0,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for fast lookups
CREATE INDEX IF NOT EXISTS idx_assets_status_last_seen ON assets_status_optimized(last_seen);
CREATE INDEX IF NOT EXISTS idx_assets_status_agent_status ON assets_status_optimized(agent_status);

-- 2. HOURLY METRICS (Aggregated data for charts)
CREATE TABLE IF NOT EXISTS assets_metrics_hourly (
    id BIGSERIAL PRIMARY KEY,
    asset_id UUID NOT NULL REFERENCES assets(asset_id) ON DELETE CASCADE,
    hour_timestamp TIMESTAMPTZ NOT NULL,
    avg_cpu DECIMAL(5,2),
    max_cpu DECIMAL(5,2),
    avg_memory DECIMAL(5,2),
    max_memory DECIMAL(5,2),
    avg_disk DECIMAL(5,2),
    max_disk DECIMAL(5,2),
    uptime_minutes INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(asset_id, hour_timestamp)
);

-- Partitioning by date for performance
CREATE INDEX IF NOT EXISTS idx_metrics_hourly_asset_time ON assets_metrics_hourly(asset_id, hour_timestamp);
CREATE INDEX IF NOT EXISTS idx_metrics_hourly_timestamp ON assets_metrics_hourly(hour_timestamp);

-- 3. INVENTORY SNAPSHOTS (Versioned, updated daily)
CREATE TABLE IF NOT EXISTS assets_inventory_snapshots (
    id BIGSERIAL PRIMARY KEY,
    asset_id UUID NOT NULL REFERENCES assets(asset_id) ON DELETE CASCADE,
    version INTEGER NOT NULL DEFAULT 1,
    hardware_summary JSONB, -- Compressed key info only
    software_summary JSONB, -- Top 20 programs + counts
    full_inventory_compressed BYTEA, -- Full data compressed
    inventory_hash VARCHAR(64), -- For change detection
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(asset_id, version)
);

CREATE INDEX IF NOT EXISTS idx_inventory_asset_version ON assets_inventory_snapshots(asset_id, version DESC);
CREATE INDEX IF NOT EXISTS idx_inventory_hash ON assets_inventory_snapshots(inventory_hash);

-- 4. ALERTS TABLE (Event-driven)
CREATE TABLE IF NOT EXISTS assets_alerts_optimized (
    id BIGSERIAL PRIMARY KEY,
    asset_id UUID NOT NULL REFERENCES assets(asset_id) ON DELETE CASCADE,
    alert_type VARCHAR(50) NOT NULL, -- 'cpu_high', 'disk_full', 'offline', etc.
    severity VARCHAR(20) NOT NULL, -- 'low', 'medium', 'high', 'critical'
    message TEXT NOT NULL,
    threshold_value DECIMAL(10,2),
    current_value DECIMAL(10,2),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMPTZ,
    resolved_by UUID REFERENCES users(user_id),
    is_active BOOLEAN NOT NULL DEFAULT true
);

CREATE INDEX IF NOT EXISTS idx_alerts_asset_active ON assets_alerts_optimized(asset_id, is_active);
CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON assets_alerts_optimized(created_at);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON assets_alerts_optimized(severity, is_active);

-- 5. DATA RETENTION FUNCTION
CREATE OR REPLACE FUNCTION cleanup_old_metrics()
RETURNS void AS $$
BEGIN
    -- Delete raw metrics older than 7 days
    DELETE FROM assets_metrics_hourly 
    WHERE hour_timestamp < NOW() - INTERVAL '7 days';
    
    -- Keep only last 5 inventory versions per asset
    DELETE FROM assets_inventory_snapshots 
    WHERE id NOT IN (
        SELECT id FROM (
            SELECT id, ROW_NUMBER() OVER (PARTITION BY asset_id ORDER BY version DESC) as rn
            FROM assets_inventory_snapshots
        ) t WHERE rn <= 5
    );
    
    -- Auto-resolve old alerts (older than 30 days)
    UPDATE assets_alerts_optimized 
    SET is_active = false, resolved_at = NOW()
    WHERE is_active = true 
    AND created_at < NOW() - INTERVAL '30 days';
    
    RAISE NOTICE 'Cleanup completed at %', NOW();
END;
$$ LANGUAGE plpgsql;

-- 6. AUTOMATED CLEANUP SCHEDULE (Run daily)
-- Note: This would typically be set up as a cron job or scheduled task

-- 7. MIGRATION FUNCTION TO POPULATE NEW TABLES
CREATE OR REPLACE FUNCTION migrate_existing_data()
RETURNS void AS $$
BEGIN
    -- Migrate current asset status
    INSERT INTO assets_status_optimized (asset_id, agent_status, last_seen, last_heartbeat)
    SELECT 
        asset_id,
        COALESCE(specifications->>'agent_status', 'offline'),
        COALESCE(last_seen, NOW() - INTERVAL '1 hour'),
        COALESCE(last_seen, NOW() - INTERVAL '1 hour')
    FROM assets
    ON CONFLICT (asset_id) DO UPDATE SET
        agent_status = EXCLUDED.agent_status,
        last_seen = EXCLUDED.last_seen,
        last_heartbeat = EXCLUDED.last_heartbeat,
        updated_at = NOW();
    
    -- Create initial inventory snapshots
    INSERT INTO assets_inventory_snapshots (asset_id, hardware_summary, software_summary, inventory_hash)
    SELECT 
        asset_id,
        COALESCE(specifications->'hardware_info', '{}'::jsonb),
        COALESCE(specifications->'software_info', '{}'::jsonb),
        MD5(COALESCE(specifications::text, ''))
    FROM assets
    WHERE specifications IS NOT NULL
    ON CONFLICT (asset_id, version) DO NOTHING;
    
    RAISE NOTICE 'Migration completed at %', NOW();
END;
$$ LANGUAGE plpgsql;

-- 8. PERFORMANCE VIEWS
CREATE OR REPLACE VIEW assets_dashboard_summary AS
SELECT 
    COUNT(*) as total_assets,
    COUNT(*) FILTER (WHERE agent_status = 'online') as online_assets,
    COUNT(*) FILTER (WHERE agent_status = 'offline') as offline_assets,
    COUNT(*) FILTER (WHERE last_seen < NOW() - INTERVAL '1 hour') as stale_assets,
    AVG(cpu_percent) as avg_cpu,
    AVG(memory_percent) as avg_memory,
    AVG(disk_percent) as avg_disk
FROM assets_status_optimized;

-- 9. ASSET PERFORMANCE VIEW
CREATE OR REPLACE VIEW assets_performance_current AS
SELECT 
    a.asset_id,
    a.name,
    a.client_id,
    a.site_id,
    s.agent_status,
    s.cpu_percent,
    s.memory_percent,
    s.disk_percent,
    s.last_seen,
    s.alert_count,
    CASE 
        WHEN s.last_seen > NOW() - INTERVAL '5 minutes' THEN 'online'
        WHEN s.last_seen > NOW() - INTERVAL '1 hour' THEN 'warning'
        ELSE 'offline'
    END as connection_status
FROM assets a
LEFT JOIN assets_status_optimized s ON a.asset_id = s.asset_id
WHERE a.status = 'active';

-- Execute migration
SELECT migrate_existing_data();
