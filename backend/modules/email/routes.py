#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - Email Routes
Email configuration, queue management, and email-to-ticket endpoints
"""

from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.security import require_role
from .service import email_service
from datetime import datetime

email_bp = Blueprint('email', __name__)

@email_bp.route('/configurations', methods=['GET'])
@jwt_required()
@require_role(['superadmin', 'admin'])
def get_email_configurations():
    """Get all email configurations"""
    try:
        query = """
        SELECT config_id, name, description, smtp_host, smtp_port, smtp_username,
               smtp_use_ssl, smtp_use_tls, imap_host, imap_port, imap_username,
               enable_email_to_ticket, default_priority, subject_prefix,
               is_active, is_default, created_at, updated_at
        FROM email_configurations
        WHERE is_active = true
        ORDER BY is_default DESC, name
        """

        configurations = current_app.db_manager.execute_query(query)

        formatted_configs = []
        for config in (configurations or []):
            formatted_config = current_app.response_manager.format_email_config_data(config)
            formatted_configs.append(formatted_config)

        return current_app.response_manager.success(formatted_configs)

    except Exception as e:
        current_app.logger.error(f"Get email configurations error: {e}")
        return current_app.response_manager.server_error('Failed to get email configurations')



@email_bp.route('/incoming/check', methods=['POST'])
@jwt_required()
@require_role(['superadmin', 'admin'])
def check_incoming_emails():
    """Manually check for incoming emails"""
    try:
        data = request.get_json()
        config_id = data.get('config_id') if data else None

        incoming_emails = email_service.check_incoming_emails(config_id)
        processed_tickets = []

        # Process each incoming email
        for email_data in incoming_emails:
            config = email_service.get_config_by_id(config_id) if config_id else email_service.get_default_config()
            if config:
                ticket_id = email_service.process_incoming_email(email_data, config)
                if ticket_id:
                    processed_tickets.append({
                        'ticket_id': ticket_id,
                        'from_email': email_data['from_email'],
                        'subject': email_data['subject']
                    })

        return current_app.response_manager.success({
            'emails_found': len(incoming_emails),
            'tickets_processed': len(processed_tickets),
            'processed_tickets': processed_tickets
        })

    except Exception as e:
        current_app.logger.error(f"Check incoming emails error: {e}")
        return current_app.response_manager.server_error('Failed to check incoming emails')

@email_bp.route('/send', methods=['POST'])
@jwt_required()
def send_email():
    """Send email (for notifications)"""
    try:
        data = request.get_json()
        if not data:
            return current_app.response_manager.bad_request('No data provided')

        required_fields = ['to_email', 'subject', 'body']
        for field in required_fields:
            if not data.get(field):
                return current_app.response_manager.bad_request(f'{field} is required')

        # Queue email for background processing
        success = email_service.queue_email(
            to_email=data['to_email'],
            subject=data['subject'],
            body=data['body'],
            cc_emails=data.get('cc_emails'),
            bcc_emails=data.get('bcc_emails'),
            ticket_id=data.get('ticket_id'),
            user_id=get_jwt_identity(),
            priority=data.get('priority', 5),
            config_id=data.get('config_id')
        )

        if success:
            return current_app.response_manager.success({'message': 'Email queued successfully'})
        else:
            return current_app.response_manager.server_error('Failed to queue email')

    except Exception as e:
        current_app.logger.error(f"Send email error: {e}")
        return current_app.response_manager.server_error('Failed to send email')

@email_bp.route('/templates', methods=['GET'])
@jwt_required()
@require_role(['superadmin', 'admin'])
def get_email_templates():
    """Get all email templates"""
    try:
        templates = current_app.db_manager.execute_query(
            "SELECT * FROM email_templates WHERE is_active = true ORDER BY name"
        )

        return current_app.response_manager.success(templates)

    except Exception as e:
        current_app.logger.error(f"Get email templates error: {e}")
        return current_app.response_manager.server_error('Failed to get email templates')

@email_bp.route('/configurations/<config_id>', methods=['GET'])
@jwt_required()
@require_role(['superadmin', 'admin'])
def get_email_configuration(config_id):
    """Get specific email configuration"""
    try:
        query = """
        SELECT config_id, name, description, smtp_host, smtp_port, smtp_username,
               smtp_use_tls, smtp_use_ssl, imap_host, imap_port, imap_username,
               imap_use_ssl, imap_folder, enable_email_to_ticket,
               default_priority, subject_prefix, ticket_number_regex,
               auto_assign_to, default_client_id, default_category_id,
               is_active, is_default, created_at, updated_at
        FROM email_configurations
        WHERE config_id = %s
        """

        config = current_app.db_manager.execute_query(query, (config_id,), fetch='one')

        if not config:
            return current_app.response_manager.not_found('Email configuration not found')

        return current_app.response_manager.success(config)

    except Exception as e:
        current_app.logger.error(f"Error getting email configuration {config_id}: {e}")
        return current_app.response_manager.server_error('Failed to get email configuration')

@email_bp.route('/configurations', methods=['POST'])
@jwt_required()
@require_role(['superadmin', 'admin'])
def create_email_configuration():
    """Create new email configuration"""
    try:
        data = request.get_json()
        if not data:
            return current_app.response_manager.bad_request('No data provided')

        # Validate required fields
        required_fields = ['name', 'smtp_host', 'smtp_port', 'smtp_username', 'smtp_password']
        for field in required_fields:
            if not data.get(field):
                return current_app.response_manager.bad_request(f'{field} is required')

        # Encrypt passwords
        from utils.security import SecurityUtils
        smtp_password_encrypted = SecurityUtils.encrypt_password(data['smtp_password'])
        imap_password_encrypted = None
        if data.get('imap_password'):
            imap_password_encrypted = SecurityUtils.encrypt_password(data['imap_password'])

        # Prepare configuration data
        config_data = {
            'name': data['name'],
            'description': data.get('description'),
            'smtp_host': data['smtp_host'],
            'smtp_port': data['smtp_port'],
            'smtp_username': data['smtp_username'],
            'smtp_password_encrypted': smtp_password_encrypted,
            'smtp_use_tls': data.get('smtp_use_tls', True),
            'smtp_use_ssl': data.get('smtp_use_ssl', False),
            'imap_host': data.get('imap_host'),
            'imap_port': data.get('imap_port', 993),
            'imap_username': data.get('imap_username'),
            'imap_password_encrypted': imap_password_encrypted,
            'imap_use_ssl': data.get('imap_use_ssl', True),
            'imap_folder': data.get('imap_folder', 'INBOX'),
            'enable_email_to_ticket': data.get('enable_email_to_ticket', False),
            'default_priority': data.get('default_priority', 'media'),
            'subject_prefix': data.get('subject_prefix'),
            'ticket_number_regex': data.get('ticket_number_regex'),
            'auto_assign_to': data.get('auto_assign_to'),
            'default_client_id': data.get('default_client_id'),
            'default_category_id': data.get('default_category_id'),
            'is_active': data.get('is_active', True),
            'is_default': False  # New configs are not default by default
        }

        # Insert configuration
        result = current_app.db_manager.execute_insert(
            'email_configurations',
            config_data,
            returning='config_id'
        )

        if result:
            # Get the created configuration
            created_config = current_app.db_manager.execute_query(
                "SELECT * FROM email_configurations WHERE config_id = %s",
                (result['config_id'],),
                fetch='one'
            )
            return current_app.response_manager.created(created_config)
        else:
            return current_app.response_manager.server_error('Failed to create email configuration')

    except Exception as e:
        current_app.logger.error(f"Error creating email configuration: {e}")
        return current_app.response_manager.server_error('Failed to create email configuration')

@email_bp.route('/configurations/<config_id>', methods=['PUT'])
@jwt_required()
@require_role(['superadmin', 'admin'])
def update_email_configuration(config_id):
    """Update email configuration"""
    try:
        data = request.get_json()
        current_app.logger.info(f"🔧 UPDATING EMAIL CONFIG {config_id}")
        current_app.logger.info(f"🔧 RECEIVED DATA: {data}")
        current_app.logger.info(f"🔧 SSL VALUE: {data.get('smtp_use_ssl')} (type: {type(data.get('smtp_use_ssl'))})")
        current_app.logger.info(f"🔧 TLS VALUE: {data.get('smtp_use_tls')} (type: {type(data.get('smtp_use_tls'))})")

        if not data:
            return current_app.response_manager.bad_request('No data provided')

        # Check if configuration exists
        existing_config = current_app.db_manager.execute_query(
            "SELECT config_id FROM email_configurations WHERE config_id = %s",
            (config_id,),
            fetch='one'
        )

        if not existing_config:
            return current_app.response_manager.not_found('Email configuration not found')

        # Prepare update data
        update_data = {}

        # Basic fields (only include fields that exist in the database)
        valid_fields = ['name', 'description', 'smtp_host', 'smtp_port', 'smtp_username',
                       'smtp_use_tls', 'smtp_use_ssl', 'imap_host', 'imap_port', 'imap_username',
                       'imap_use_ssl', 'imap_folder', 'enable_email_to_ticket', 'default_priority',
                       'subject_prefix', 'ticket_number_regex', 'is_active']

        for field in valid_fields:
            if field in data:
                update_data[field] = data[field]

        # Handle password updates (only if provided)
        if data.get('smtp_password'):
            from utils.security import SecurityUtils
            update_data['smtp_password_encrypted'] = SecurityUtils.encrypt_password(data['smtp_password'])

        if data.get('imap_password'):
            from utils.security import SecurityUtils
            update_data['imap_password_encrypted'] = SecurityUtils.encrypt_password(data['imap_password'])

        # Add updated timestamp (use datetime object, not string)
        from datetime import datetime
        update_data['updated_at'] = datetime.now()

        # Update configuration
        current_app.logger.info(f"🔧 UPDATE_DATA TO SAVE: {update_data}")
        current_app.db_manager.execute_update(
            'email_configurations',
            update_data,
            'config_id = %s',
            (config_id,)
        )

        # Get updated configuration
        updated_config = current_app.db_manager.execute_query(
            "SELECT * FROM email_configurations WHERE config_id = %s",
            (config_id,),
            fetch='one'
        )

        current_app.logger.info(f"🔧 FINAL SAVED CONFIG: {updated_config}")
        return current_app.response_manager.success(updated_config)

    except Exception as e:
        current_app.logger.error(f"Error updating email configuration {config_id}: {e}")
        import traceback
        current_app.logger.error(f"Full traceback: {traceback.format_exc()}")
        return current_app.response_manager.server_error(f'Failed to update email configuration: {str(e)}')

@email_bp.route('/configurations/<config_id>', methods=['DELETE'])
@jwt_required()
@require_role(['superadmin', 'admin'])
def delete_email_configuration(config_id):
    """Delete email configuration"""
    try:
        # Check if configuration exists
        existing_config = current_app.db_manager.execute_query(
            "SELECT config_id, is_default FROM email_configurations WHERE config_id = %s",
            (config_id,),
            fetch='one'
        )

        if not existing_config:
            return current_app.response_manager.not_found('Email configuration not found')

        # Prevent deletion of default configuration
        if existing_config['is_default']:
            return current_app.response_manager.bad_request('Cannot delete default email configuration')

        # Delete configuration
        current_app.db_manager.execute_query(
            "DELETE FROM email_configurations WHERE config_id = %s",
            (config_id,),
            fetch='none'
        )

        return current_app.response_manager.success(None, 'Email configuration deleted successfully')

    except Exception as e:
        current_app.logger.error(f"Error deleting email configuration {config_id}: {e}")
        return current_app.response_manager.server_error('Failed to delete email configuration')

@email_bp.route('/configurations/<config_id>/test', methods=['POST'])
@jwt_required()
@require_role(['superadmin', 'admin'])
def test_email_configuration(config_id):
    """Test email configuration connection"""
    try:
        current_app.logger.info(f"🔧 BACKEND: Testing email configuration: {config_id}")

        config = email_service.get_config_by_id(config_id)
        current_app.logger.info(f"🔧 BACKEND: Config found: {config is not None}")

        if not config:
            current_app.logger.error(f"🔧 BACKEND: Email configuration not found for ID: {config_id}")
            return current_app.response_manager.not_found('Email configuration not found')

        current_app.logger.info(f"🔧 BACKEND: Config data keys: {list(config.keys()) if config else 'None'}")
        current_app.logger.info(f"🔧 BACKEND: SMTP password encrypted: {config.get('smtp_password_encrypted') is not None}")
        current_app.logger.info(f"🔧 BACKEND: IMAP password encrypted: {config.get('imap_password_encrypted') is not None}")

        # Check if passwords are encrypted
        if not config.get('smtp_password_encrypted'):
            return current_app.response_manager.bad_request('SMTP password not configured')

        # Test SMTP connection
        smtp_success = email_service.connect_smtp(config)
        current_app.logger.info(f"SMTP test result: {smtp_success}")

        # Test IMAP connection if enabled
        imap_success = True
        if config['enable_email_to_ticket'] and config['imap_host']:
            if not config.get('imap_password_encrypted'):
                return current_app.response_manager.bad_request('IMAP password not configured')
            imap_success = email_service.connect_imap(config)
            current_app.logger.info(f"IMAP test result: {imap_success}")

        overall_success = smtp_success and imap_success

        result = {
            'success': overall_success,
            'smtp_test': smtp_success,
            'imap_test': imap_success if config['enable_email_to_ticket'] else None,
            'message': 'Connection test completed'
        }

        if not overall_success:
            result['message'] = 'Connection test failed'
            if not smtp_success:
                result['error_details'] = 'SMTP connection failed'
            elif not imap_success:
                result['error_details'] = 'IMAP connection failed'

        return current_app.response_manager.success(result)

    except Exception as e:
        current_app.logger.error(f"Error testing email configuration {config_id}: {e}")
        import traceback
        current_app.logger.error(f"Full traceback: {traceback.format_exc()}")
        return current_app.response_manager.server_error(f'Failed to test email configuration: {str(e)}')


@email_bp.route('/configurations/<config_id>/send-test', methods=['POST'])
@jwt_required()
@require_role(['superadmin', 'admin'])
def send_test_email_endpoint(config_id):
    """Send a test email using the specified configuration"""
    try:
        data = request.get_json()
        to_email = data.get('to_email')

        if not to_email:
            return current_app.response_manager.bad_request('Email address is required')

        # Validate email format
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, to_email):
            return current_app.response_manager.bad_request('Invalid email format')

        config = email_service.get_config_by_id(config_id)
        if not config:
            return current_app.response_manager.not_found('Email configuration not found')

        current_app.logger.info(f"Sending test email to {to_email} using config {config_id}")

        # Send test email
        success, error_message = email_service.send_test_email(config, to_email)

        if success:
            result = {
                'success': True,
                'message': f'Email de prueba enviado exitosamente a {to_email}',
                'to_email': to_email
            }
        else:
            result = {
                'success': False,
                'message': 'Error enviando email de prueba',
                'error_details': error_message,
                'to_email': to_email
            }

        return current_app.response_manager.success(result)

    except Exception as e:
        current_app.logger.error(f"Error sending test email {config_id}: {e}")
        import traceback
        current_app.logger.error(f"Full traceback: {traceback.format_exc()}")
        return current_app.response_manager.server_error(f'Failed to send test email: {str(e)}')

@email_bp.route('/configurations/<config_id>/set-default', methods=['POST'])
@jwt_required()
@require_role(['superadmin', 'admin'])
def set_default_email_configuration(config_id):
    """Set email configuration as default"""
    try:
        # Check if configuration exists
        config = current_app.db_manager.execute_query(
            "SELECT config_id FROM email_configurations WHERE config_id = %s AND is_active = true",
            (config_id,),
            fetch='one'
        )

        if not config:
            return current_app.response_manager.not_found('Email configuration not found or inactive')

        # Remove default from all configurations
        current_app.db_manager.execute_query(
            "UPDATE email_configurations SET is_default = false",
            fetch='none'
        )

        # Set new default
        current_app.db_manager.execute_query(
            "UPDATE email_configurations SET is_default = true WHERE config_id = %s",
            (config_id,),
            fetch='none'
        )

        return current_app.response_manager.success(None, 'Default email configuration updated')

    except Exception as e:
        current_app.logger.error(f"Error setting default email configuration {config_id}: {e}")
        return current_app.response_manager.server_error('Failed to set default email configuration')

@email_bp.route('/templates/<template_id>', methods=['GET'])
@jwt_required()
@require_role(['superadmin', 'admin'])
def get_email_template(template_id):
    """Get specific email template"""
    try:
        query = """
        SELECT template_id, name, description, template_type, subject_template,
               body_template, is_html, available_variables, is_active, is_default,
               created_at, updated_at
        FROM email_templates
        WHERE template_id = %s
        """

        template = current_app.db_manager.execute_query(query, (template_id,), fetch='one')

        if not template:
            return current_app.response_manager.not_found('Email template not found')

        return current_app.response_manager.success(template)

    except Exception as e:
        current_app.logger.error(f"Error getting email template {template_id}: {e}")
        return current_app.response_manager.server_error('Failed to get email template')

@email_bp.route('/templates', methods=['POST'])
@jwt_required()
@require_role(['superadmin', 'admin'])
def create_email_template():
    """Create new email template"""
    try:
        data = request.get_json()
        if not data:
            return current_app.response_manager.bad_request('No data provided')

        # Validate required fields
        required_fields = ['name', 'template_type', 'subject_template', 'body_template']
        for field in required_fields:
            if not data.get(field):
                return current_app.response_manager.bad_request(f'{field} is required')

        # Get available variables for template type
        template_variables = {
            'ticket_created': ['{{ticket_number}}', '{{client_name}}', '{{site_name}}', '{{subject}}', '{{description}}', '{{priority}}', '{{affected_person}}', '{{created_date}}'],
            'ticket_assigned': ['{{ticket_number}}', '{{client_name}}', '{{technician_name}}', '{{subject}}', '{{priority}}', '{{assigned_date}}'],
            'ticket_updated': ['{{ticket_number}}', '{{client_name}}', '{{subject}}', '{{status}}', '{{updated_by}}', '{{update_date}}'],
            'ticket_resolved': ['{{ticket_number}}', '{{client_name}}', '{{subject}}', '{{resolution}}', '{{resolved_by}}', '{{resolved_date}}'],
            'ticket_closed': ['{{ticket_number}}', '{{client_name}}', '{{subject}}', '{{closed_by}}', '{{closed_date}}'],
            'sla_breach': ['{{ticket_number}}', '{{client_name}}', '{{subject}}', '{{priority}}', '{{breach_type}}', '{{time_elapsed}}'],
            'auto_response': ['{{sender_name}}', '{{ticket_number}}', '{{subject}}', '{{original_subject}}', '{{client_name}}']
        }

        # Prepare template data
        template_data = {
            'name': data['name'],
            'description': data.get('description'),
            'template_type': data['template_type'],
            'subject_template': data['subject_template'],
            'body_template': data['body_template'],
            'is_html': data.get('is_html', True),
            'available_variables': template_variables.get(data['template_type'], []),
            'is_active': data.get('is_active', True),
            'is_default': data.get('is_default', False)
        }

        # If setting as default, remove default from others of same type
        if template_data['is_default']:
            current_app.db_manager.execute_query(
                "UPDATE email_templates SET is_default = false WHERE template_type = %s",
                (template_data['template_type'],),
                fetch='none'
            )

        # Insert template
        result = current_app.db_manager.execute_insert(
            'email_templates',
            template_data,
            returning='template_id'
        )

        if result:
            # Get the created template
            created_template = current_app.db_manager.execute_query(
                "SELECT * FROM email_templates WHERE template_id = %s",
                (result['template_id'],),
                fetch='one'
            )
            return current_app.response_manager.created(created_template)
        else:
            return current_app.response_manager.server_error('Failed to create email template')

    except Exception as e:
        current_app.logger.error(f"Error creating email template: {e}")
        return current_app.response_manager.server_error('Failed to create email template')

@email_bp.route('/templates/<template_id>', methods=['PUT'])
@jwt_required()
@require_role(['superadmin', 'admin'])
def update_email_template(template_id):
    """Update email template"""
    try:
        data = request.get_json()
        if not data:
            return current_app.response_manager.bad_request('No data provided')

        # Check if template exists
        existing_template = current_app.db_manager.execute_query(
            "SELECT template_id, template_type FROM email_templates WHERE template_id = %s",
            (template_id,),
            fetch='one'
        )

        if not existing_template:
            return current_app.response_manager.not_found('Email template not found')

        # Prepare update data
        update_data = {}

        # Basic fields
        for field in ['name', 'description', 'template_type', 'subject_template',
                     'body_template', 'is_html', 'is_active', 'is_default']:
            if field in data:
                update_data[field] = data[field]

        # Update available variables if template type changed
        if 'template_type' in data:
            template_variables = {
                'ticket_created': ['{{ticket_number}}', '{{client_name}}', '{{site_name}}', '{{subject}}', '{{description}}', '{{priority}}', '{{affected_person}}', '{{created_date}}'],
                'ticket_assigned': ['{{ticket_number}}', '{{client_name}}', '{{technician_name}}', '{{subject}}', '{{priority}}', '{{assigned_date}}'],
                'ticket_updated': ['{{ticket_number}}', '{{client_name}}', '{{subject}}', '{{status}}', '{{updated_by}}', '{{update_date}}'],
                'ticket_resolved': ['{{ticket_number}}', '{{client_name}}', '{{subject}}', '{{resolution}}', '{{resolved_by}}', '{{resolved_date}}'],
                'ticket_closed': ['{{ticket_number}}', '{{client_name}}', '{{subject}}', '{{closed_by}}', '{{closed_date}}'],
                'sla_breach': ['{{ticket_number}}', '{{client_name}}', '{{subject}}', '{{priority}}', '{{breach_type}}', '{{time_elapsed}}'],
                'auto_response': ['{{sender_name}}', '{{ticket_number}}', '{{subject}}', '{{original_subject}}', '{{client_name}}']
            }
            update_data['available_variables'] = template_variables.get(data['template_type'], [])

        # If setting as default, remove default from others of same type
        if data.get('is_default'):
            template_type = data.get('template_type', existing_template['template_type'])
            current_app.db_manager.execute_query(
                "UPDATE email_templates SET is_default = false WHERE template_type = %s AND template_id != %s",
                (template_type, template_id),
                fetch='none'
            )

        # Add updated timestamp
        update_data['updated_at'] = 'CURRENT_TIMESTAMP'

        # Update template
        current_app.db_manager.execute_update(
            'email_templates',
            update_data,
            'template_id = %s',
            (template_id,)
        )

        # Get updated template
        updated_template = current_app.db_manager.execute_query(
            "SELECT * FROM email_templates WHERE template_id = %s",
            (template_id,),
            fetch='one'
        )

        return current_app.response_manager.success(updated_template)

    except Exception as e:
        current_app.logger.error(f"Error updating email template {template_id}: {e}")
        return current_app.response_manager.server_error('Failed to update email template')

@email_bp.route('/templates/<template_id>', methods=['DELETE'])
@jwt_required()
@require_role(['superadmin', 'admin'])
def delete_email_template(template_id):
    """Delete email template"""
    try:
        # Check if template exists
        existing_template = current_app.db_manager.execute_query(
            "SELECT template_id, is_default FROM email_templates WHERE template_id = %s",
            (template_id,),
            fetch='one'
        )

        if not existing_template:
            return current_app.response_manager.not_found('Email template not found')

        # Prevent deletion of default template (optional - you may want to allow this)
        if existing_template['is_default']:
            return current_app.response_manager.bad_request('Cannot delete default email template. Set another template as default first.')

        # Delete template
        current_app.db_manager.execute_query(
            "DELETE FROM email_templates WHERE template_id = %s",
            (template_id,),
            fetch='none'
        )

        return current_app.response_manager.success(None, 'Email template deleted successfully')

    except Exception as e:
        current_app.logger.error(f"Error deleting email template {template_id}: {e}")
        return current_app.response_manager.server_error('Failed to delete email template')

@email_bp.route('/templates/<template_id>/preview', methods=['POST'])
@jwt_required()
@require_role(['superadmin', 'admin'])
def preview_email_template(template_id):
    """Preview email template with sample variables"""
    try:
        data = request.get_json()
        variables = data.get('variables', {}) if data else {}

        # Get template
        template = current_app.db_manager.execute_query(
            "SELECT subject_template, body_template FROM email_templates WHERE template_id = %s",
            (template_id,),
            fetch='one'
        )

        if not template:
            return current_app.response_manager.not_found('Email template not found')

        # Replace variables in subject and body
        subject = template['subject_template']
        body = template['body_template']

        for variable, value in variables.items():
            placeholder = f"{{{{{variable}}}}}"
            subject = subject.replace(placeholder, str(value))
            body = body.replace(placeholder, str(value))

        return current_app.response_manager.success({
            'subject': subject,
            'body': body
        })

    except Exception as e:
        current_app.logger.error(f"Error previewing email template {template_id}: {e}")
        return current_app.response_manager.server_error('Failed to preview email template')

# Removed duplicate send-test endpoint - using /configurations/<config_id>/send-test instead

@email_bp.route('/queue', methods=['GET'])
@jwt_required()
@require_role(['superadmin', 'admin'])
def get_email_queue():
    """Get email queue with filters and pagination"""
    try:
        # Get query parameters
        status = request.args.get('status')
        priority = request.args.get('priority')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))

        # Build query conditions
        conditions = []
        params = []

        if status:
            conditions.append("status = %s")
            params.append(status)

        if priority:
            conditions.append("priority = %s")
            params.append(int(priority))

        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

        # Get total count
        count_query = f"SELECT COUNT(*) as total FROM email_queue {where_clause}"
        total_result = current_app.db_manager.execute_query(count_query, params, fetch='one')
        total = total_result['total'] if total_result else 0

        # Get paginated results
        offset = (page - 1) * per_page
        queue_query = f"""
        SELECT queue_id, config_id, to_email, cc_emails, bcc_emails, subject,
               ticket_id, user_id, status, priority, attempts, max_attempts,
               next_attempt_at, error_message, created_at, sent_at
        FROM email_queue
        {where_clause}
        ORDER BY priority ASC, created_at DESC
        LIMIT %s OFFSET %s
        """

        queue_items = current_app.db_manager.execute_query(
            queue_query,
            params + [per_page, offset]
        )

        return current_app.response_manager.success({
            'items': queue_items or [],
            'total': total,
            'page': page,
            'per_page': per_page
        })

    except Exception as e:
        current_app.logger.error(f"Error getting email queue: {e}")
        return current_app.response_manager.server_error('Failed to get email queue')

@email_bp.route('/queue/<queue_id>/retry', methods=['POST'])
@jwt_required()
@require_role(['superadmin', 'admin'])
def retry_email_queue(queue_id):
    """Retry failed email"""
    try:
        # Check if queue item exists and can be retried
        queue_item = current_app.db_manager.execute_query(
            "SELECT queue_id, status, attempts, max_attempts FROM email_queue WHERE queue_id = %s",
            (queue_id,),
            fetch='one'
        )

        if not queue_item:
            return current_app.response_manager.not_found('Email queue item not found')

        if queue_item['status'] not in ['failed', 'cancelled']:
            return current_app.response_manager.bad_request('Email cannot be retried')

        if queue_item['attempts'] >= queue_item['max_attempts']:
            return current_app.response_manager.bad_request('Maximum retry attempts reached')

        # Reset email for retry
        current_app.db_manager.execute_update(
            'email_queue',
            {
                'status': 'pending',
                'error_message': None,
                'next_attempt_at': 'CURRENT_TIMESTAMP'
            },
            'queue_id = %s',
            (queue_id,)
        )

        return current_app.response_manager.success(None, 'Email queued for retry')

    except Exception as e:
        current_app.logger.error(f"Error retrying email {queue_id}: {e}")
        return current_app.response_manager.server_error('Failed to retry email')

@email_bp.route('/queue/<queue_id>/cancel', methods=['POST'])
@jwt_required()
@require_role(['superadmin', 'admin'])
def cancel_email_queue(queue_id):
    """Cancel pending email"""
    try:
        # Check if queue item exists and can be cancelled
        queue_item = current_app.db_manager.execute_query(
            "SELECT queue_id, status FROM email_queue WHERE queue_id = %s",
            (queue_id,),
            fetch='one'
        )

        if not queue_item:
            return current_app.response_manager.not_found('Email queue item not found')

        if queue_item['status'] not in ['pending', 'failed']:
            return current_app.response_manager.bad_request('Email cannot be cancelled')

        # Cancel email
        current_app.db_manager.execute_update(
            'email_queue',
            {'status': 'cancelled'},
            'queue_id = %s',
            (queue_id,)
        )

        return current_app.response_manager.success(None, 'Email cancelled')

    except Exception as e:
        current_app.logger.error(f"Error cancelling email {queue_id}: {e}")
        return current_app.response_manager.server_error('Failed to cancel email')

@email_bp.route('/queue/process', methods=['POST'])
@jwt_required()
@require_role(['superadmin', 'admin'])
def process_email_queue():
    """Process pending emails in queue"""
    try:
        # Get pending emails
        pending_emails = current_app.db_manager.execute_query(
            """
            SELECT queue_id FROM email_queue
            WHERE status = 'pending'
            AND (next_attempt_at IS NULL OR next_attempt_at <= CURRENT_TIMESTAMP)
            ORDER BY priority ASC, created_at ASC
            LIMIT 50
            """
        )

        processed_count = 0

        for email_item in (pending_emails or []):
            try:
                # Process individual email
                success = email_service.process_queue_item(email_item['queue_id'])
                if success:
                    processed_count += 1
            except Exception as e:
                current_app.logger.error(f"Error processing queue item {email_item['queue_id']}: {e}")
                continue

        return current_app.response_manager.success({
            'processed': processed_count,
            'message': f'Processed {processed_count} emails from queue'
        })

    except Exception as e:
        current_app.logger.error(f"Error processing email queue: {e}")
        return current_app.response_manager.server_error('Failed to process email queue')

@email_bp.route('/logs', methods=['GET'])
@jwt_required()
@require_role(['superadmin', 'admin'])
def get_email_processing_logs():
    """Get email processing logs with filters and pagination"""
    try:
        # Get query parameters
        status = request.args.get('status')
        from_email = request.args.get('from_email')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))

        # Build query conditions
        conditions = []
        params = []

        if status:
            conditions.append("processing_status = %s")
            params.append(status)

        if from_email:
            conditions.append("from_email ILIKE %s")
            params.append(f"%{from_email}%")

        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

        # Get total count
        count_query = f"SELECT COUNT(*) as total FROM email_processing_log {where_clause}"
        total_result = current_app.db_manager.execute_query(count_query, params, fetch='one')
        total = total_result['total'] if total_result else 0

        # Get paginated results
        offset = (page - 1) * per_page
        logs_query = f"""
        SELECT log_id, config_id, message_id, from_email, to_email, subject,
               processing_status, ticket_id, action_taken, error_message,
               processed_at, created_at
        FROM email_processing_log
        {where_clause}
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
        """

        logs = current_app.db_manager.execute_query(
            logs_query,
            params + [per_page, offset]
        )

        return current_app.response_manager.success({
            'logs': logs or [],
            'total': total,
            'page': page,
            'per_page': per_page
        })

    except Exception as e:
        current_app.logger.error(f"Error getting email processing logs: {e}")
        return current_app.response_manager.server_error('Failed to get email processing logs')

@email_bp.route('/statistics', methods=['GET'])
@jwt_required()
@require_role(['superadmin', 'admin'])
def get_email_statistics():
    """Get email system statistics"""
    try:
        # Get queue statistics
        queue_stats = current_app.db_manager.execute_query(
            """
            SELECT
                COUNT(CASE WHEN status = 'sent' THEN 1 END) as total_sent,
                COUNT(CASE WHEN status = 'failed' THEN 1 END) as total_failed,
                COUNT(CASE WHEN status = 'pending' THEN 1 END) as total_pending,
                COUNT(CASE WHEN status = 'sending' THEN 1 END) as total_sending
            FROM email_queue
            """,
            fetch='one'
        )

        # Get today's processed emails
        today_stats = current_app.db_manager.execute_query(
            """
            SELECT COUNT(*) as total_processed_today
            FROM email_processing_log
            WHERE DATE(created_at) = CURRENT_DATE
            """,
            fetch='one'
        )

        # Calculate success rate
        total_sent = queue_stats['total_sent'] if queue_stats else 0
        total_failed = queue_stats['total_failed'] if queue_stats else 0
        total_processed = total_sent + total_failed
        success_rate = (total_sent / total_processed * 100) if total_processed > 0 else 0

        statistics = {
            'total_sent': total_sent,
            'total_failed': total_failed,
            'total_pending': queue_stats['total_pending'] if queue_stats else 0,
            'total_processed_today': today_stats['total_processed_today'] if today_stats else 0,
            'success_rate': round(success_rate, 2)
        }

        return current_app.response_manager.success(statistics)

    except Exception as e:
        current_app.logger.error(f"Error getting email statistics: {e}")
        return current_app.response_manager.server_error('Failed to get email statistics')


@email_bp.route('/configurations/<config_id>/check-emails', methods=['POST'])
@jwt_required()
def check_emails(config_id):
    """Check for new emails and create tickets"""
    try:
        current_app.logger.info(f"🔧 BACKEND: Checking emails for config: {config_id}")

        config = email_service.get_config_by_id(config_id)
        if not config:
            return current_app.response_manager.not_found('Email configuration not found')

        if not config.get('enable_email_to_ticket'):
            return current_app.response_manager.bad_request('Email-to-ticket is not enabled for this configuration')

        # Check IMAP connection first
        try:
            imap_result = email_service.connect_imap(config)
            current_app.logger.info(f"🔧 BACKEND: IMAP connection result: {imap_result}")
        except Exception as e:
            current_app.logger.error(f"🔧 BACKEND: IMAP connection failed: {e}")
            return current_app.response_manager.server_error(f'IMAP connection failed: {str(e)}')

        # Check for new emails and create tickets
        try:
            result = email_service.check_and_process_emails(config)
            current_app.logger.info(f"🔧 BACKEND: Email processing result: {result}")

            return current_app.response_manager.success(
                'Email check completed successfully',
                {
                    'success': True,
                    'emails_found': result.get('emails_found', 0),
                    'tickets_created': result.get('tickets_created', 0),
                    'message': f"Found {result.get('emails_found', 0)} emails, created {result.get('tickets_created', 0)} tickets"
                }
            )
        except Exception as e:
            current_app.logger.error(f"🔧 BACKEND: Email processing failed: {e}")
            return current_app.response_manager.server_error(f'Email processing failed: {str(e)}')

    except Exception as e:
        current_app.logger.error(f"Error checking emails: {e}")
        return current_app.response_manager.server_error(f'Error checking emails: {str(e)}')
