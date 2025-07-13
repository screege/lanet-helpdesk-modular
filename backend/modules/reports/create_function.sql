-- Function to get current user info for RLS policies
CREATE OR REPLACE FUNCTION get_current_user_info()
RETURNS TABLE(user_id UUID, role TEXT, client_id UUID) AS $$
BEGIN
    RETURN QUERY
    SELECT
        u.user_id,
        u.role::TEXT,
        u.client_id
    FROM users u
    WHERE u.user_id = current_setting('app.current_user_id', true)::UUID;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
