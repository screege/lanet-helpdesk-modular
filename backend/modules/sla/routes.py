#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - SLA Module Routes
SLA management endpoints
"""

from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required
from utils.security import require_role

sla_bp = Blueprint('sla', __name__)

@sla_bp.route('/', methods=['GET'])
@jwt_required()
@require_role(['superadmin', 'admin'])
def get_slas():
    """Get all SLA policies"""
    try:
        slas = current_app.db_manager.execute_query(
            "SELECT * FROM slas WHERE is_active = true ORDER BY name"
        )
        
        return current_app.response_manager.success(slas)
        
    except Exception as e:
        current_app.logger.error(f"Get SLAs error: {e}")
        return current_app.response_manager.server_error('Failed to get SLAs')

@sla_bp.route('/<sla_id>', methods=['GET'])
@jwt_required()
def get_sla(sla_id):
    """Get specific SLA policy"""
    try:
        sla = current_app.db_manager.execute_query(
            "SELECT * FROM slas WHERE sla_id = %s",
            (sla_id,),
            fetch='one'
        )
        
        if not sla:
            return current_app.response_manager.not_found('SLA')
        
        return current_app.response_manager.success(sla)
        
    except Exception as e:
        current_app.logger.error(f"Get SLA error: {e}")
        return current_app.response_manager.server_error('Failed to get SLA')
