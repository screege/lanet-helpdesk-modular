-- LANET Helpdesk V3 - Add Reply-To Field for Bidirectional Email Communication
-- This enables SMTP send-only servers to use a different Reply-To address for receiving responses

-- Add reply_to field to email_configurations table
ALTER TABLE email_configurations 
ADD COLUMN IF NOT EXISTS smtp_reply_to VARCHAR(255);

-- Add comment to explain the field
COMMENT ON COLUMN email_configurations.smtp_reply_to IS 'Reply-To email address for outgoing notifications. Used when SMTP server is send-only and replies should go to IMAP-enabled address.';

-- Update existing configurations to use IMAP username as reply-to if available
UPDATE email_configurations 
SET smtp_reply_to = imap_username 
WHERE smtp_reply_to IS NULL 
AND imap_username IS NOT NULL 
AND imap_username != '';

-- For configurations without IMAP, use SMTP username as fallback
UPDATE email_configurations 
SET smtp_reply_to = smtp_username 
WHERE smtp_reply_to IS NULL;

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_email_configurations_reply_to 
ON email_configurations(smtp_reply_to) 
WHERE smtp_reply_to IS NOT NULL;
