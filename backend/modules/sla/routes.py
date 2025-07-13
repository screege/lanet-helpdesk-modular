#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - SLA Routes
Complete SLA management, monitoring, and escalation endpoints
"""

from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.security import require_role
from .service import sla_service
import json

sla_bp = Blueprint('sla', __name__)

@sla_bp.route('/policies', methods=['GET'])
@jwt_required()
@require_role(['superadmin', 'admin'])
def get_sla_policies():
    """Get all SLA policies"""
    try:
        query = """
        SELECT sp.policy_id, sp.name, sp.description, sp.priority,
               sp.response_time_hours, sp.resolution_time_hours,
               sp.business_hours_only, sp.business_start_hour, sp.business_end_hour,
               sp.business_days, sp.timezone, sp.escalation_enabled,
               sp.escalation_levels, sp.is_active, sp.is_default,
               sp.created_at, sp.updated_at,
               c.name as client_name, cat.name as category_name
        FROM sla_policies sp
        LEFT JOIN clients c ON sp.client_id = c.client_id
        LEFT JOIN categories cat ON sp.category_id = cat.category_id
        WHERE sp.is_active = true
        ORDER BY sp.is_default DESC, sp.name
        """

        policies = current_app.db_manager.execute_query(query)

        formatted_policies = []
        for policy in (policies or []):
            formatted_policy = current_app.response_manager.format_sla_policy_data(policy)
            formatted_policies.append(formatted_policy)

        return current_app.response_manager.success(formatted_policies)

    except Exception as e:
        current_app.logger.error(f"Get SLA policies error: {e}")
        return current_app.response_manager.server_error('Failed to get SLA policies')

@sla_bp.route('/policies', methods=['POST'])
@jwt_required()
@require_role(['superadmin', 'admin'])
def create_sla_policy():
    """Create a new SLA policy"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['name', 'priority', 'response_time_hours', 'resolution_time_hours']
        for field in required_fields:
            if field not in data:
                return current_app.response_manager.bad_request(f'Missing required field: {field}')

        # Create policy
        policy_id = sla_service.create_sla_policy(data)

        if policy_id:
            return current_app.response_manager.success({'policy_id': policy_id}, 'SLA policy created successfully')
        else:
            return current_app.response_manager.server_error('Failed to create SLA policy')

    except Exception as e:
        current_app.logger.error(f"Create SLA policy error: {e}")
        return current_app.response_manager.server_error('Failed to create SLA policy')

@sla_bp.route('/policies/<policy_id>', methods=['PUT'])
@jwt_required()
@require_role(['superadmin', 'admin'])
def update_sla_policy(policy_id):
    """Update an existing SLA policy"""
    try:
        data = request.get_json()

        # Update policy
        success = sla_service.update_sla_policy(policy_id, data)

        if success:
            return current_app.response_manager.success(None, 'SLA policy updated successfully')
        else:
            return current_app.response_manager.server_error('Failed to update SLA policy')

    except Exception as e:
        current_app.logger.error(f"Update SLA policy error: {e}")
        return current_app.response_manager.server_error('Failed to update SLA policy')

@sla_bp.route('/policies/<policy_id>', methods=['DELETE'])
@jwt_required()
@require_role(['superadmin', 'admin'])
def delete_sla_policy(policy_id):
    """Delete an SLA policy"""
    try:
        success = sla_service.delete_sla_policy(policy_id)

        if success:
            return current_app.response_manager.success(None, 'SLA policy deleted successfully')
        else:
            return current_app.response_manager.server_error('Failed to delete SLA policy')

    except Exception as e:
        current_app.logger.error(f"Delete SLA policy error: {e}")
        return current_app.response_manager.server_error('Failed to delete SLA policy')

