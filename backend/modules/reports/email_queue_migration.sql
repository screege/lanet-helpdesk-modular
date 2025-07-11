-- Add attachment support to email_queue table
ALTER TABLE email_queue ADD COLUMN IF NOT EXISTS attachment_data TEXT;
