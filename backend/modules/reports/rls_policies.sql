-- =====================================================
-- LANET HELPDESK V3 - REPORTING MODULE RLS POLICIES
-- =====================================================

-- Report Templates RLS Policies
CREATE POLICY report_templates_superadmin_all ON report_templates
    FOR ALL TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM get_current_user_info()
            WHERE role IN ('superadmin', 'admin')
        )
    );

CREATE POLICY report_templates_read_all ON report_templates
    FOR SELECT TO authenticated
    USING (is_active = true);

-- Report Configurations RLS Policies
CREATE POLICY report_configurations_superadmin_all ON report_configurations
    FOR ALL TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM get_current_user_info()
            WHERE role IN ('superadmin', 'admin', 'technician')
        )
    );

CREATE POLICY report_configurations_client_own ON report_configurations
    FOR ALL TO authenticated
    USING (
        client_id = (SELECT client_id FROM get_current_user_info())
        OR client_id IS NULL
    );

-- Report Schedules RLS Policies
CREATE POLICY report_schedules_superadmin_all ON report_schedules
    FOR ALL TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM get_current_user_info()
            WHERE role IN ('superadmin', 'admin', 'technician')
        )
    );

CREATE POLICY report_schedules_client_own ON report_schedules
    FOR ALL TO authenticated
    USING (
        config_id IN (
            SELECT config_id FROM report_configurations
            WHERE client_id = (SELECT client_id FROM get_current_user_info())
            OR client_id IS NULL
        )
    );

-- Report Executions RLS Policies
CREATE POLICY report_executions_superadmin_all ON report_executions
    FOR ALL TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM get_current_user_info()
            WHERE role IN ('superadmin', 'admin', 'technician')
        )
    );

CREATE POLICY report_executions_client_own ON report_executions
    FOR SELECT TO authenticated
    USING (
        config_id IN (
            SELECT config_id FROM report_configurations
            WHERE client_id = (SELECT client_id FROM get_current_user_info())
            OR client_id IS NULL
        )
    );

-- Report Deliveries RLS Policies
CREATE POLICY report_deliveries_superadmin_all ON report_deliveries
    FOR ALL TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM get_current_user_info()
            WHERE role IN ('superadmin', 'admin', 'technician')
        )
    );

-- Dashboard Widgets RLS Policies
CREATE POLICY dashboard_widgets_own_only ON dashboard_widgets
    FOR ALL TO authenticated
    USING (user_id = (SELECT user_id FROM get_current_user_info()));
