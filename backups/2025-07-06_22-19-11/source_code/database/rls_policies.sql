-- =====================================================
-- LANET HELPDESK V3 - ROW LEVEL SECURITY POLICIES
-- Comprehensive RLS implementation for multi-tenant security
-- Based on helpdesk_msp_architecture.md blueprint
-- =====================================================

-- =====================================================
-- RLS HELPER FUNCTIONS
-- =====================================================

-- Function to get current user ID from session
CREATE OR REPLACE FUNCTION current_user_id()
RETURNS UUID AS $$
BEGIN
    RETURN current_setting('app.current_user_id', true)::UUID;
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get current user role from session
CREATE OR REPLACE FUNCTION current_user_role()
RETURNS user_role AS $$
BEGIN
    RETURN current_setting('app.current_user_role', true)::user_role;
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get current user's client ID
CREATE OR REPLACE FUNCTION current_user_client_id()
RETURNS UUID AS $$
BEGIN
    RETURN current_setting('app.current_user_client_id', true)::UUID;
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get current user's site IDs
CREATE OR REPLACE FUNCTION current_user_site_ids()
RETURNS UUID[] AS $$
BEGIN
    RETURN string_to_array(current_setting('app.current_user_site_ids', true), ',')::UUID[];
EXCEPTION
    WHEN OTHERS THEN
        RETURN ARRAY[]::UUID[];
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- ENABLE RLS ON ALL TABLES
-- =====================================================

ALTER TABLE clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE sites ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_site_assignments ENABLE ROW LEVEL SECURITY;
ALTER TABLE assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE ticket_categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE ticket_comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE file_attachments ENABLE ROW LEVEL SECURITY;
ALTER TABLE slas ENABLE ROW LEVEL SECURITY;
ALTER TABLE sla_compliance ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE technician_assignments ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE password_reset_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE software_licenses ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- CLIENTS TABLE RLS POLICIES
-- =====================================================

-- Superadmin and Admin can see all clients
CREATE POLICY clients_select_policy ON clients
    FOR SELECT
    USING (
        current_user_role() IN ('superadmin', 'admin', 'technician') OR
        client_id = current_user_client_id()
    );

-- Only superadmin and admin can insert clients
CREATE POLICY clients_insert_policy ON clients
    FOR INSERT
    WITH CHECK (current_user_role() IN ('superadmin', 'admin'));

-- Only superadmin and admin can update clients
CREATE POLICY clients_update_policy ON clients
    FOR UPDATE
    USING (
        current_user_role() IN ('superadmin', 'admin') OR
        (current_user_role() = 'client_admin' AND client_id = current_user_client_id())
    );

-- Only superadmin can delete clients (with protection)
CREATE POLICY clients_delete_policy ON clients
    FOR DELETE
    USING (
        current_user_role() = 'superadmin' AND
        client_id != current_user_client_id() -- Prevent self-deletion
    );

-- =====================================================
-- SITES TABLE RLS POLICIES
-- =====================================================

-- Users can see sites based on their role and assignments
CREATE POLICY sites_select_policy ON sites
    FOR SELECT
    USING (
        current_user_role() IN ('superadmin', 'admin', 'technician') OR
        client_id = current_user_client_id()
    );

-- Only superadmin and admin can insert sites
CREATE POLICY sites_insert_policy ON sites
    FOR INSERT
    WITH CHECK (current_user_role() IN ('superadmin', 'admin'));

-- Sites can be updated by authorized users
CREATE POLICY sites_update_policy ON sites
    FOR UPDATE
    USING (
        current_user_role() IN ('superadmin', 'admin') OR
        (current_user_role() = 'client_admin' AND client_id = current_user_client_id())
    );

-- Only superadmin and admin can delete sites
CREATE POLICY sites_delete_policy ON sites
    FOR DELETE
    USING (current_user_role() IN ('superadmin', 'admin'));

