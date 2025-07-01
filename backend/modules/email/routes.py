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
               imap_host, imap_port, imap_username, enable_email_to_ticket,
               default_priority, subject_prefix, is_active, is_default,
               created_at, updated_at
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

@email_bp.route('/queue/process', methods=['POST'])
@jwt_required()
@require_role(['superadmin', 'admin'])
def process_email_queue():
    """Manually process email queue"""
    try:
        data = request.get_json()
        limit = data.get('limit', 10) if data else 10
        limit = min(max(limit, 1), 50)  # Between 1 and 50

        processed = email_service.process_email_queue(limit)

        return current_app.response_manager.success({
            'processed': processed,
            'message': f'Processed {processed} emails from queue'
        })

    except Exception as e:
        current_app.logger.error(f"Process email queue error: {e}")
        return current_app.response_manager.server_error('Failed to process email queue')

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
