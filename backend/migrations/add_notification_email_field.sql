-- LANET Helpdesk V3 - Add notification email field and rename affected_person_contact
-- Migration: Add notification_email field and rename affected_person_contact to affected_person_phone

BEGIN;

-- Step 1: Add new notification_email field (optional)
ALTER TABLE tickets
ADD COLUMN notification_email VARCHAR(255);

-- Step 2: Add email validation constraint for notification_email
ALTER TABLE tickets
ADD CONSTRAINT tickets_notification_email_check
CHECK (notification_email IS NULL OR notification_email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

-- Step 3: Make affected_person_contact optional first (drop NOT NULL constraint)
ALTER TABLE tickets
ALTER COLUMN affected_person_contact DROP NOT NULL;

-- Step 4: Update existing data - move email addresses from affected_person_contact to notification_email
-- All current data appears to be email addresses
UPDATE tickets
SET notification_email = affected_person_contact
WHERE affected_person_contact ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$';

-- Step 5: Clear affected_person_contact for all records (will become phone field)
UPDATE tickets
SET affected_person_contact = NULL;

-- Step 6: Rename affected_person_contact to affected_person_phone
ALTER TABLE tickets
RENAME COLUMN affected_person_contact TO affected_person_phone;

-- Step 7: Add comment for documentation
COMMENT ON COLUMN tickets.affected_person_phone IS 'Optional phone number of the affected person';
COMMENT ON COLUMN tickets.notification_email IS 'Optional email address for additional notifications';

COMMIT;

-- Verify the changes
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default
FROM information_schema.columns 
WHERE table_name = 'tickets' 
AND column_name IN ('affected_person_phone', 'notification_email')
ORDER BY column_name;