@sla_bp.route('/policies/<policy_id>/set-default', methods=['POST'])
@jwt_required()
@require_role(['superadmin', 'admin'])
def set_default_sla_policy(policy_id):
    """Set an SLA policy as default"""
    try:
        success = sla_service.set_default_policy(policy_id)

        if success:
            return current_app.response_manager.success(None, 'Default SLA policy set successfully')
        else:
            return current_app.response_manager.server_error('Failed to set default SLA policy')

    except Exception as e:
        current_app.logger.error(f"Set default SLA policy error: {e}")
        return current_app.response_manager.server_error('Failed to set default SLA policy')

@sla_bp.route('/breaches', methods=['GET'])
@jwt_required()
@require_role(['superadmin', 'admin', 'technician'])
def get_sla_breaches():
    """Get current SLA breaches"""
    try:
        breaches = sla_service.check_sla_breaches()

        formatted_breaches = []
        for breach in breaches:
            formatted_breach = current_app.response_manager.format_sla_breach_data(breach)
            formatted_breaches.append(formatted_breach)

        return current_app.response_manager.success(formatted_breaches)

    except Exception as e:
        current_app.logger.error(f"Get SLA breaches error: {e}")
        return current_app.response_manager.server_error('Failed to get SLA breaches')

@sla_bp.route('/warnings', methods=['GET'])
@jwt_required()
@require_role(['superadmin', 'admin', 'technician'])
def get_sla_warnings():
    """Get SLA warnings (upcoming breaches)"""
    try:
        warning_hours = int(request.args.get('hours', 2))
        warnings = sla_service.check_sla_warnings(warning_hours)

        formatted_warnings = []
        for warning in warnings:
            formatted_warning = current_app.response_manager.format_sla_warning_data(warning)
            formatted_warnings.append(formatted_warning)

        return current_app.response_manager.success(formatted_warnings)

    except Exception as e:
        current_app.logger.error(f"Get SLA warnings error: {e}")
        return current_app.response_manager.server_error('Failed to get SLA warnings')

@sla_bp.route('/metrics', methods=['GET'])
@jwt_required()
@require_role(['superadmin', 'admin', 'technician'])
def get_sla_metrics():
    """Get SLA performance metrics"""
    try:
        days = int(request.args.get('days', 30))

        metrics_query = """
        SELECT
            COUNT(*) as total_tickets,
            COUNT(CASE WHEN st.response_status = 'met' THEN 1 END) as response_met,
            COUNT(CASE WHEN st.resolution_status = 'met' THEN 1 END) as resolution_met,
            COUNT(CASE WHEN st.response_status = 'breached' THEN 1 END) as response_breached,
            COUNT(CASE WHEN st.resolution_status = 'breached' THEN 1 END) as resolution_breached,
            COUNT(CASE WHEN st.escalation_level > 0 THEN 1 END) as escalated_tickets
        FROM sla_tracking st
        JOIN tickets t ON st.ticket_id = t.ticket_id
        WHERE st.created_at >= CURRENT_DATE - INTERVAL '%s days'
        """

        metrics = current_app.db_manager.execute_query(metrics_query, (days,), fetch='one')

        # Calculate percentages
        total = metrics['total_tickets'] or 1
        formatted_metrics = {
            'total_tickets': metrics['total_tickets'],
            'response_met': metrics['response_met'],
            'response_met_percentage': round((metrics['response_met'] / total) * 100, 2),
            'resolution_met': metrics['resolution_met'],
            'resolution_met_percentage': round((metrics['resolution_met'] / total) * 100, 2),
            'response_breached': metrics['response_breached'],
            'response_breach_percentage': round((metrics['response_breached'] / total) * 100, 2),
            'resolution_breached': metrics['resolution_breached'],
            'resolution_breach_percentage': round((metrics['resolution_breached'] / total) * 100, 2),
            'escalated_tickets': metrics['escalated_tickets'],
            'escalation_percentage': round((metrics['escalated_tickets'] / total) * 100, 2),
            'period_days': days
        }

        return current_app.response_manager.success(formatted_metrics)

    except Exception as e:
        current_app.logger.error(f"Get SLA metrics error: {e}")
        return current_app.response_manager.server_error('Failed to get SLA metrics')