-- =====================================================
-- USERS TABLE RLS POLICIES
-- =====================================================

-- Users visibility based on role and client relationship
CREATE POLICY users_select_policy ON users
    FOR SELECT
    USING (
        current_user_role() IN ('superadmin', 'admin', 'technician') OR
        client_id = current_user_client_id() OR
        user_id = current_user_id()
    );

-- Only superadmin and admin can insert users
CREATE POLICY users_insert_policy ON users
    FOR INSERT
    WITH CHECK (current_user_role() IN ('superadmin', 'admin'));

-- Users can update their own profile, admins can update within client
CREATE POLICY users_update_policy ON users
    FOR UPDATE
    USING (
        current_user_role() IN ('superadmin', 'admin') OR
        (current_user_role() = 'client_admin' AND client_id = current_user_client_id()) OR
        user_id = current_user_id()
    );

-- Only superadmin can delete users (with protection)
CREATE POLICY users_delete_policy ON users
    FOR DELETE
    USING (
        current_user_role() = 'superadmin' AND
        user_id != current_user_id() -- Prevent self-deletion
    );

-- =====================================================
-- USER SITE ASSIGNMENTS TABLE RLS POLICIES
-- =====================================================

CREATE POLICY user_site_assignments_select_policy ON user_site_assignments
    FOR SELECT
    USING (
        current_user_role() IN ('superadmin', 'admin', 'technician') OR
        user_id = current_user_id() OR
        site_id = ANY(current_user_site_ids())
    );

CREATE POLICY user_site_assignments_insert_policy ON user_site_assignments
    FOR INSERT
    WITH CHECK (current_user_role() IN ('superadmin', 'admin'));

CREATE POLICY user_site_assignments_delete_policy ON user_site_assignments
    FOR DELETE
    USING (current_user_role() IN ('superadmin', 'admin'));

-- =====================================================
-- ASSETS TABLE RLS POLICIES
-- =====================================================

-- Assets visibility based on client and site access
CREATE POLICY assets_select_policy ON assets
    FOR SELECT
    USING (
        current_user_role() IN ('superadmin', 'admin', 'technician') OR
        client_id = current_user_client_id() OR
        site_id = ANY(current_user_site_ids())
    );

CREATE POLICY assets_insert_policy ON assets
    FOR INSERT
    WITH CHECK (current_user_role() IN ('superadmin', 'admin'));

CREATE POLICY assets_update_policy ON assets
    FOR UPDATE
    USING (
        current_user_role() IN ('superadmin', 'admin', 'technician') OR
        (current_user_role() = 'client_admin' AND client_id = current_user_client_id())
    );

CREATE POLICY assets_delete_policy ON assets
    FOR DELETE
    USING (current_user_role() IN ('superadmin', 'admin'));

-- =====================================================
-- TICKETS TABLE RLS POLICIES
-- =====================================================

-- Tickets visibility based on role and client/site relationship
CREATE POLICY tickets_select_policy ON tickets
    FOR SELECT
    USING (
        current_user_role() IN ('superadmin', 'admin', 'technician') OR
        client_id = current_user_client_id() OR
        site_id = ANY(current_user_site_ids()) OR
        created_by = current_user_id() OR
        assigned_to = current_user_id()
    );

-- Tickets can be created by authorized users
CREATE POLICY tickets_insert_policy ON tickets
    FOR INSERT
    WITH CHECK (
        current_user_role() IN ('superadmin', 'admin', 'technician', 'client_admin', 'solicitante')
    );

-- Tickets can be updated by authorized users
CREATE POLICY tickets_update_policy ON tickets
    FOR UPDATE
    USING (
        current_user_role() IN ('superadmin', 'admin', 'technician') OR
        (current_user_role() = 'client_admin' AND client_id = current_user_client_id()) OR
        created_by = current_user_id() OR
        assigned_to = current_user_id()
    );

