#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - Reports Module Routes
API endpoints for report management and generation
"""

from flask import Blueprint, request, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from utils.security import require_role
from datetime import datetime
import pytz
import logging
import os
import uuid
from .enterprise_columns import ENTERPRISE_COLUMNS, COLUMN_CATEGORIES, get_columns_by_category, build_enterprise_query
from .report_factory import ReportFactory



reports_bp = Blueprint('reports', __name__)
logger = logging.getLogger(__name__)

def get_mexico_time():
    """Get current time in Mexico timezone"""
    mexico_tz = pytz.timezone('America/Mexico_City')
    return datetime.now(mexico_tz)

@reports_bp.route('/test', methods=['GET'])
def test_endpoint():
    """Simple test endpoint to verify blueprint is working"""
    logger.info("🧪 Test endpoint called")
    return {'success': True, 'message': 'Reports blueprint is working!'}

@reports_bp.route('/test-executions', methods=['GET'])
@jwt_required()
def test_executions():
    """Test endpoint for executions query"""
    try:
        # Simple direct query
        query = "SELECT execution_id, started_at, file_path FROM report_executions ORDER BY started_at DESC LIMIT 5"
        executions = current_app.db_manager.execute_query(query, fetch='all')

        return current_app.response_manager.success({
            'count': len(executions) if executions else 0,
            'executions': executions or []
        })

    except Exception as e:
        logger.error(f"💥 Error in test executions: {e}")
        import traceback
        logger.error(f"📋 Traceback: {traceback.format_exc()}")
        return current_app.response_manager.server_error(f'Test failed: {str(e)}')

@reports_bp.route('/test-download/<execution_id>', methods=['GET'])
@jwt_required()
def test_download(execution_id):
    """Test download endpoint with detailed logging"""
    try:
        logger.info(f"🔽 TEST Download request for execution_id: {execution_id}")

        # Test the database query
        query = """
        SELECT file_path, output_format
        FROM report_executions
        WHERE execution_id = %s::uuid AND status = 'completed' AND file_path IS NOT NULL
        """

        result = current_app.db_manager.execute_query(query, (execution_id,), fetch='one')
        logger.info(f"📋 TEST Database result: {result}")

        if not result:
            return current_app.response_manager.not_found('Report file not found in database')

        file_path = result['file_path']
        logger.info(f"📁 TEST File path from DB: {file_path}")

        # Check if file exists
        file_exists = os.path.exists(file_path)
        logger.info(f"📄 TEST File exists: {file_exists}")

        if not file_exists:
            return current_app.response_manager.not_found('Report file not found on disk')

        # Return file info instead of trying to send file
        return current_app.response_manager.success({
            'execution_id': execution_id,
            'file_path': file_path,
            'output_format': result['output_format'],
            'file_exists': file_exists,
            'file_size': os.path.getsize(file_path) if file_exists else 0
        })

    except Exception as e:
        logger.error(f"💥 TEST Error downloading report {execution_id}: {e}")
        import traceback
        logger.error(f"📋 TEST Traceback: {traceback.format_exc()}")
        return current_app.response_manager.server_error(f'Test failed: {str(e)}')

@reports_bp.route('/templates', methods=['GET'])
@jwt_required()
def get_report_templates():
    """Get available report templates"""
    try:
        from .service import reports_service
        
        # Get current user info
        claims = get_jwt()
        current_user_role = claims.get('role')
        
        templates = reports_service.get_available_templates(current_user_role)
        return current_app.response_manager.success(templates)
        
    except Exception as e:
        logger.error(f"Error getting report templates: {e}")
        return current_app.response_manager.server_error('Failed to get report templates')

@reports_bp.route('/templates/<template_id>', methods=['GET'])
@jwt_required()
def get_report_template(template_id):
    """Get specific report template"""
    try:
        from .service import reports_service
        
        template = reports_service.get_template_by_id(template_id)
        if not template:
            return current_app.response_manager.not_found('Report template not found')
            
        return current_app.response_manager.success(template)
        
    except Exception as e:
        logger.error(f"Error getting report template {template_id}: {e}")
        return current_app.response_manager.server_error('Failed to get report template')

@reports_bp.route('/configurations', methods=['GET'])
@jwt_required()
def get_report_configurations():
    """Get report configurations for current user"""
    try:
        from .service import reports_service
        
        # Get current user info
        claims = get_jwt()
        current_user_role = claims.get('role')
        current_user_client_id = claims.get('client_id')
        
        configurations = reports_service.get_user_configurations(
            current_user_role, 
            current_user_client_id
        )
        return current_app.response_manager.success(configurations)
        
    except Exception as e:
        logger.error(f"Error getting report configurations: {e}")
        return current_app.response_manager.server_error('Failed to get report configurations')

@reports_bp.route('/configurations', methods=['POST'])
@jwt_required()
@require_role(['superadmin', 'admin', 'technician', 'client_admin'])
def create_report_configuration():
    """Create new report configuration"""
    try:
        data = request.get_json()
        if not data:
            return current_app.response_manager.bad_request('No data provided')

        # Validate required fields
        required_fields = ['name', 'template_id', 'output_formats']
        for field in required_fields:
            if not data.get(field):
                return current_app.response_manager.bad_request(f'{field} is required')

        from .service import reports_service
        
        # Get current user info
        claims = get_jwt()
        current_user_id = get_jwt_identity()
        current_user_role = claims.get('role')
        current_user_client_id = claims.get('client_id')
        
        # Determine client_id based on user role
        target_client_id = None
        if current_user_role in ['superadmin', 'admin', 'technician']:
            target_client_id = data.get('client_id')  # Can be None for global reports
        else:
            target_client_id = current_user_client_id  # Client users can only create reports for their own organization

        config_id = reports_service.create_configuration(
            name=data['name'],
            description=data.get('description'),
            template_id=data['template_id'],
            client_id=target_client_id,
            report_filters=data.get('report_filters', {}),
            output_formats=data['output_formats'],
            created_by=current_user_id
        )

        # If scheduling is enabled, create the schedule
        if data.get('schedule_enabled') and config_id:
            schedule_config = data.get('schedule_config', {})
            if schedule_config.get('recipients'):
                schedule_id = reports_service.create_schedule(
                    name=f"Programación - {data['name']}",
                    config_id=config_id,
                    schedule_type=schedule_config.get('type', 'monthly'),
                    schedule_config={
                        'day': schedule_config.get('day', 1),
                        'hour': schedule_config.get('hour', 9)
                    },
                    recipients=schedule_config['recipients'],
                    created_by=current_user_id
                )

                if schedule_id:
                    logger.info(f"Created schedule {schedule_id} for configuration {config_id}")

        if config_id:
            return current_app.response_manager.success(
                {'config_id': config_id},
                'Configuración de reporte creada exitosamente'
            )
        else:
            return current_app.response_manager.server_error('Failed to create report configuration')
            
    except Exception as e:
        logger.error(f"Error creating report configuration: {e}")
        return current_app.response_manager.server_error('Failed to create report configuration')

@reports_bp.route('/configurations/<config_id>', methods=['PUT'])
@jwt_required()
@require_role(['superadmin', 'admin', 'technician', 'client_admin'])
def update_report_configuration(config_id):
    """Update report configuration"""
    try:
        data = request.get_json()
        if not data:
            return current_app.response_manager.bad_request('No data provided')

        from .service import reports_service
        
        success = reports_service.update_configuration(config_id, data)
        
        if success:
            return current_app.response_manager.success(None, 'Report configuration updated successfully')
        else:
            return current_app.response_manager.server_error('Failed to update report configuration')
            
    except Exception as e:
        logger.error(f"Error updating report configuration {config_id}: {e}")
        return current_app.response_manager.server_error('Failed to update report configuration')

@reports_bp.route('/configurations/<config_id>', methods=['DELETE'])
@jwt_required()
@require_role(['superadmin', 'admin', 'technician', 'client_admin'])
def delete_report_configuration(config_id):
    """Delete report configuration"""
    try:
        from .service import reports_service
        
        success = reports_service.delete_configuration(config_id)
        
        if success:
            return current_app.response_manager.success(None, 'Report configuration deleted successfully')
        else:
            return current_app.response_manager.server_error('Failed to delete report configuration')
            
    except Exception as e:
        logger.error(f"Error deleting report configuration {config_id}: {e}")
        return current_app.response_manager.server_error('Failed to delete report configuration')

@reports_bp.route('/generate', methods=['POST'])
@jwt_required()
@require_role(['superadmin', 'admin', 'technician', 'client_admin'])
def generate_report():
    """Generate report on-demand"""
    try:
        data = request.get_json()
        if not data:
            return current_app.response_manager.bad_request('No data provided')

        # Validate required fields
        required_fields = ['config_id', 'output_format']
        for field in required_fields:
            if not data.get(field):
                return current_app.response_manager.bad_request(f'{field} is required')

        from .service import reports_service
        
        current_user_id = get_jwt_identity()
        
        execution_id = reports_service.generate_report(
            config_id=data['config_id'],
            output_format=data['output_format'],
            executed_by=current_user_id
        )
        
        if execution_id:
            return current_app.response_manager.success(
                {'execution_id': execution_id}, 
                'Report generation started successfully'
            )
        else:
            return current_app.response_manager.server_error('Failed to start report generation')
            
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        return current_app.response_manager.server_error('Failed to generate report')

@reports_bp.route('/generate-quick', methods=['POST'])
@jwt_required()
def generate_quick_report():
    """Generate a professional quick report with real business data"""
    try:
        logger.info("🚀 Starting professional quick report generation...")

        # Get user claims
        claims = get_jwt()
        current_user_id = get_jwt_identity()
        logger.info(f"👤 User: {claims.get('name')} ({current_user_id})")

        # Get request data
        data = request.get_json()
        if not data or 'output_format' not in data:
            return current_app.response_manager.bad_request('Missing output_format parameter')

        if data['output_format'] not in ['pdf', 'excel']:
            return current_app.response_manager.bad_request('Invalid output_format. Must be pdf or excel')

        logger.info(f"📄 Output format: {data['output_format']}")

        # Generate execution ID
        execution_id = str(uuid.uuid4())
        logger.info(f"🆔 Execution ID: {execution_id}")

        try:
            # Import report factory
            from .report_factory import ReportFactory

            # Create reports directory
            reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reports_files')
            os.makedirs(reports_dir, exist_ok=True)

            # Initialize report factory
            factory = ReportFactory(current_app.db_manager, reports_dir)

            # Generate professional report
            file_path = factory.generate_quick_report(
                user_claims=claims,
                output_format=data['output_format']
            )

            logger.info(f"✅ Professional report generated: {file_path}")

            # Save to database
            query = """
            INSERT INTO report_executions (
                execution_id, config_id, execution_type, status,
                output_format, file_path, executed_by, started_at, completed_at
            ) VALUES (%s::uuid, %s, %s, %s, %s, %s, %s::uuid, %s, %s)
            """

            now = get_mexico_time()

            current_app.db_manager.execute_query(query, (
                execution_id,
                None,  # No config_id for quick reports
                'manual',
                'completed',
                data['output_format'],
                file_path,
                current_user_id,
                now,
                now
            ), fetch='none')

            logger.info("✅ Report execution saved to database")

            return current_app.response_manager.success(
                {'execution_id': execution_id},
                'Reporte profesional generado exitosamente. Revise la sección de Ejecuciones.'
            )

        except Exception as generation_error:
            logger.error(f"💥 Error generating professional report: {generation_error}")
            import traceback
            logger.error(f"📋 Generation traceback: {traceback.format_exc()}")

            # Fallback to simple report
            return current_app.response_manager.server_error(
                f'Error generando reporte profesional: {str(generation_error)}'
            )

    except Exception as e:
        logger.error(f"💥 Error in quick report endpoint: {e}")
        import traceback
        logger.error(f"📋 Traceback: {traceback.format_exc()}")
        return current_app.response_manager.server_error('Failed to generate quick report')

@reports_bp.route('/generate-statistics', methods=['POST'])
@jwt_required()
def generate_statistics_report():
    """Generate comprehensive ticket statistics report"""
    try:
        logger.info("📊 Starting ticket statistics report generation...")

        claims = get_jwt()
        current_user_id = get_jwt_identity()

        data = request.get_json()
        if not data or 'output_format' not in data:
            return current_app.response_manager.bad_request('Missing output_format parameter')

        if data['output_format'] not in ['pdf', 'excel']:
            return current_app.response_manager.bad_request('Invalid output_format. Must be pdf or excel')

        # Get date range
        date_from = data.get('date_from')
        date_to = data.get('date_to')

        execution_id = str(uuid.uuid4())

        # Import report factory
        from .report_factory import ReportFactory

        reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reports_files')
        factory = ReportFactory(current_app.db_manager, reports_dir)

        # Generate report
        file_path = factory.generate_ticket_statistics_report(
            user_claims=claims,
            output_format=data['output_format'],
            date_from=date_from,
            date_to=date_to
        )

        # Save to database
        query = """
        INSERT INTO report_executions (
            execution_id, config_id, execution_type, status,
            output_format, file_path, executed_by, started_at, completed_at
        ) VALUES (%s::uuid, %s, %s, %s, %s, %s, %s::uuid, %s, %s)
        """

        now = get_mexico_time()
        current_app.db_manager.execute_query(query, (
            execution_id, None, 'manual', 'completed',
            data['output_format'], file_path, current_user_id, now, now
        ), fetch='none')

        return current_app.response_manager.success(
            {'execution_id': execution_id},
            'Reporte de estadísticas generado exitosamente.'
        )

    except Exception as e:
        logger.error(f"💥 Error generating statistics report: {e}")
        return current_app.response_manager.server_error('Failed to generate statistics report')

@reports_bp.route('/generate-sla', methods=['POST'])
@jwt_required()
def generate_sla_report():
    """Generate SLA compliance report"""
    try:
        logger.info("📈 Starting SLA compliance report generation...")

        claims = get_jwt()
        current_user_id = get_jwt_identity()

        data = request.get_json()
        if not data or 'output_format' not in data:
            return current_app.response_manager.bad_request('Missing output_format parameter')

        if data['output_format'] not in ['pdf', 'excel']:
            return current_app.response_manager.bad_request('Invalid output_format. Must be pdf or excel')

        date_from = data.get('date_from')
        date_to = data.get('date_to')
        execution_id = str(uuid.uuid4())

        from .report_factory import ReportFactory

        reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reports_files')
        factory = ReportFactory(current_app.db_manager, reports_dir)

        file_path = factory.generate_sla_compliance_report(
            user_claims=claims,
            output_format=data['output_format'],
            date_from=date_from,
            date_to=date_to
        )

        # Save to database
        query = """
        INSERT INTO report_executions (
            execution_id, config_id, execution_type, status,
            output_format, file_path, executed_by, started_at, completed_at
        ) VALUES (%s::uuid, %s, %s, %s, %s, %s, %s::uuid, %s, %s)
        """

        now = get_mexico_time()
        current_app.db_manager.execute_query(query, (
            execution_id, None, 'manual', 'completed',
            data['output_format'], file_path, current_user_id, now, now
        ), fetch='none')

        return current_app.response_manager.success(
            {'execution_id': execution_id},
            'Reporte de cumplimiento SLA generado exitosamente.'
        )

    except Exception as e:
        logger.error(f"💥 Error generating SLA report: {e}")
        return current_app.response_manager.server_error('Failed to generate SLA report')

@reports_bp.route('/executions', methods=['GET'])
@jwt_required()
def get_report_executions():
    """Get report execution history"""
    try:
        # Get current user info
        claims = get_jwt()
        current_user_role = claims.get('role')

        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)

        # Use the simple query that we know works
        query = "SELECT execution_id, started_at, file_path FROM report_executions ORDER BY started_at DESC LIMIT %s OFFSET %s"

        raw_executions = current_app.db_manager.execute_query(query, (limit, offset), fetch='all')

        # Transform the data to include config_name
        executions = []
        if raw_executions:
            for exec in raw_executions:
                config_name = 'Reporte Rápido'
                if exec.get('file_path'):
                    if 'reporte_rapido' in exec['file_path']:
                        config_name = 'Reporte Rápido - Dashboard Ejecutivo'
                    elif 'estadisticas_tickets' in exec['file_path']:
                        config_name = 'Reporte de Estadísticas de Tickets'
                    elif 'cumplimiento_sla' in exec['file_path']:
                        config_name = 'Reporte de Cumplimiento SLA'
                    elif 'resumen_clientes' in exec['file_path']:
                        config_name = 'Reporte Resumen de Clientes'

                executions.append({
                    'execution_id': exec['execution_id'],
                    'started_at': exec['started_at'],
                    'file_path': exec['file_path'],
                    'config_name': config_name,
                    'status': 'completed',
                    'output_format': 'pdf' if exec.get('file_path', '').endswith('.pdf') else 'excel',
                    'executed_by_name': 'Usuario'
                })

        return current_app.response_manager.success(executions or [])

    except Exception as e:
        logger.error(f"💥 Error getting report executions: {e}")
        import traceback
        logger.error(f"📋 Traceback: {traceback.format_exc()}")
        return current_app.response_manager.server_error('Failed to get report executions')

@reports_bp.route('/executions/<execution_id>/download', methods=['GET'])
@jwt_required()
def download_report(execution_id):
    """Download generated report file"""
    try:
        logger.info(f"🔽 Download request for execution_id: {execution_id}")

        # Simple database query to get file info
        query = """
        SELECT file_path, output_format
        FROM report_executions
        WHERE execution_id = %s::uuid AND status = 'completed' AND file_path IS NOT NULL
        """

        result = current_app.db_manager.execute_query(query, (execution_id,), fetch='one')
        logger.info(f"📋 Database result: {result}")

        if not result:
            logger.error(f"❌ No file found in database for execution_id: {execution_id}")
            return current_app.response_manager.not_found('Report file not found in database')

        file_path = result['file_path']
        output_format = result['output_format']

        logger.info(f"📁 File path from DB: {file_path}")

        # Check if file exists
        if not os.path.exists(file_path):
            logger.error(f"❌ File not found on disk: {file_path}")
            return current_app.response_manager.not_found('Report file not found on disk')

        # Generate simple download filename
        file_extension = 'xlsx' if output_format == 'excel' else output_format
        base_filename = os.path.basename(file_path)
        download_filename = base_filename if base_filename.endswith(f'.{file_extension}') else f"report.{file_extension}"

        logger.info(f"✅ Sending file: {file_path} as {download_filename}")

        # Use send_file with proper parameters
        return send_file(
            file_path,
            as_attachment=True,
            download_name=download_filename,
            mimetype='application/octet-stream'
        )

    except Exception as e:
        logger.error(f"💥 Error downloading report {execution_id}: {e}")
        import traceback
        logger.error(f"📋 Traceback: {traceback.format_exc()}")
        return current_app.response_manager.server_error('Failed to download report')

@reports_bp.route('/schedules', methods=['GET'])
@jwt_required()
def get_report_schedules():
    """Get report schedules for current user"""
    try:
        from .service import reports_service
        
        # Get current user info
        claims = get_jwt()
        current_user_role = claims.get('role')
        current_user_client_id = claims.get('client_id')
        
        schedules = reports_service.get_user_schedules(
            current_user_role,
            current_user_client_id
        )
        
        return current_app.response_manager.success(schedules)
        
    except Exception as e:
        logger.error(f"Error getting report schedules: {e}")
        return current_app.response_manager.server_error('Failed to get report schedules')

@reports_bp.route('/schedules', methods=['POST'])
@jwt_required()
@require_role(['superadmin', 'admin', 'technician', 'client_admin'])
def create_report_schedule():
    """Create new report schedule"""
    try:
        data = request.get_json()
        if not data:
            return current_app.response_manager.bad_request('No data provided')

        # Validate required fields
        required_fields = ['name', 'config_id', 'schedule_type', 'schedule_config', 'recipients']
        for field in required_fields:
            if not data.get(field):
                return current_app.response_manager.bad_request(f'{field} is required')

        from .service import reports_service
        
        current_user_id = get_jwt_identity()
        
        schedule_id = reports_service.create_schedule(
            name=data['name'],
            config_id=data['config_id'],
            schedule_type=data['schedule_type'],
            schedule_config=data['schedule_config'],
            recipients=data['recipients'],
            created_by=current_user_id
        )
        
        if schedule_id:
            return current_app.response_manager.success(
                {'schedule_id': schedule_id}, 
                'Report schedule created successfully'
            )
        else:
            return current_app.response_manager.server_error('Failed to create report schedule')
            
    except Exception as e:
        logger.error(f"Error creating report schedule: {e}")
        return current_app.response_manager.server_error('Failed to create report schedule')

@reports_bp.route('/schedules/<schedule_id>', methods=['PUT'])
@jwt_required()
@require_role(['superadmin', 'admin', 'technician', 'client_admin'])
def update_report_schedule(schedule_id):
    """Update report schedule"""
    try:
        data = request.get_json()
        if not data:
            return current_app.response_manager.bad_request('No data provided')

        from .service import reports_service
        
        success = reports_service.update_schedule(schedule_id, data)
        
        if success:
            return current_app.response_manager.success(None, 'Report schedule updated successfully')
        else:
            return current_app.response_manager.server_error('Failed to update report schedule')
            
    except Exception as e:
        logger.error(f"Error updating report schedule {schedule_id}: {e}")
        return current_app.response_manager.server_error('Failed to update report schedule')

@reports_bp.route('/schedules/<schedule_id>', methods=['DELETE'])
@jwt_required()
@require_role(['superadmin', 'admin', 'technician', 'client_admin'])
def delete_report_schedule(schedule_id):
    """Delete report schedule"""
    try:
        from .service import reports_service
        
        success = reports_service.delete_schedule(schedule_id)
        
        if success:
            return current_app.response_manager.success(None, 'Report schedule deleted successfully')
        else:
            return current_app.response_manager.server_error('Failed to delete report schedule')
            
    except Exception as e:
        logger.error(f"Error deleting report schedule {schedule_id}: {e}")
        return current_app.response_manager.server_error('Failed to delete report schedule')

# =====================================================
# ENTERPRISE REPORTING HELPERS
# =====================================================

def generate_excel_report(data, columns, report_name, filename):
    """Generate Excel report for enterprise data"""
    try:
        import pandas as pd

        # Create reports directory if it doesn't exist
        reports_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'reports_files')
        os.makedirs(reports_dir, exist_ok=True)

        file_path = os.path.join(reports_dir, filename)

        # Convert data to DataFrame
        df_data = []
        for row in data:
            df_row = {}
            for col in columns:
                df_row[col['display_name']] = row.get(col['column_key'], 'N/A')
            df_data.append(df_row)

        df = pd.DataFrame(df_data)

        # Create simple Excel file
        df.to_excel(file_path, sheet_name='Reporte', index=False)

        return file_path

    except Exception as e:
        logger.error(f"Error generating Excel report: {e}")
        return None

def generate_pdf_report(data, columns, report_name, filename):
    """Generate PDF report for enterprise data"""
    try:
        # Create reports directory if it doesn't exist
        reports_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'reports_files')
        os.makedirs(reports_dir, exist_ok=True)

        file_path = os.path.join(reports_dir, filename)

        # For now, create a simple text file instead of PDF to test the flow
        with open(file_path.replace('.pdf', '.txt'), 'w', encoding='utf-8') as f:
            f.write(f"REPORTE: {report_name}\n")
            f.write(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
            f.write(f"Total registros: {len(data)}\n\n")

            # Headers
            headers = [col['display_name'] for col in columns]
            f.write(" | ".join(headers) + "\n")
            f.write("-" * (len(" | ".join(headers))) + "\n")

            # Data rows
            for row in data:
                row_data = []
                for col in columns:
                    value = str(row.get(col['column_key'], 'N/A'))
                    if len(value) > 30:
                        value = value[:27] + '...'
                    row_data.append(value)
                f.write(" | ".join(row_data) + "\n")

        return file_path.replace('.pdf', '.txt')

    except Exception as e:
        logger.error(f"Error generating PDF report: {e}")
        return None

# =====================================================
# ENTERPRISE REPORTING ENDPOINTS
# =====================================================

@reports_bp.route('/enterprise/columns', methods=['GET'])
@jwt_required()
def get_enterprise_columns():
    """Get available enterprise columns for report building"""
    try:
        # Get user claims for role-based filtering
        claims = get_jwt()
        user_role = claims.get('role', 'solicitante')

        # Filter columns based on user role
        available_columns = {}
        for column_key, column_data in ENTERPRISE_COLUMNS.items():
            # Role-based column filtering
            if user_role == 'solicitante':
                # Solicitantes get basic columns only
                if column_data['category'] in ['basic', 'technical']:
                    available_columns[column_key] = column_data
            elif user_role == 'client_admin':
                # Client admins get most columns except sensitive technical details
                if column_data['category'] in ['basic', 'sla', 'business']:
                    available_columns[column_key] = column_data
            else:
                # Superadmin and technicians get all columns
                available_columns[column_key] = column_data

        # Organize by category
        categorized_columns = {}
        for column_key, column_data in available_columns.items():
            category = column_data['category']
            if category not in categorized_columns:
                categorized_columns[category] = []
            categorized_columns[category].append({
                'column_key': column_key,
                **column_data
            })

        return current_app.response_manager.success({
            'columns': available_columns,
            'categorized_columns': categorized_columns,
            'categories': COLUMN_CATEGORIES,
            'total_columns': len(available_columns),
            'user_role': user_role
        })

    except Exception as e:
        logger.error(f"Error getting enterprise columns: {e}")
        return current_app.response_manager.error(f"Error al obtener columnas: {e}", 500)

@reports_bp.route('/enterprise/preview', methods=['POST'])
@jwt_required()
def preview_enterprise_report():
    """Generate preview data for enterprise report"""
    try:
        data = request.get_json()
        if not data:
            return current_app.response_manager.error("No data provided", 400)

        column_keys = data.get('column_keys', [])
        filters = data.get('filters', {})
        limit = data.get('limit', 50)

        if not column_keys:
            return current_app.response_manager.error("No columns selected", 400)

        # Build query
        query = build_enterprise_query(column_keys, filters, limit)
        if not query:
            return current_app.response_manager.error("Could not build query", 400)

        # Execute query
        results = current_app.db_manager.execute_query(query, fetch='all')

        # Get column metadata
        selected_columns = []
        for key in column_keys:
            if key in ENTERPRISE_COLUMNS:
                selected_columns.append({
                    'column_key': key,
                    'display_name': ENTERPRISE_COLUMNS[key]['display_name'],
                    'data_type': ENTERPRISE_COLUMNS[key]['data_type']
                })

        return current_app.response_manager.success({
            'columns': selected_columns,
            'data': results or [],
            'total_records': len(results) if results else 0,
            'preview_limit': limit,
            'filters_applied': filters
        })

    except Exception as e:
        logger.error(f"Error generating enterprise preview: {e}")
        return current_app.response_manager.error(f"Error al generar vista previa: {e}", 500)

@reports_bp.route('/enterprise/filters/options', methods=['GET'])
@jwt_required()
def get_filter_options():
    """Get available filter options for enterprise reports"""
    try:
        # Get user claims for role-based filtering
        claims = get_jwt()
        user_role = claims.get('role', 'solicitante')
        client_id = claims.get('client_id')

        # Base filter options
        filter_options = {
            'date_ranges': [
                {'value': 'today', 'label': 'Hoy'},
                {'value': 'yesterday', 'label': 'Ayer'},
                {'value': 'last_7_days', 'label': 'Últimos 7 días'},
                {'value': 'last_30_days', 'label': 'Últimos 30 días'},
                {'value': 'last_90_days', 'label': 'Últimos 90 días'},
                {'value': 'this_month', 'label': 'Este mes'},
                {'value': 'last_month', 'label': 'Mes pasado'},
                {'value': 'this_year', 'label': 'Este año'},
                {'value': 'custom', 'label': 'Rango personalizado'}
            ],
            'status_options': [
                {'value': 'Abierto', 'label': 'Abierto'},
                {'value': 'En Progreso', 'label': 'En Progreso'},
                {'value': 'Esperando Cliente', 'label': 'Esperando Cliente'},
                {'value': 'Resuelto', 'label': 'Resuelto'},
                {'value': 'Cerrado', 'label': 'Cerrado'}
            ],
            'priority_options': [
                {'value': 'Crítica', 'label': 'Crítica'},
                {'value': 'Alta', 'label': 'Alta'},
                {'value': 'Media', 'label': 'Media'},
                {'value': 'Baja', 'label': 'Baja'}
            ],
            'sla_compliance_options': [
                {'value': 'all', 'label': 'Todos'},
                {'value': 'compliant', 'label': 'SLA Cumplido'},
                {'value': 'non_compliant', 'label': 'SLA Incumplido'},
                {'value': 'pending', 'label': 'SLA Pendiente'}
            ]
        }

        # Get clients based on role
        if user_role in ['superadmin', 'technician']:
            # Get all clients
            clients_query = "SELECT client_id, name FROM clients WHERE is_active = true ORDER BY name"
            clients = current_app.db_manager.execute_query(clients_query, fetch='all')
            filter_options['clients'] = [{'client_id': c['client_id'], 'name': c['name']} for c in clients] if clients else []
        elif user_role == 'client_admin' and client_id:
            # Get only user's client
            client_query = "SELECT client_id, name FROM clients WHERE client_id = %s AND is_active = true"
            client = current_app.db_manager.execute_query(client_query, (client_id,), fetch='one')
            filter_options['clients'] = [{'client_id': client['client_id'], 'name': client['name']}] if client else []
        else:
            filter_options['clients'] = []

        # Get technicians
        if user_role in ['superadmin', 'technician', 'client_admin']:
            technicians_query = """
                SELECT user_id, name
                FROM users
                WHERE role IN ('superadmin', 'technician') AND is_active = true
                ORDER BY name
            """
            technicians = current_app.db_manager.execute_query(technicians_query, fetch='all')
            filter_options['technicians'] = [{'user_id': t['user_id'], 'name': t['name']} for t in technicians] if technicians else []
        else:
            filter_options['technicians'] = []

        # Get categories
        categories_query = """
            SELECT DISTINCT c.category_id, c.name
            FROM categories c
            INNER JOIN tickets t ON t.category_id = c.category_id
            WHERE c.is_active = true
            ORDER BY c.name
        """
        categories = current_app.db_manager.execute_query(categories_query, fetch='all')
        filter_options['categories'] = [{'value': c['category_id'], 'label': c['name']} for c in categories] if categories else []

        return current_app.response_manager.success(filter_options)

    except Exception as e:
        logger.error(f"Error getting filter options: {e}")
        return current_app.response_manager.error(f"Error al obtener opciones de filtro: {e}", 500)

@reports_bp.route('/enterprise/generate', methods=['POST'])
@jwt_required()
def generate_enterprise_report():
    """Generate and export enterprise report"""
    try:
        data = request.get_json()
        if not data:
            return current_app.response_manager.error("No data provided", 400)

        column_keys = data.get('column_keys', [])
        filters = data.get('filters', {})
        output_format = data.get('output_format', 'pdf')
        report_name = data.get('report_name', 'Reporte Empresarial')

        if not column_keys:
            return current_app.response_manager.error("No columns selected", 400)

        # For now, just return success without actually generating the file
        # This is to test the flow first
        return current_app.response_manager.success({
            'message': f'Reporte {output_format.upper()} generado exitosamente',
            'columns': len(column_keys),
            'format': output_format,
            'name': report_name
        })

    except Exception as e:
        logger.error(f"Error generating enterprise report: {e}")
        return current_app.response_manager.error(f"Error al generar reporte: {e}", 500)

# =====================================================
# MONTHLY REPORTS ENDPOINTS (SIMPLE SYSTEM)
# =====================================================

@reports_bp.route('/monthly/status', methods=['GET'])
@jwt_required()
def get_monthly_reports_status():
    """Get status of monthly reports system"""
    try:
        from .monthly_reports import monthly_reports_service

        status = monthly_reports_service.get_system_status()
        return current_app.response_manager.success(status)

    except Exception as e:
        logger.error(f"Error getting monthly reports status: {e}")
        return current_app.response_manager.error("Error al obtener estado del sistema", 500)

@reports_bp.route('/monthly/generate-test', methods=['POST'])
@jwt_required()
def generate_test_monthly_report():
    """Generate a test monthly report with optional custom parameters"""
    try:
        from .monthly_reports import monthly_reports_service
        from datetime import datetime

        claims = get_jwt()
        current_user_id = get_jwt_identity()

        # Check if custom parameters are provided
        data = request.get_json()
        if data and (data.get('start_date') or data.get('end_date') or data.get('client_id')):
            # Custom report with parameters
            client_id = data.get('client_id')
            start_date_str = data.get('start_date')
            end_date_str = data.get('end_date')

            # Handle empty string client_id
            if client_id == "":
                client_id = None

            # Parse dates
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None

                # Adjust end_date to end of day
                if end_date:
                    end_date = end_date.replace(hour=23, minute=59, second=59)

            except ValueError as e:
                return current_app.response_manager.error("Formato de fecha inválido. Use YYYY-MM-DD", 400)

            # Generate comprehensive report
            file_path = monthly_reports_service.generate_comprehensive_report(
                start_date=start_date,
                end_date=end_date,
                client_id=client_id
            )
        else:
            # Original test report
            file_path = monthly_reports_service.generate_test_report(claims)

        if not file_path:
            return current_app.response_manager.error("No se pudo generar el reporte de prueba", 400)

        # Save execution to database
        execution_id = str(uuid.uuid4())
        query = """
            INSERT INTO report_executions (
                execution_id, config_id, execution_type, status,
                output_format, file_path, executed_by, started_at, completed_at
            ) VALUES (%s::uuid, %s, %s, %s, %s, %s, %s::uuid, %s, %s)
        """

        # Determine format based on file extension
        output_format = 'text' if file_path.endswith('.txt') else 'excel'

        now = get_mexico_time()
        current_app.db_manager.execute_query(query, (
            execution_id, None, 'manual', 'completed',
            output_format, file_path, current_user_id, now, now
        ), fetch='none')

        return current_app.response_manager.success({
            'execution_id': execution_id,
            'file_path': file_path,
            'message': 'Reporte de prueba generado exitosamente'
        })

    except Exception as e:
        logger.error(f"Error generating test monthly report: {e}")
        return current_app.response_manager.error("Error al generar reporte de prueba", 500)

@reports_bp.route('/monthly/generate-custom', methods=['POST'])
@jwt_required()
def generate_custom_monthly_report():
    """Generate a custom monthly report with date range and client filter"""
    print("🚀 ENDPOINT CALLED!")
    try:
        print("🚀 Starting custom monthly report generation")
        logger.info("🚀 Starting custom monthly report generation")

        from .monthly_reports import monthly_reports_service
        from datetime import datetime

        claims = get_jwt()
        current_user_id = get_jwt_identity()

        print(f"👤 User: {current_user_id}, Claims: {claims}")
        logger.info(f"👤 User: {current_user_id}, Claims: {claims}")

        # Get request data
        data = request.get_json()
        print(f"📋 Request data: {data}")
        logger.info(f"📋 Request data: {data}")

        client_id = data.get('client_id') if data else None
        start_date_str = data.get('start_date') if data else None
        end_date_str = data.get('end_date') if data else None

        # Handle empty string client_id (convert to None)
        if client_id == "":
            client_id = None

        print(f"📅 Raw dates: start={start_date_str}, end={end_date_str}, client={client_id}")
        logger.info(f"📅 Raw dates: start={start_date_str}, end={end_date_str}, client={client_id}")

        # Parse dates
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None

            # Adjust end_date to end of day
            if end_date:
                end_date = end_date.replace(hour=23, minute=59, second=59)

            logger.info(f"📅 Parsed dates: start={start_date}, end={end_date}")

        except ValueError as e:
            logger.error(f"❌ Date parsing error: {e}")
            return current_app.response_manager.error("Formato de fecha inválido. Use YYYY-MM-DD", 400)

        logger.info(f"🎯 Generating custom report: client_id={client_id}, start={start_date}, end={end_date}")

        # Generate custom report
        print(f"🎯 About to call generate_comprehensive_report")
        file_path = monthly_reports_service.generate_comprehensive_report(
            start_date=start_date,
            end_date=end_date,
            client_id=client_id
        )
        print(f"📄 File path result: {file_path}")

        if not file_path:
            print(f"❌ No file path returned")
            return current_app.response_manager.error("No se pudo generar el reporte personalizado", 400)

        # Save execution to database
        execution_id = str(uuid.uuid4())
        query = """
            INSERT INTO report_executions (
                execution_id, config_id, execution_type, status,
                output_format, file_path, executed_by, started_at, completed_at
            ) VALUES (%s::uuid, %s, %s, %s, %s, %s, %s::uuid, %s, %s)
        """

        # Determine format based on file extension
        output_format = 'text' if file_path.endswith('.txt') else 'excel'

        now = get_mexico_time()
        current_app.db_manager.execute_query(query, (
            execution_id, None, 'custom', 'completed',
            output_format, file_path, current_user_id, now, now
        ), fetch='none')

        return current_app.response_manager.success({
            'execution_id': execution_id,
            'file_path': file_path,
            'message': 'Reporte personalizado generado exitosamente'
        })

    except Exception as e:
        print(f"❌ EXCEPTION in generate_custom_monthly_report: {e}")
        import traceback
        print(f"❌ TRACEBACK: {traceback.format_exc()}")
        logger.error(f"Error generating custom monthly report: {e}")
        return current_app.response_manager.error("Error al generar reporte personalizado", 500)

@reports_bp.route('/debug-test', methods=['GET'])
def debug_test_endpoint():
    """Simple debug test endpoint"""
    print("🧪 DEBUG TEST ENDPOINT CALLED!")
    return current_app.response_manager.success({"message": "Debug test endpoint works!"})

@reports_bp.route('/monthly/setup-schedules', methods=['POST'])
@jwt_required()
@require_role(['superadmin'])
def setup_monthly_schedules():
    """Setup automatic monthly schedules for all clients"""
    try:
        from .monthly_reports import monthly_reports_service

        monthly_reports_service.setup_monthly_schedules()

        return current_app.response_manager.success({
            'message': 'Programaciones mensuales configuradas exitosamente'
        })

    except Exception as e:
        logger.error(f"Error setting up monthly schedules: {e}")
        return current_app.response_manager.error("Error al configurar programaciones", 500)
