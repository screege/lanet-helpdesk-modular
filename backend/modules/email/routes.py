#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - Email Module Routes
Email management endpoints
"""

from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required
from utils.security import require_role

email_bp = Blueprint('email', __name__)

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

@email_bp.route('/config', methods=['GET'])
@jwt_required()
@require_role(['superadmin', 'admin'])
def get_email_config():
    """Get email configuration"""
    try:
        config = current_app.db_manager.execute_query(
            "SELECT config_key, config_value FROM system_config WHERE config_key LIKE 'smtp_%' OR config_key LIKE 'imap_%'"
        )
        
        return current_app.response_manager.success(config)
        
    except Exception as e:
        current_app.logger.error(f"Get email config error: {e}")
        return current_app.response_manager.server_error('Failed to get email configuration')