-- Only superadmin and admin can delete tickets
CREATE POLICY tickets_delete_policy ON tickets
    FOR DELETE
    USING (current_user_role() IN ('superadmin', 'admin'));

-- =====================================================
-- TICKET COMMENTS TABLE RLS POLICIES
-- =====================================================

CREATE POLICY ticket_comments_select_policy ON ticket_comments
    FOR SELECT
    USING (
        current_user_role() IN ('superadmin', 'admin', 'technician') OR
        EXISTS (
            SELECT 1 FROM tickets t
            WHERE t.ticket_id = ticket_comments.ticket_id
            AND (
                t.client_id = current_user_client_id() OR
                t.site_id = ANY(current_user_site_ids()) OR
                t.created_by = current_user_id() OR
                t.assigned_to = current_user_id()
            )
        )
    );

CREATE POLICY ticket_comments_insert_policy ON ticket_comments
    FOR INSERT
    WITH CHECK (
        current_user_role() IN ('superadmin', 'admin', 'technician', 'client_admin', 'solicitante') AND
        EXISTS (
            SELECT 1 FROM tickets t
            WHERE t.ticket_id = ticket_comments.ticket_id
            AND (
                current_user_role() IN ('superadmin', 'admin', 'technician') OR
                t.client_id = current_user_client_id() OR
                t.site_id = ANY(current_user_site_ids()) OR
                t.created_by = current_user_id() OR
                t.assigned_to = current_user_id()
            )
        )
    );

CREATE POLICY ticket_comments_update_policy ON ticket_comments
    FOR UPDATE
    USING (
        current_user_role() IN ('superadmin', 'admin') OR
        user_id = current_user_id()
    );

CREATE POLICY ticket_comments_delete_policy ON ticket_comments
    FOR DELETE
    USING (
        current_user_role() IN ('superadmin', 'admin') OR
        user_id = current_user_id()
    );

-- =====================================================
-- FILE ATTACHMENTS TABLE RLS POLICIES
-- =====================================================

CREATE POLICY file_attachments_select_policy ON file_attachments
    FOR SELECT
    USING (
        current_user_role() IN ('superadmin', 'admin', 'technician') OR
        uploaded_by = current_user_id() OR
        EXISTS (
            SELECT 1 FROM tickets t
            WHERE t.ticket_id = file_attachments.ticket_id
            AND (
                t.client_id = current_user_client_id() OR
                t.site_id = ANY(current_user_site_ids()) OR
                t.created_by = current_user_id() OR
                t.assigned_to = current_user_id()
            )
        )
    );

CREATE POLICY file_attachments_insert_policy ON file_attachments
    FOR INSERT
    WITH CHECK (
        current_user_role() IN ('superadmin', 'admin', 'technician', 'client_admin', 'solicitante')
    );

CREATE POLICY file_attachments_delete_policy ON file_attachments
    FOR DELETE
    USING (
        current_user_role() IN ('superadmin', 'admin') OR
        uploaded_by = current_user_id()
    );

-- =====================================================
-- SLA TABLES RLS POLICIES
-- =====================================================

-- SLAs table
CREATE POLICY slas_select_policy ON slas
    FOR SELECT
    USING (
        current_user_role() IN ('superadmin', 'admin', 'technician') OR
        client_id = current_user_client_id()
    );

CREATE POLICY slas_insert_policy ON slas
    FOR INSERT
    WITH CHECK (current_user_role() IN ('superadmin', 'admin'));

CREATE POLICY slas_update_policy ON slas
    FOR UPDATE
    USING (current_user_role() IN ('superadmin', 'admin'));

CREATE POLICY slas_delete_policy ON slas
    FOR DELETE
    USING (current_user_role() IN ('superadmin', 'admin'));

