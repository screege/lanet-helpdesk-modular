#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - Reports Service
Business logic for report generation and management
"""

import logging
import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from flask import current_app

logger = logging.getLogger(__name__)

class ReportsService:
    """Service class for report management and generation"""
    
    def __init__(self):
        self.reports_dir = os.path.join(os.getcwd(), 'reports')
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)
    
    def get_available_templates(self, user_role: str) -> List[Dict]:
        """Get available report templates based on user role"""
        try:
            query = """
            SELECT template_id, name, description, report_type, template_config, 
                   chart_config, is_system, created_at
            FROM report_templates
            WHERE is_active = true
            ORDER BY is_system DESC, name ASC
            """
            
            templates = current_app.db_manager.execute_query(query)
            return templates or []
            
        except Exception as e:
            logger.error(f"Error getting available templates: {e}")
            return []
    
    def get_template_by_id(self, template_id: str) -> Optional[Dict]:
        """Get specific report template by ID"""
        try:
            query = """
            SELECT template_id, name, description, report_type, template_config,
                   chart_config, is_system, created_at
            FROM report_templates
            WHERE template_id = %s AND is_active = true
            """
            
            return current_app.db_manager.execute_query(query, (template_id,), fetch='one')
            
        except Exception as e:
            logger.error(f"Error getting template {template_id}: {e}")
            return None
    
    def get_user_configurations(self, user_role: str, client_id: str = None) -> List[Dict]:
        """Get report configurations for user based on role"""
        try:
            # Build query based on user role
            if user_role in ['superadmin', 'admin', 'technician']:
                # Can see all configurations
                query = """
                SELECT rc.config_id, rc.name, rc.description, rc.client_id,
                       rc.report_filters, rc.output_formats, rc.is_active,
                       rc.created_at, rt.name as template_name, rt.report_type,
                       c.name as client_name
                FROM report_configurations rc
                JOIN report_templates rt ON rc.template_id = rt.template_id
                LEFT JOIN clients c ON rc.client_id = c.client_id
                WHERE rc.is_active = true
                ORDER BY rc.created_at DESC
                """
                params = ()
            else:
                # Client users can only see their own configurations
                query = """
                SELECT rc.config_id, rc.name, rc.description, rc.client_id,
                       rc.report_filters, rc.output_formats, rc.is_active,
                       rc.created_at, rt.name as template_name, rt.report_type,
                       c.name as client_name
                FROM report_configurations rc
                JOIN report_templates rt ON rc.template_id = rt.template_id
                LEFT JOIN clients c ON rc.client_id = c.client_id
                WHERE rc.is_active = true 
                AND (rc.client_id = %s OR rc.client_id IS NULL)
                ORDER BY rc.created_at DESC
                """
                params = (client_id,)
            
            configurations = current_app.db_manager.execute_query(query, params, fetch='all')
            return configurations or []
            
        except Exception as e:
            logger.error(f"Error getting user configurations: {e}")
            return []
    
    def create_configuration(self, name: str, template_id: str, created_by: str,
                           description: str = None, client_id: str = None,
                           report_filters: Dict = None, output_formats: List[str] = None) -> Optional[str]:
        """Create new report configuration"""
        try:
            # Validate template exists
            template = self.get_template_by_id(template_id)
            if not template:
                logger.error(f"Template {template_id} not found")
                return None
            
            # Validate output formats
            valid_formats = ['pdf', 'excel', 'csv']
            if output_formats:
                for fmt in output_formats:
                    if fmt not in valid_formats:
                        logger.error(f"Invalid output format: {fmt}")
                        return None
            else:
                output_formats = ['pdf']
            
            config_data = {
                'name': name,
                'description': description,
                'template_id': template_id,
                'client_id': client_id,
                'report_filters': json.dumps(report_filters or {}),
                'output_formats': output_formats,
                'created_by': created_by
            }
            
            result = current_app.db_manager.execute_insert('report_configurations', config_data)
            return result.get('config_id') if result else None
            
        except Exception as e:
            logger.error(f"Error creating configuration: {e}")
            return None
    
    def update_configuration(self, config_id: str, data: Dict) -> bool:
        """Update report configuration"""
        try:
            # Build update data
            update_data = {}
            allowed_fields = ['name', 'description', 'report_filters', 'output_formats', 'is_active']
            
            for field in allowed_fields:
                if field in data:
                    if field == 'report_filters':
                        update_data[field] = json.dumps(data[field])
                    else:
                        update_data[field] = data[field]
            
            if not update_data:
                return False
            
            update_data['updated_at'] = datetime.utcnow()
            
            result = current_app.db_manager.execute_update(
                'report_configurations',
                update_data,
                {'config_id': config_id}
            )
            
            return result > 0
            
        except Exception as e:
            logger.error(f"Error updating configuration {config_id}: {e}")
            return False
    
    def delete_configuration(self, config_id: str) -> bool:
        """Delete report configuration (soft delete)"""
        try:
            update_data = {
                'is_active': False,
                'updated_at': datetime.utcnow()
            }
            
            result = current_app.db_manager.execute_update(
                'report_configurations',
                update_data,
                {'config_id': config_id}
            )
            
            return result > 0
            
        except Exception as e:
            logger.error(f"Error deleting configuration {config_id}: {e}")
            return False
    
    def generate_report(self, config_id: str, output_format: str, executed_by: str) -> Optional[str]:
        """Generate report on-demand"""
        try:
            # Get configuration
            config = current_app.db_manager.execute_query(
                """
                SELECT rc.*, rt.name as template_name, rt.template_config, rt.chart_config
                FROM report_configurations rc
                JOIN report_templates rt ON rc.template_id = rt.template_id
                WHERE rc.config_id = %s AND rc.is_active = true
                """,
                (config_id,),
                fetch='one'
            )
            
            if not config:
                logger.error(f"Configuration {config_id} not found")
                return None
            
            # Create execution record
            execution_data = {
                'config_id': config_id,
                'execution_type': 'manual',
                'status': 'pending',
                'output_format': output_format,
                'executed_by': executed_by
            }
            
            execution_result = current_app.db_manager.execute_insert('report_executions', execution_data)
            if not execution_result:
                return None
            
            execution_id = execution_result['execution_id']
            
            # Start report generation (this would be async in production)
            self._generate_report_file(execution_id, config, output_format)
            
            return execution_id
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return None
    
    def _generate_report_file(self, execution_id: str, config: Dict, output_format: str):
        """Generate the actual report file"""
        try:
            # Update status to running
            current_app.db_manager.execute_update(
                'report_executions',
                {'status': 'running', 'started_at': datetime.utcnow()},
                {'execution_id': execution_id}
            )
            
            start_time = datetime.utcnow()
            
            # Generate report based on template type
            report_data = self._collect_report_data(config)
            
            # Generate file based on format
            filename = f"report_{execution_id}.{output_format}"
            file_path = os.path.join(self.reports_dir, filename)
            
            if output_format == 'pdf':
                self._generate_pdf_report(file_path, config, report_data)
            elif output_format == 'excel':
                self._generate_excel_report(file_path, config, report_data)
            elif output_format == 'csv':
                self._generate_csv_report(file_path, config, report_data)
            
            # Calculate generation time
            end_time = datetime.utcnow()
            generation_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Get file size
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            
            # Update execution record
            current_app.db_manager.execute_update(
                'report_executions',
                {
                    'status': 'completed',
                    'file_path': file_path,
                    'file_size': file_size,
                    'generation_time_ms': generation_time_ms,
                    'completed_at': end_time
                },
                {'execution_id': execution_id}
            )
            
            logger.info(f"Report {execution_id} generated successfully in {generation_time_ms}ms")
            
        except Exception as e:
            logger.error(f"Error generating report file for execution {execution_id}: {e}")
            
            # Update status to failed
            current_app.db_manager.execute_update(
                'report_executions',
                {
                    'status': 'failed',
                    'error_message': str(e),
                    'completed_at': datetime.utcnow()
                },
                {'execution_id': execution_id}
            )
    
    def _collect_report_data(self, config: Dict) -> Dict:
        """Collect data for report generation"""
        try:
            template_config = config.get('template_config', {})
            if isinstance(template_config, str):
                template_config = json.loads(template_config)
            
            report_filters = config.get('report_filters', {})
            if isinstance(report_filters, str):
                report_filters = json.loads(report_filters)
            
            report_type = config.get('report_type', 'dashboard')
            
            # Collect data based on report type
            if report_type == 'dashboard':
                return self._collect_dashboard_data(report_filters)
            elif report_type == 'tickets':
                return self._collect_tickets_data(report_filters)
            elif report_type == 'sla':
                return self._collect_sla_data(report_filters)
            elif report_type == 'performance':
                return self._collect_performance_data(report_filters)
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Error collecting report data: {e}")
            return {}
    
    def _collect_dashboard_data(self, filters: Dict) -> Dict:
        """Collect dashboard data for reports"""
        try:
            # Get date range from filters - default to previous month for monthly reports
            if filters.get('report_period') == 'monthly':
                # For monthly reports, get previous month's data
                today = datetime.utcnow()
                if today.month == 1:
                    start_date = datetime(today.year - 1, 12, 1)
                    end_date = datetime(today.year, 1, 1) - timedelta(days=1)
                else:
                    start_date = datetime(today.year, today.month - 1, 1)
                    end_date = datetime(today.year, today.month, 1) - timedelta(days=1)
            else:
                # Default to last 30 days
                end_date = datetime.utcnow()
                start_date = end_date - timedelta(days=30)

            if filters.get('start_date') and filters.get('end_date'):
                try:
                    start_date = datetime.fromisoformat(filters['start_date'])
                    end_date = datetime.fromisoformat(filters['end_date'])
                except:
                    pass

            # Collect comprehensive metrics
            data = {
                'period': {
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'end_date': end_date.strftime('%Y-%m-%d'),
                    'start_date_formatted': start_date.strftime('%d de %B de %Y'),
                    'end_date_formatted': end_date.strftime('%d de %B de %Y'),
                    'month_name': start_date.strftime('%B %Y') if filters.get('report_period') == 'monthly' else None
                },
                'tickets': self._get_ticket_metrics(start_date, end_date, filters),
                'sla': self._get_sla_metrics(start_date, end_date, filters),
                'clients': self._get_client_metrics(filters),
                'technicians': self._get_technician_metrics(start_date, end_date, filters),
                'categories': self._get_category_metrics(start_date, end_date, filters),
                'priorities': self._get_priority_metrics(start_date, end_date, filters),
                'resolution_times': self._get_resolution_time_metrics(start_date, end_date, filters)
            }

            return data

        except Exception as e:
            logger.error(f"Error collecting dashboard data: {e}")
            return {}
    
    def _get_ticket_metrics(self, start_date: datetime, end_date: datetime, filters: Dict) -> Dict:
        """Get ticket metrics for report"""
        try:
            # Apply client filter if specified
            client_filter = ""
            params = [start_date, end_date]
            
            if filters.get('client_id'):
                client_filter = "AND t.client_id = %s"
                params.append(filters['client_id'])
            
            query = f"""
            SELECT 
                COUNT(*) as total_tickets,
                COUNT(CASE WHEN t.status IN ('nuevo', 'asignado', 'en_proceso', 'espera_cliente', 'reabierto') THEN 1 END) as open_tickets,
                COUNT(CASE WHEN t.status = 'resuelto' THEN 1 END) as resolved_tickets,
                COUNT(CASE WHEN t.status = 'cerrado' THEN 1 END) as closed_tickets,
                COUNT(CASE WHEN t.priority = 'alta' THEN 1 END) as high_priority,
                COUNT(CASE WHEN t.priority = 'media' THEN 1 END) as medium_priority,
                COUNT(CASE WHEN t.priority = 'baja' THEN 1 END) as low_priority,
                AVG(EXTRACT(EPOCH FROM (COALESCE(t.resolved_at, CURRENT_TIMESTAMP) - t.created_at))/3600) as avg_resolution_hours
            FROM tickets t
            WHERE t.created_at >= %s AND t.created_at <= %s
            {client_filter}
            """
            
            result = current_app.db_manager.execute_query(query, tuple(params), fetch='one')
            return result or {}
            
        except Exception as e:
            logger.error(f"Error getting ticket metrics: {e}")
            return {}

    def _get_sla_metrics(self, start_date: datetime, end_date: datetime, filters: Dict) -> Dict:
        """Get SLA metrics for report"""
        try:
            client_filter = ""
            params = [start_date, end_date]

            if filters.get('client_id'):
                client_filter = "AND t.client_id = %s"
                params.append(filters['client_id'])

            query = f"""
            SELECT
                COUNT(*) as total_tickets_with_sla,
                COUNT(CASE WHEN st.response_breach = true THEN 1 END) as response_breaches,
                COUNT(CASE WHEN st.resolution_breach = true THEN 1 END) as resolution_breaches,
                AVG(CASE WHEN st.response_time_minutes IS NOT NULL THEN st.response_time_minutes END) as avg_response_minutes,
                AVG(CASE WHEN st.resolution_time_minutes IS NOT NULL THEN st.resolution_time_minutes END) as avg_resolution_minutes
            FROM tickets t
            LEFT JOIN sla_tracking st ON t.ticket_id = st.ticket_id
            WHERE t.created_at >= %s AND t.created_at <= %s
            {client_filter}
            """

            result = current_app.db_manager.execute_query(query, tuple(params), fetch='one')

            # Calculate compliance percentages
            if result and result.get('total_tickets_with_sla', 0) > 0:
                total = result['total_tickets_with_sla']
                result['response_compliance'] = round(((total - (result.get('response_breaches', 0) or 0)) / total) * 100, 1)
                result['resolution_compliance'] = round(((total - (result.get('resolution_breaches', 0) or 0)) / total) * 100, 1)

            return result or {}

        except Exception as e:
            logger.error(f"Error getting SLA metrics: {e}")
            return {}

    def _get_client_metrics(self, filters: Dict) -> Dict:
        """Get client metrics for report"""
        try:
            client_filter = ""
            params = []

            if filters.get('client_id'):
                client_filter = "WHERE c.client_id = %s"
                params.append(filters['client_id'])

            query = f"""
            SELECT
                COUNT(DISTINCT c.client_id) as total_clients,
                COUNT(DISTINCT s.site_id) as total_sites,
                COUNT(DISTINCT u.user_id) as total_users,
                COUNT(DISTINCT t.ticket_id) as total_tickets
            FROM clients c
            LEFT JOIN sites s ON c.client_id = s.client_id AND s.is_active = true
            LEFT JOIN users u ON c.client_id = u.client_id AND u.is_active = true
            LEFT JOIN tickets t ON c.client_id = t.client_id
            {client_filter}
            """

            result = current_app.db_manager.execute_query(query, tuple(params), fetch='one')
            return result or {}

        except Exception as e:
            logger.error(f"Error getting client metrics: {e}")
            return {}

    def _get_technician_metrics(self, start_date: datetime, end_date: datetime, filters: Dict) -> Dict:
        """Get technician performance metrics"""
        try:
            query = """
            SELECT
                u.user_id,
                u.first_name,
                u.last_name,
                COUNT(t.ticket_id) as assigned_tickets,
                COUNT(CASE WHEN t.status = 'resuelto' THEN 1 END) as resolved_tickets,
                AVG(EXTRACT(EPOCH FROM (COALESCE(t.resolved_at, CURRENT_TIMESTAMP) - t.created_at))/3600) as avg_resolution_hours
            FROM users u
            LEFT JOIN tickets t ON u.user_id = t.assigned_to
                AND t.created_at >= %s AND t.created_at <= %s
            WHERE u.role = 'technician' AND u.is_active = true
            GROUP BY u.user_id, u.first_name, u.last_name
            ORDER BY resolved_tickets DESC
            """

            result = current_app.db_manager.execute_query(query, (start_date, end_date))
            return {'technicians': result or []}

        except Exception as e:
            logger.error(f"Error getting technician metrics: {e}")
            return {}

    def _collect_tickets_data(self, filters: Dict) -> Dict:
        """Collect detailed ticket data for reports"""
        try:
            # Implementation for ticket-specific reports
            return self._collect_dashboard_data(filters)

        except Exception as e:
            logger.error(f"Error collecting tickets data: {e}")
            return {}

    def _collect_sla_data(self, filters: Dict) -> Dict:
        """Collect SLA-specific data for reports"""
        try:
            # Implementation for SLA-specific reports
            return self._collect_dashboard_data(filters)

        except Exception as e:
            logger.error(f"Error collecting SLA data: {e}")
            return {}

    def _collect_performance_data(self, filters: Dict) -> Dict:
        """Collect performance data for reports"""
        try:
            # Implementation for performance-specific reports
            return self._collect_dashboard_data(filters)

        except Exception as e:
            logger.error(f"Error collecting performance data: {e}")
            return {}

    def _generate_pdf_report(self, file_path: str, config: Dict, data: Dict):
        """Generate PDF report using professional generator"""
        try:
            from .generators import report_generator
            report_generator.generate_report(file_path, config, data, 'pdf')
            logger.info(f"PDF report generated: {file_path}")

        except Exception as e:
            logger.error(f"Error generating PDF report: {e}")
            raise

    def _generate_excel_report(self, file_path: str, config: Dict, data: Dict):
        """Generate Excel report using professional generator"""
        try:
            from .generators import report_generator
            report_generator.generate_report(file_path, config, data, 'excel')
            logger.info(f"Excel report generated: {file_path}")

        except Exception as e:
            logger.error(f"Error generating Excel report: {e}")
            raise

    def _generate_csv_report(self, file_path: str, config: Dict, data: Dict):
        """Generate CSV report using professional generator"""
        try:
            from .generators import report_generator
            report_generator.generate_report(file_path, config, data, 'csv')
            logger.info(f"CSV report generated: {file_path}")

        except Exception as e:
            logger.error(f"Error generating CSV report: {e}")
            raise

    def get_execution_history(self, user_role: str, client_id: str = None,
                            limit: int = 50, offset: int = 0) -> List[Dict]:
        """Get report execution history"""
        try:
            logger.info(f"🔍 Obteniendo historial de ejecuciones para rol: {user_role}, client_id: {client_id}")

            # Build query based on user role - simplified version
            if user_role in ['superadmin', 'admin', 'technician']:
                query = """
                SELECT re.execution_id, re.config_id, re.execution_type, re.status, re.output_format,
                       re.file_path, re.file_size, re.started_at, re.completed_at,
                       re.error_message, re.executed_by,
                       CASE
                           WHEN re.file_path LIKE '%reporte_rapido%' THEN 'Reporte Rápido - Dashboard Ejecutivo'
                           WHEN re.file_path LIKE '%estadisticas_tickets%' THEN 'Reporte de Estadísticas de Tickets'
                           WHEN re.file_path LIKE '%cumplimiento_sla%' THEN 'Reporte de Cumplimiento SLA'
                           WHEN re.file_path LIKE '%resumen_clientes%' THEN 'Reporte Resumen de Clientes'
                           ELSE 'Reporte Rápido'
                       END as config_name,
                       COALESCE(u.name, 'Usuario') as executed_by_name
                FROM report_executions re
                LEFT JOIN users u ON re.executed_by = u.user_id
                ORDER BY re.started_at DESC
                LIMIT %s OFFSET %s
                """
                params = (limit, offset)
            else:
                query = """
                SELECT re.execution_id, re.config_id, re.execution_type, re.status, re.output_format,
                       re.file_path, re.file_size, re.started_at, re.completed_at,
                       re.error_message, re.executed_by,
                       CASE
                           WHEN re.file_path LIKE '%reporte_rapido%' THEN 'Reporte Rápido - Dashboard Ejecutivo'
                           WHEN re.file_path LIKE '%estadisticas_tickets%' THEN 'Reporte de Estadísticas de Tickets'
                           WHEN re.file_path LIKE '%cumplimiento_sla%' THEN 'Reporte de Cumplimiento SLA'
                           WHEN re.file_path LIKE '%resumen_clientes%' THEN 'Reporte Resumen de Clientes'
                           ELSE 'Reporte Rápido'
                       END as config_name,
                       COALESCE(u.name, 'Usuario') as executed_by_name
                FROM report_executions re
                LEFT JOIN users u ON re.executed_by = u.user_id
                ORDER BY re.started_at DESC
                LIMIT %s OFFSET %s
                """
                params = (limit, offset)

            logger.info(f"📋 Ejecutando query: {query}")
            logger.info(f"📋 Parámetros: {params}")

            try:
                executions = current_app.db_manager.execute_query(query, params, fetch='all')
                logger.info(f"✅ Query ejecutado exitosamente")
                logger.info(f"✅ Encontradas {len(executions) if executions else 0} ejecuciones")
                if executions:
                    logger.info(f"📋 Primera ejecución: {executions[0]}")
            except Exception as query_error:
                logger.error(f"💥 Error en query: {query_error}")
                import traceback
                logger.error(f"📋 Query traceback: {traceback.format_exc()}")
                return []

            return executions or []

        except Exception as e:
            logger.error(f"💥 Error getting execution history: {e}")
            import traceback
            logger.error(f"📋 Traceback: {traceback.format_exc()}")
            return []

    def get_report_file(self, execution_id: str, user_role: str, client_id: str = None) -> Optional[Dict]:
        """Get report file information for download"""
        try:
            # Build query based on user role - use LEFT JOIN to include quick reports
            if user_role in ['superadmin', 'admin', 'technician']:
                query = """
                SELECT re.file_path, re.output_format,
                       CASE
                           WHEN re.config_id IS NULL THEN
                               CASE
                                   WHEN re.file_path LIKE '%reporte_rapido%' THEN 'Reporte Rápido - Dashboard Ejecutivo'
                                   WHEN re.file_path LIKE '%estadisticas_tickets%' THEN 'Reporte de Estadísticas de Tickets'
                                   WHEN re.file_path LIKE '%cumplimiento_sla%' THEN 'Reporte de Cumplimiento SLA'
                                   WHEN re.file_path LIKE '%resumen_clientes%' THEN 'Reporte Resumen de Clientes'
                                   ELSE 'Reporte Rápido'
                               END
                           ELSE rc.name
                       END as config_name
                FROM report_executions re
                LEFT JOIN report_configurations rc ON re.config_id = rc.config_id
                WHERE re.execution_id = %s::uuid AND re.status = 'completed' AND re.file_path IS NOT NULL
                """
                params = (execution_id,)
            else:
                query = """
                SELECT re.file_path, re.output_format,
                       COALESCE(rc.name, 'Reporte Rápido') as config_name
                FROM report_executions re
                LEFT JOIN report_configurations rc ON re.config_id = rc.config_id
                WHERE re.execution_id = %s::uuid AND re.status = 'completed' AND re.file_path IS NOT NULL
                AND (rc.client_id = %s OR rc.client_id IS NULL OR re.config_id IS NULL)
                """
                params = (execution_id, client_id)

            result = current_app.db_manager.execute_query(query, params, fetch='one')

            if result:
                # Generate filename
                timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                filename = f"{result['config_name']}_{timestamp}.{result['output_format']}"
                result['filename'] = filename

            return result

        except Exception as e:
            logger.error(f"Error getting report file {execution_id}: {e}")
            return None

    def get_user_schedules(self, user_role: str, client_id: str = None) -> List[Dict]:
        """Get report schedules for user"""
        try:
            # Build query based on user role
            if user_role in ['superadmin', 'admin', 'technician']:
                query = """
                SELECT rs.schedule_id, rs.name, rs.schedule_type, rs.schedule_config,
                       rs.recipients, rs.is_active, rs.last_run_at, rs.next_run_at,
                       rs.created_at, rc.name as config_name, c.name as client_name
                FROM report_schedules rs
                JOIN report_configurations rc ON rs.config_id = rc.config_id
                LEFT JOIN clients c ON rc.client_id = c.client_id
                WHERE rs.is_active = true
                ORDER BY rs.created_at DESC
                """
                params = ()
            else:
                query = """
                SELECT rs.schedule_id, rs.name, rs.schedule_type, rs.schedule_config,
                       rs.recipients, rs.is_active, rs.last_run_at, rs.next_run_at,
                       rs.created_at, rc.name as config_name, c.name as client_name
                FROM report_schedules rs
                JOIN report_configurations rc ON rs.config_id = rc.config_id
                LEFT JOIN clients c ON rc.client_id = c.client_id
                WHERE rs.is_active = true
                AND (rc.client_id = %s OR rc.client_id IS NULL)
                ORDER BY rs.created_at DESC
                """
                params = (client_id,)

            schedules = current_app.db_manager.execute_query(query, params, fetch='all')
            return schedules or []

        except Exception as e:
            logger.error(f"Error getting user schedules: {e}")
            return []

    def create_schedule(self, name: str, config_id: str, schedule_type: str,
                       schedule_config: Dict, recipients: List[str], created_by: str) -> Optional[str]:
        """Create new report schedule"""
        try:
            # Validate configuration exists
            config = current_app.db_manager.execute_query(
                "SELECT config_id FROM report_configurations WHERE config_id = %s AND is_active = true",
                (config_id,),
                fetch='one'
            )

            if not config:
                logger.error(f"Configuration {config_id} not found")
                return None

            # Calculate next run time based on schedule
            next_run_at = self._calculate_next_run(schedule_type, schedule_config)

            schedule_data = {
                'name': name,
                'config_id': config_id,
                'schedule_type': schedule_type,
                'schedule_config': json.dumps(schedule_config),
                'recipients': recipients,
                'next_run_at': next_run_at,
                'created_by': created_by
            }

            result = current_app.db_manager.execute_insert('report_schedules', schedule_data)
            return result.get('schedule_id') if result else None

        except Exception as e:
            logger.error(f"Error creating schedule: {e}")
            return None

    def update_schedule(self, schedule_id: str, data: Dict) -> bool:
        """Update report schedule"""
        try:
            update_data = {}
            allowed_fields = ['name', 'schedule_type', 'schedule_config', 'recipients', 'is_active']

            for field in allowed_fields:
                if field in data:
                    if field == 'schedule_config':
                        update_data[field] = json.dumps(data[field])
                    else:
                        update_data[field] = data[field]

            if not update_data:
                return False

            # Recalculate next run if schedule changed
            if 'schedule_type' in data or 'schedule_config' in data:
                schedule_type = data.get('schedule_type')
                schedule_config = data.get('schedule_config', {})

                if schedule_type:
                    update_data['next_run_at'] = self._calculate_next_run(schedule_type, schedule_config)

            update_data['updated_at'] = datetime.utcnow()

            result = current_app.db_manager.execute_update(
                'report_schedules',
                update_data,
                {'schedule_id': schedule_id}
            )

            return result > 0

        except Exception as e:
            logger.error(f"Error updating schedule {schedule_id}: {e}")
            return False

    def delete_schedule(self, schedule_id: str) -> bool:
        """Delete report schedule (soft delete)"""
        try:
            update_data = {
                'is_active': False,
                'updated_at': datetime.utcnow()
            }

            result = current_app.db_manager.execute_update(
                'report_schedules',
                update_data,
                {'schedule_id': schedule_id}
            )

            return result > 0

        except Exception as e:
            logger.error(f"Error deleting schedule {schedule_id}: {e}")
            return False

    def _calculate_next_run(self, schedule_type: str, schedule_config: Dict) -> datetime:
        """Calculate next run time for schedule"""
        try:
            now = datetime.utcnow()

            if schedule_type == 'daily':
                # Run daily at specified hour (default 9 AM)
                hour = schedule_config.get('hour', 9)
                next_run = now.replace(hour=hour, minute=0, second=0, microsecond=0)
                if next_run <= now:
                    next_run += timedelta(days=1)
                return next_run

            elif schedule_type == 'weekly':
                # Run weekly on specified day (default Monday)
                weekday = schedule_config.get('weekday', 0)  # 0 = Monday
                hour = schedule_config.get('hour', 9)

                days_ahead = weekday - now.weekday()
                if days_ahead <= 0:  # Target day already happened this week
                    days_ahead += 7

                next_run = now + timedelta(days=days_ahead)
                next_run = next_run.replace(hour=hour, minute=0, second=0, microsecond=0)
                return next_run

            elif schedule_type == 'monthly':
                # Run monthly on specified day (default 1st)
                day = schedule_config.get('day', 1)
                hour = schedule_config.get('hour', 9)

                # Calculate next month's date
                if now.day >= day:
                    # Next month
                    if now.month == 12:
                        next_run = now.replace(year=now.year + 1, month=1, day=day, hour=hour, minute=0, second=0, microsecond=0)
                    else:
                        next_run = now.replace(month=now.month + 1, day=day, hour=hour, minute=0, second=0, microsecond=0)
                else:
                    # This month
                    next_run = now.replace(day=day, hour=hour, minute=0, second=0, microsecond=0)

                return next_run

            else:
                # Default to daily
                return now + timedelta(days=1)

        except Exception as e:
            logger.error(f"Error calculating next run: {e}")
            return datetime.utcnow() + timedelta(days=1)

    def _get_category_metrics(self, start_date: datetime, end_date: datetime, filters: Dict) -> Dict:
        """Get ticket metrics by category"""
        try:
            client_filter = ""
            params = [start_date, end_date]

            if filters.get('client_id'):
                client_filter = "AND t.client_id = %s"
                params.append(filters['client_id'])

            query = f"""
            SELECT
                c.name as category_name,
                COUNT(t.ticket_id) as total_tickets,
                COUNT(CASE WHEN t.status IN ('resuelto', 'cerrado') THEN 1 END) as resolved_tickets,
                AVG(EXTRACT(EPOCH FROM (COALESCE(t.resolved_at, CURRENT_TIMESTAMP) - t.created_at))/3600) as avg_resolution_hours
            FROM tickets t
            LEFT JOIN categories c ON t.category_id = c.category_id
            WHERE t.created_at >= %s AND t.created_at <= %s
            {client_filter}
            GROUP BY c.category_id, c.name
            ORDER BY total_tickets DESC
            """

            results = current_app.db_manager.execute_query(query, tuple(params))
            return {'categories': results or []}

        except Exception as e:
            logger.error(f"Error getting category metrics: {e}")
            return {'categories': []}

    def _get_priority_metrics(self, start_date: datetime, end_date: datetime, filters: Dict) -> Dict:
        """Get ticket metrics by priority"""
        try:
            client_filter = ""
            params = [start_date, end_date]

            if filters.get('client_id'):
                client_filter = "AND t.client_id = %s"
                params.append(filters['client_id'])

            query = f"""
            SELECT
                t.priority,
                COUNT(*) as total_tickets,
                COUNT(CASE WHEN t.status IN ('resuelto', 'cerrado') THEN 1 END) as resolved_tickets,
                COUNT(CASE WHEN t.status IN ('nuevo', 'asignado', 'en_proceso', 'espera_cliente', 'reabierto') THEN 1 END) as open_tickets,
                AVG(EXTRACT(EPOCH FROM (COALESCE(t.resolved_at, CURRENT_TIMESTAMP) - t.created_at))/3600) as avg_resolution_hours
            FROM tickets t
            WHERE t.created_at >= %s AND t.created_at <= %s
            {client_filter}
            GROUP BY t.priority
            ORDER BY
                CASE t.priority
                    WHEN 'alta' THEN 1
                    WHEN 'media' THEN 2
                    WHEN 'baja' THEN 3
                    ELSE 4
                END
            """

            results = current_app.db_manager.execute_query(query, tuple(params))
            return {'priorities': results or []}

        except Exception as e:
            logger.error(f"Error getting priority metrics: {e}")
            return {'priorities': []}

    def generate_report_direct(self, config: Dict, output_format: str) -> str:
        """Generate a report directly without saving configuration to database"""
        try:
            logger.info(f"🚀 Iniciando generate_report_direct con formato: {output_format}")

            # Create a temporary execution record
            execution_id = str(uuid.uuid4())
            logger.info(f"📋 ID de ejecución: {execution_id}")

            # Collect data using the same logic as regular reports
            filters = config.get('report_filters', {})
            if config.get('client_id'):
                filters['client_id'] = config['client_id']

            logger.info(f"🔍 Filtros aplicados: {filters}")
            data = self._collect_dashboard_data(filters)
            logger.info(f"📊 Datos recolectados: {len(data) if data else 0} elementos")

            # For now, let's create a simple mock file to test the flow
            import tempfile
            import json

            # Create a temporary file
            temp_dir = tempfile.gettempdir()
            file_name = f"quick_report_{execution_id}.{output_format}"
            file_path = os.path.join(temp_dir, file_name)

            logger.info(f"📁 Creando archivo temporal: {file_path}")

            # Create a simple test file
            if output_format == 'pdf':
                # Create a simple text file for now (we'll implement PDF later)
                with open(file_path.replace('.pdf', '.txt'), 'w', encoding='utf-8') as f:
                    f.write(f"Reporte PDF Rápido\nGenerado: {datetime.utcnow()}\nDatos: {json.dumps(data, indent=2, default=str)}")
                file_path = file_path.replace('.pdf', '.txt')
            elif output_format == 'excel':
                # Create a simple text file for now (we'll implement Excel later)
                with open(file_path.replace('.excel', '.txt'), 'w', encoding='utf-8') as f:
                    f.write(f"Reporte Excel Rápido\nGenerado: {datetime.utcnow()}\nDatos: {json.dumps(data, indent=2, default=str)}")
                file_path = file_path.replace('.excel', '.txt')
            else:
                raise ValueError(f"Formato no soportado: {output_format}")

            logger.info(f"✅ Archivo creado: {file_path}")

            if file_path and os.path.exists(file_path):
                # Save execution record to database
                query = """
                INSERT INTO report_executions (
                    execution_id, config_id, status, output_format,
                    file_path, created_at, completed_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """

                now = datetime.utcnow()
                logger.info(f"💾 Guardando en base de datos...")

                current_app.db_manager.execute_query(query, (
                    execution_id,
                    None,  # No config_id for quick reports
                    'completed',
                    output_format,
                    file_path,
                    now,
                    now
                ))

                logger.info(f"✅ Reporte rápido generado exitosamente: {execution_id}")
                return execution_id
            else:
                logger.error("❌ No se pudo generar el archivo del reporte")
                return None

        except Exception as e:
            logger.error(f"💥 Error generando reporte directo: {e}")
            import traceback
            logger.error(f"📋 Traceback completo: {traceback.format_exc()}")
            return None

# Create service instance
reports_service = ReportsService()
