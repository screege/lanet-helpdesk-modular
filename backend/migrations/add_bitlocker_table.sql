-- Migration: Add BitLocker keys table
-- Created: 2025-01-22
-- Description: Create table to store BitLocker recovery keys securely

-- Create bitlocker_keys table
CREATE TABLE IF NOT EXISTS bitlocker_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id UUID NOT NULL REFERENCES assets(asset_id) ON DELETE CASCADE,
    volume_letter VARCHAR(10) NOT NULL, -- C:, D:, etc.
    volume_label VARCHAR(255),
    protection_status VARCHAR(50) NOT NULL, -- 'Protected', 'Unprotected', 'Unknown'
    encryption_method VARCHAR(50), -- 'AES-128', 'AES-256', etc.
    key_protector_type VARCHAR(100), -- 'TPM', 'TPM+PIN', 'Password', 'RecoveryPassword', etc.
    recovery_key_id VARCHAR(100), -- Key protector ID from BitLocker
    recovery_key_encrypted TEXT, -- Encrypted recovery key
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_verified_at TIMESTAMP WITH TIME ZONE,
    
    -- Constraints
    UNIQUE(asset_id, volume_letter),
    CHECK (volume_letter ~ '^[A-Z]:$'), -- Ensure format like 'C:'
    CHECK (protection_status IN ('Protected', 'Unprotected', 'Unknown'))
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_bitlocker_keys_asset_id ON bitlocker_keys(asset_id);
CREATE INDEX IF NOT EXISTS idx_bitlocker_keys_protection_status ON bitlocker_keys(protection_status);
CREATE INDEX IF NOT EXISTS idx_bitlocker_keys_updated_at ON bitlocker_keys(updated_at);

-- Note: RLS policies will be implemented at the application level
-- since we're using standard PostgreSQL without Supabase auth
-- The backend will handle access control based on JWT tokens

-- For now, we'll disable RLS and handle security in the application layer
ALTER TABLE bitlocker_keys DISABLE ROW LEVEL SECURITY;

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_bitlocker_keys_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for updated_at
DROP TRIGGER IF EXISTS trigger_update_bitlocker_keys_updated_at ON bitlocker_keys;
CREATE TRIGGER trigger_update_bitlocker_keys_updated_at
    BEFORE UPDATE ON bitlocker_keys
    FOR EACH ROW
    EXECUTE FUNCTION update_bitlocker_keys_updated_at();

-- Add comments for documentation
COMMENT ON TABLE bitlocker_keys IS 'Stores BitLocker recovery keys and volume information for assets';
COMMENT ON COLUMN bitlocker_keys.recovery_key_encrypted IS 'Encrypted BitLocker recovery key - only accessible to superadmin/technician';
COMMENT ON COLUMN bitlocker_keys.key_protector_type IS 'Type of key protector: TPM, TPM+PIN, Password, RecoveryPassword, etc.';
COMMENT ON COLUMN bitlocker_keys.protection_status IS 'Current protection status of the volume';

-- Grant permissions to postgres user (will be handled by application)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON bitlocker_keys TO authenticated;
-- GRANT USAGE ON SEQUENCE bitlocker_keys_id_seq TO authenticated;