-- SLA compliance table
CREATE POLICY sla_compliance_select_policy ON sla_compliance
    FOR SELECT
    USING (
        current_user_role() IN ('superadmin', 'admin', 'technician') OR
        EXISTS (
            SELECT 1 FROM tickets t
            WHERE t.ticket_id = sla_compliance.ticket_id
            AND (
                t.client_id = current_user_client_id() OR
                t.site_id = ANY(current_user_site_ids())
            )
        )
    );

CREATE POLICY sla_compliance_insert_policy ON sla_compliance
    FOR INSERT
    WITH CHECK (current_user_role() IN ('superadmin', 'admin', 'technician'));

CREATE POLICY sla_compliance_update_policy ON sla_compliance
    FOR UPDATE
    USING (current_user_role() IN ('superadmin', 'admin', 'technician'));

-- =====================================================
-- EMAIL TEMPLATES TABLE RLS POLICIES
-- =====================================================

CREATE POLICY email_templates_select_policy ON email_templates
    FOR SELECT
    USING (
        current_user_role() IN ('superadmin', 'admin', 'technician') OR
        client_id = current_user_client_id() OR
        client_id IS NULL -- System-wide templates
    );

CREATE POLICY email_templates_insert_policy ON email_templates
    FOR INSERT
    WITH CHECK (current_user_role() IN ('superadmin', 'admin'));

CREATE POLICY email_templates_update_policy ON email_templates
    FOR UPDATE
    USING (current_user_role() IN ('superadmin', 'admin'));

CREATE POLICY email_templates_delete_policy ON email_templates
    FOR DELETE
    USING (current_user_role() IN ('superadmin', 'admin'));

-- =====================================================
-- TECHNICIAN ASSIGNMENTS TABLE RLS POLICIES
-- =====================================================

CREATE POLICY technician_assignments_select_policy ON technician_assignments
    FOR SELECT
    USING (
        current_user_role() IN ('superadmin', 'admin', 'technician') OR
        client_id = current_user_client_id() OR
        technician_id = current_user_id()
    );

CREATE POLICY technician_assignments_insert_policy ON technician_assignments
    FOR INSERT
    WITH CHECK (current_user_role() IN ('superadmin', 'admin'));

CREATE POLICY technician_assignments_update_policy ON technician_assignments
    FOR UPDATE
    USING (current_user_role() IN ('superadmin', 'admin'));

CREATE POLICY technician_assignments_delete_policy ON technician_assignments
    FOR DELETE
    USING (current_user_role() IN ('superadmin', 'admin'));

-- =====================================================
-- AUDIT LOG TABLE RLS POLICIES
-- =====================================================

CREATE POLICY audit_log_select_policy ON audit_log
    FOR SELECT
    USING (
        current_user_role() IN ('superadmin', 'admin') OR
        user_id = current_user_id()
    );

CREATE POLICY audit_log_insert_policy ON audit_log
    FOR INSERT
    WITH CHECK (true); -- Allow all inserts for audit logging

-- =====================================================
-- PASSWORD RESET TOKENS TABLE RLS POLICIES
-- =====================================================

CREATE POLICY password_reset_tokens_select_policy ON password_reset_tokens
    FOR SELECT
    USING (
        current_user_role() IN ('superadmin', 'admin') OR
        user_id = current_user_id()
    );

CREATE POLICY password_reset_tokens_insert_policy ON password_reset_tokens
    FOR INSERT
    WITH CHECK (true); -- Allow token creation for password reset

CREATE POLICY password_reset_tokens_update_policy ON password_reset_tokens
    FOR UPDATE
    USING (
        current_user_role() IN ('superadmin', 'admin') OR
        user_id = current_user_id()
    );

CREATE POLICY password_reset_tokens_delete_policy ON password_reset_tokens
    FOR DELETE
    USING (
        current_user_role() IN ('superadmin', 'admin') OR
        user_id = current_user_id()
    );

-- =====================================================
-- SOFTWARE LICENSES TABLE RLS POLICIES
-- =====================================================

