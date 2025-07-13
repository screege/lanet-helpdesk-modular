-- Create notification tracking table to prevent duplicate notifications
CREATE TABLE IF NOT EXISTS notification_tracking (
    tracking_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticket_id UUID NOT NULL REFERENCES tickets(ticket_id),
    comment_id UUID REFERENCES ticket_comments(comment_id),
    notification_type VARCHAR(50) NOT NULL, -- 'ticket_created', 'ticket_commented', etc.
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Ensure we don't send duplicate notifications
    UNIQUE(ticket_id, comment_id, notification_type)
    -- Note: Partial unique constraint for ticket-level notifications handled by application logic
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_notification_tracking_ticket_id ON notification_tracking(ticket_id);
CREATE INDEX IF NOT EXISTS idx_notification_tracking_comment_id ON notification_tracking(comment_id);
CREATE INDEX IF NOT EXISTS idx_notification_tracking_type ON notification_tracking(notification_type);
CREATE INDEX IF NOT EXISTS idx_notification_tracking_sent_at ON notification_tracking(sent_at);

-- Prevent re-sending notifications for ALL existing tickets
INSERT INTO notification_tracking (ticket_id, notification_type)
SELECT DISTINCT t.ticket_id, 'ticket_created'
FROM tickets t
ON CONFLICT DO NOTHING;

-- Prevent re-sending notifications for ALL existing comments
INSERT INTO notification_tracking (ticket_id, comment_id, notification_type)
SELECT DISTINCT tc.ticket_id, tc.comment_id, 'ticket_commented'
FROM ticket_comments tc
WHERE tc.is_internal = false
ON CONFLICT DO NOTHING;

-- Specifically mark the problematic tickets as already notified
INSERT INTO notification_tracking (ticket_id, comment_id, notification_type)
SELECT DISTINCT tc.ticket_id, tc.comment_id, 'ticket_commented'
FROM ticket_comments tc
JOIN tickets t ON tc.ticket_id = t.ticket_id
WHERE t.ticket_number IN ('TKT-000115', 'TKT-000022')
AND tc.is_internal = false
ON CONFLICT DO NOTHING;
