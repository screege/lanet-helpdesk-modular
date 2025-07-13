-- Add ticket_reopened to the email_templates_type_check constraint
-- This allows the new ticket_reopened template type

-- Drop the existing constraint
ALTER TABLE email_templates DROP CONSTRAINT email_templates_type_check;

-- Add the new constraint with ticket_reopened included
ALTER TABLE email_templates ADD CONSTRAINT email_templates_type_check 
CHECK (template_type::text = ANY (ARRAY[
    'ticket_created'::character varying, 
    'ticket_assigned'::character varying, 
    'ticket_updated'::character varying, 
    'ticket_resolved'::character varying, 
    'ticket_closed'::character varying, 
    'ticket_commented'::character varying, 
    'ticket_reopened'::character varying,  -- NEW: Added ticket_reopened
    'sla_breach'::character varying, 
    'sla_warning'::character varying, 
    'auto_response'::character varying
]::text[]));