CREATE POLICY software_licenses_select_policy ON software_licenses
    FOR SELECT
    USING (
        current_user_role() IN ('superadmin', 'admin', 'technician') OR
        client_id = current_user_client_id()
    );

CREATE POLICY software_licenses_insert_policy ON software_licenses
    FOR INSERT
    WITH CHECK (current_user_role() IN ('superadmin', 'admin'));

CREATE POLICY software_licenses_update_policy ON software_licenses
    FOR UPDATE
    USING (
        current_user_role() IN ('superadmin', 'admin') OR
        (current_user_role() = 'client_admin' AND client_id = current_user_client_id())
    );

CREATE POLICY software_licenses_delete_policy ON software_licenses
    FOR DELETE
    USING (current_user_role() IN ('superadmin', 'admin'));

-- =====================================================
-- TICKET CATEGORIES TABLE RLS POLICIES
-- =====================================================

CREATE POLICY ticket_categories_select_policy ON ticket_categories
    FOR SELECT
    USING (
        current_user_role() IN ('superadmin', 'admin', 'technician') OR
        client_id = current_user_client_id() OR
        client_id IS NULL -- System-wide categories
    );

CREATE POLICY ticket_categories_insert_policy ON ticket_categories
    FOR INSERT
    WITH CHECK (current_user_role() IN ('superadmin', 'admin'));

CREATE POLICY ticket_categories_update_policy ON ticket_categories
    FOR UPDATE
    USING (current_user_role() IN ('superadmin', 'admin'));

CREATE POLICY ticket_categories_delete_policy ON ticket_categories
    FOR DELETE
    USING (current_user_role() IN ('superadmin', 'admin'));

-- =====================================================
-- SYSTEM CONFIG TABLE RLS POLICIES
-- =====================================================

CREATE POLICY system_config_select_policy ON system_config
    FOR SELECT
    USING (current_user_role() IN ('superadmin', 'admin'));

CREATE POLICY system_config_insert_policy ON system_config
    FOR INSERT
    WITH CHECK (current_user_role() IN ('superadmin', 'admin'));

CREATE POLICY system_config_update_policy ON system_config
    FOR UPDATE
    USING (current_user_role() IN ('superadmin', 'admin'));

CREATE POLICY system_config_delete_policy ON system_config
    FOR DELETE
    USING (current_user_role() = 'superadmin');

-- =====================================================
-- GRANT PERMISSIONS TO ROLES
-- =====================================================

-- Create database roles if they don't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'app_user') THEN
        CREATE ROLE app_user;
    END IF;
END
$$;

-- Grant necessary permissions to app_user role
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO app_user;

-- Grant permissions for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT EXECUTE ON FUNCTIONS TO app_user;

-- =====================================================
-- RLS TESTING FUNCTION
-- =====================================================

CREATE OR REPLACE FUNCTION test_rls_policies()
RETURNS TABLE(
    test_name TEXT,
    result BOOLEAN,
    message TEXT
) AS $$
BEGIN
    -- Test 1: Verify RLS is enabled on all tables
    RETURN QUERY
    SELECT
        'RLS Enabled Check'::TEXT,
        (SELECT COUNT(*) = 16 FROM pg_class c
         JOIN pg_namespace n ON c.relnamespace = n.oid
         WHERE n.nspname = 'public'
         AND c.relkind = 'r'
         AND c.relrowsecurity = true),
        'All tables should have RLS enabled'::TEXT;

    -- Test 2: Verify helper functions exist
    RETURN QUERY
    SELECT
        'Helper Functions Check'::TEXT,
        (SELECT COUNT(*) = 4 FROM pg_proc p
         JOIN pg_namespace n ON p.pronamespace = n.oid
         WHERE n.nspname = 'public'
         AND p.proname IN ('current_user_id', 'current_user_role', 'current_user_client_id', 'current_user_site_ids')),
        'All RLS helper functions should exist'::TEXT;

    RETURN;
END;
$$ LANGUAGE plpgsql;
