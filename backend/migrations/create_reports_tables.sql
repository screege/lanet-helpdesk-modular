-- LANET Helpdesk V3 - Reports Module Database Schema
-- Creates all necessary tables for the reporting system

-- Report Templates Table
CREATE TABLE IF NOT EXISTS report_templates (
    template_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    report_type VARCHAR(50) NOT NULL DEFAULT 'dashboard',
    template_config JSONB DEFAULT '{}',
    is_system BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(user_id)
);

-- Report Configurations Table
CREATE TABLE IF NOT EXISTS report_configurations (
    config_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    template_id UUID REFERENCES report_templates(template_id),
    client_id UUID REFERENCES clients(client_id),
    report_filters JSONB DEFAULT '{}',
    output_formats TEXT[] DEFAULT ARRAY['pdf'],
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(user_id)
);

-- Report Executions Table
CREATE TABLE IF NOT EXISTS report_executions (
    execution_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_id UUID REFERENCES report_configurations(config_id),
    status VARCHAR(50) DEFAULT 'pending',
    output_format VARCHAR(20) NOT NULL,
    file_path TEXT,
    file_size BIGINT,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_by UUID REFERENCES users(user_id)
);

-- Report Schedules Table
CREATE TABLE IF NOT EXISTS report_schedules (
    schedule_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    config_id UUID REFERENCES report_configurations(config_id),
    schedule_type VARCHAR(50) DEFAULT 'monthly',
    schedule_config JSONB DEFAULT '{}',
    recipients TEXT[] DEFAULT ARRAY[]::TEXT[],
    is_active BOOLEAN DEFAULT true,
    last_run_at TIMESTAMP WITH TIME ZONE,
    next_run_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(user_id)
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_report_configurations_client_id ON report_configurations(client_id);
CREATE INDEX IF NOT EXISTS idx_report_configurations_template_id ON report_configurations(template_id);
CREATE INDEX IF NOT EXISTS idx_report_configurations_created_by ON report_configurations(created_by);
CREATE INDEX IF NOT EXISTS idx_report_executions_config_id ON report_executions(config_id);
CREATE INDEX IF NOT EXISTS idx_report_executions_status ON report_executions(status);
CREATE INDEX IF NOT EXISTS idx_report_executions_created_at ON report_executions(created_at);
CREATE INDEX IF NOT EXISTS idx_report_schedules_config_id ON report_schedules(config_id);
CREATE INDEX IF NOT EXISTS idx_report_schedules_next_run_at ON report_schedules(next_run_at);
CREATE INDEX IF NOT EXISTS idx_report_schedules_is_active ON report_schedules(is_active);

-- Insert default report templates
INSERT INTO report_templates (name, description, report_type, template_config, is_system, created_by)
VALUES 
    (
        'Resumen Ejecutivo',
        'Reporte completo con métricas principales, gráficos y análisis de tendencias',
        'dashboard',
        '{"sections": ["summary", "tickets", "sla", "performance", "charts"], "include_charts": true, "include_details": true}',
        true,
        (SELECT user_id FROM users WHERE role = 'superadmin' LIMIT 1)
    ),
    (
        'Análisis de Tickets',
        'Reporte detallado de tickets por categoría, prioridad y estado',
        'tickets',
        '{"sections": ["tickets", "categories", "priorities"], "include_charts": true, "include_details": true}',
        true,
        (SELECT user_id FROM users WHERE role = 'superadmin' LIMIT 1)
    ),
    (
        'Cumplimiento SLA',
        'Reporte de cumplimiento de SLA y tiempos de respuesta',
        'sla',
        '{"sections": ["sla", "response_times", "resolution_times"], "include_charts": true, "include_details": true}',
        true,
        (SELECT user_id FROM users WHERE role = 'superadmin' LIMIT 1)
    ),
    (
        'Rendimiento de Técnicos',
        'Reporte de productividad y carga de trabajo de técnicos',
        'performance',
        '{"sections": ["technicians", "workload", "productivity"], "include_charts": true, "include_details": true}',
        true,
        (SELECT user_id FROM users WHERE role = 'superadmin' LIMIT 1)
    )
ON CONFLICT (name) DO NOTHING;

-- Add comments for documentation
COMMENT ON TABLE report_templates IS 'Plantillas de reportes del sistema';
COMMENT ON TABLE report_configurations IS 'Configuraciones de reportes creadas por usuarios';
COMMENT ON TABLE report_executions IS 'Historial de ejecuciones de reportes';
COMMENT ON TABLE report_schedules IS 'Programación automática de reportes';

-- Update timestamps trigger function (if not exists)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add update triggers
DROP TRIGGER IF EXISTS update_report_configurations_updated_at ON report_configurations;
CREATE TRIGGER update_report_configurations_updated_at
    BEFORE UPDATE ON report_configurations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_report_schedules_updated_at ON report_schedules;
CREATE TRIGGER update_report_schedules_updated_at
    BEFORE UPDATE ON report_schedules
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON report_templates TO postgres;
GRANT SELECT, INSERT, UPDATE, DELETE ON report_configurations TO postgres;
GRANT SELECT, INSERT, UPDATE, DELETE ON report_executions TO postgres;
GRANT SELECT, INSERT, UPDATE, DELETE ON report_schedules TO postgres;
