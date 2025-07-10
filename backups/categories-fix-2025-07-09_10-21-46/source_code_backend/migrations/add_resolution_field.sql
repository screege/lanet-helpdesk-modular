-- Migration: Add resolution field to tickets table
-- Date: 2025-07-01
-- Purpose: Add resolution_notes field for when tickets are resolved

-- Add resolution_notes column to tickets table
ALTER TABLE tickets 
ADD COLUMN IF NOT EXISTS resolution_notes TEXT;

-- Add comment to document the field
COMMENT ON COLUMN tickets.resolution_notes IS 'Notes describing how the ticket was resolved';

-- Update existing resolved tickets to have a default resolution note
UPDATE tickets 
SET resolution_notes = 'Ticket marcado como resuelto (migración automática)'
WHERE status = 'resuelto' AND resolution_notes IS NULL;

-- Verify the change
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'tickets' AND column_name = 'resolution_notes';
