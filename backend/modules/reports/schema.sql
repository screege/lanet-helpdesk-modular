-- =====================================================
-- LANET HELPDESK V3 - REPORTING MODULE DATABASE SCHEMA
-- =====================================================

-- Report Templates Table
CREATE TABLE report_templates (
    template_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    report_type VARCHAR(50) NOT NULL, -- 'dashboard', 'tickets', 'sla', 'performance', 'custom'
    template_config JSONB NOT NULL, -- Configuration for report structure and fields
    chart_config JSONB, -- Chart configuration for visualizations
    is_active BOOLEAN DEFAULT true,
    is_system BOOLEAN DEFAULT false, -- System templates cannot be deleted
    created_by UUID REFERENCES users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT report_templates_type_check CHECK (report_type IN ('dashboard', 'tickets', 'sla', 'performance', 'custom'))
);

-- Report Configurations Table
CREATE TABLE report_configurations (
    config_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    template_id UUID NOT NULL REFERENCES report_templates(template_id),
    client_id UUID REFERENCES clients(client_id), -- NULL for global reports
    report_filters JSONB, -- Filters specific to this configuration
    output_formats TEXT[] DEFAULT ARRAY['pdf'], -- 'pdf', 'excel', 'csv'
    is_active BOOLEAN DEFAULT true,
    created_by UUID NOT NULL REFERENCES users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Report Schedules Table
CREATE TABLE report_schedules (
    schedule_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    config_id UUID NOT NULL REFERENCES report_configurations(config_id),
    name VARCHAR(255) NOT NULL,
    schedule_type VARCHAR(20) NOT NULL, -- 'daily', 'weekly', 'monthly', 'custom'
    schedule_config JSONB NOT NULL, -- Cron-like configuration
    recipients TEXT[] NOT NULL, -- Email addresses
    is_active BOOLEAN DEFAULT true,
    last_run_at TIMESTAMP WITH TIME ZONE,
    next_run_at TIMESTAMP WITH TIME ZONE,
    created_by UUID NOT NULL REFERENCES users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT report_schedules_type_check CHECK (schedule_type IN ('daily', 'weekly', 'monthly', 'custom'))
);

-- Report Executions Table
CREATE TABLE report_executions (
    execution_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    config_id UUID REFERENCES report_configurations(config_id),
    schedule_id UUID REFERENCES report_schedules(schedule_id), -- NULL for on-demand reports
    execution_type VARCHAR(20) NOT NULL, -- 'scheduled', 'manual'
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'running', 'completed', 'failed'
    output_format VARCHAR(10) NOT NULL, -- 'pdf', 'excel', 'csv'
    file_path TEXT, -- Path to generated report file
    file_size BIGINT, -- File size in bytes
    generation_time_ms INTEGER, -- Time taken to generate report
    error_message TEXT,
    executed_by UUID REFERENCES users(user_id),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT report_executions_type_check CHECK (execution_type IN ('scheduled', 'manual')),
    CONSTRAINT report_executions_status_check CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    CONSTRAINT report_executions_format_check CHECK (output_format IN ('pdf', 'excel', 'csv'))
);

-- Report Deliveries Table
CREATE TABLE report_deliveries (
    delivery_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    execution_id UUID NOT NULL REFERENCES report_executions(execution_id),
    recipient_email VARCHAR(255) NOT NULL,
    delivery_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'sent', 'failed'
    email_queue_id UUID REFERENCES email_queue(queue_id),
    error_message TEXT,
    sent_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT report_deliveries_status_check CHECK (delivery_status IN ('pending', 'sent', 'failed'))
);

-- Dashboard Widgets Table (for customizable dashboards)
CREATE TABLE dashboard_widgets (
    widget_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id),
    widget_type VARCHAR(50) NOT NULL, -- 'chart', 'metric', 'table', 'alert'
    widget_config JSONB NOT NULL, -- Widget configuration and data source
    position_x INTEGER DEFAULT 0,
    position_y INTEGER DEFAULT 0,
    width INTEGER DEFAULT 1,
    height INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Report Templates indexes
CREATE INDEX idx_report_templates_type ON report_templates(report_type);
CREATE INDEX idx_report_templates_active ON report_templates(is_active);

-- Report Configurations indexes
CREATE INDEX idx_report_configurations_template ON report_configurations(template_id);
CREATE INDEX idx_report_configurations_client ON report_configurations(client_id);
CREATE INDEX idx_report_configurations_active ON report_configurations(is_active);

-- Report Schedules indexes
CREATE INDEX idx_report_schedules_config ON report_schedules(config_id);
CREATE INDEX idx_report_schedules_next_run ON report_schedules(next_run_at);
CREATE INDEX idx_report_schedules_active ON report_schedules(is_active);

-- Report Executions indexes
CREATE INDEX idx_report_executions_config ON report_executions(config_id);
CREATE INDEX idx_report_executions_schedule ON report_executions(schedule_id);
CREATE INDEX idx_report_executions_status ON report_executions(status);
CREATE INDEX idx_report_executions_started ON report_executions(started_at);

-- Report Deliveries indexes
CREATE INDEX idx_report_deliveries_execution ON report_deliveries(execution_id);
CREATE INDEX idx_report_deliveries_status ON report_deliveries(delivery_status);

-- Dashboard Widgets indexes
CREATE INDEX idx_dashboard_widgets_user ON dashboard_widgets(user_id);
CREATE INDEX idx_dashboard_widgets_active ON dashboard_widgets(is_active);

-- =====================================================
-- ROW LEVEL SECURITY POLICIES
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE report_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE report_configurations ENABLE ROW LEVEL SECURITY;
ALTER TABLE report_schedules ENABLE ROW LEVEL SECURITY;
ALTER TABLE report_executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE report_deliveries ENABLE ROW LEVEL SECURITY;
ALTER TABLE dashboard_widgets ENABLE ROW LEVEL SECURITY;

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

-- =====================================================
-- INITIAL DATA - SYSTEM REPORT TEMPLATES
-- =====================================================

-- Insert default report templates
INSERT INTO report_templates (name, description, report_type, template_config, is_system) VALUES
('Dashboard Summary', 'Resumen ejecutivo del dashboard con métricas principales', 'dashboard', 
 '{"sections": ["tickets_overview", "sla_compliance", "technician_performance"], "charts": ["tickets_by_status", "sla_trends"]}', true),

('Ticket Performance Report', 'Reporte detallado de rendimiento de tickets', 'tickets',
 '{"sections": ["ticket_metrics", "resolution_times", "category_breakdown"], "filters": ["date_range", "priority", "status"]}', true),

('SLA Compliance Report', 'Reporte de cumplimiento de SLA por cliente y técnico', 'sla',
 '{"sections": ["sla_overview", "breach_analysis", "response_times"], "charts": ["compliance_trends", "breach_by_priority"]}', true),

('Technician Performance Report', 'Reporte de rendimiento individual de técnicos', 'performance',
 '{"sections": ["ticket_resolution", "response_times", "customer_satisfaction"], "charts": ["performance_trends"]}', true);
