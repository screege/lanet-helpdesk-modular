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
