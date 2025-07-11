#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - Dashboard Module Routes
Real-time dashboard statistics and metrics
"""

from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from utils.security import require_role
from datetime import datetime, timedelta
import logging

dashboard_bp = Blueprint('dashboard', __name__)
logger = logging.getLogger(__name__)

@dashboard_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """Get dashboard statistics based on user role"""
    try:
        # Get current user info
        claims = get_jwt()
        current_user_role = claims.get('role')
        current_user_client_id = claims.get('client_id')
        current_user_id = get_jwt_identity()
        
        # Base stats for all users
        stats = {}
        
        # Ticket statistics
        ticket_stats = _get_ticket_stats(current_user_role, current_user_client_id)
        stats.update(ticket_stats)
        
        # Admin-only statistics
        if current_user_role in ['superadmin', 'admin']:
            admin_stats = _get_admin_stats()
            stats.update(admin_stats)
        
        # Client-specific statistics
        elif current_user_role in ['client_admin', 'solicitante']:
            client_stats = _get_client_stats(current_user_client_id)
            stats.update(client_stats)
        
        return current_app.response_manager.success(stats)
        
    except Exception as e:
        logger.error(f"Dashboard stats error: {e}")
        return current_app.response_manager.server_error('Failed to get dashboard statistics')

def _get_ticket_stats(user_role: str, client_id: str = None) -> dict:
    """Get ticket statistics based on user role"""
    try:
        # Base query conditions (tickets don't have is_active column)
        where_conditions = ["1=1"]
        params = []
        
        # Apply role-based filtering
        if user_role in ['client_admin', 'solicitante'] and client_id:
            where_conditions.append("t.client_id = %s")
            params.append(client_id)
        
        where_clause = " AND ".join(where_conditions)
        
        # Get ticket counts by status
        status_query = f"""
        SELECT 
            COUNT(*) as total_tickets,
            COUNT(CASE WHEN t.status IN ('nuevo', 'asignado', 'en_proceso', 'espera_cliente', 'reabierto') THEN 1 END) as open_tickets,
            COUNT(CASE WHEN t.status = 'asignado' THEN 1 END) as assigned_tickets,
            COUNT(CASE WHEN t.status = 'resuelto' THEN 1 END) as resolved_tickets,
            COUNT(CASE WHEN t.status = 'cerrado' THEN 1 END) as closed_tickets,
            COUNT(CASE WHEN t.status = 'cancelado' THEN 1 END) as cancelled_tickets
        FROM tickets t
        WHERE {where_clause}
        """
        
        ticket_counts = current_app.db_manager.execute_query(status_query, tuple(params), fetch='one')
        
        # Get overdue tickets (simplified - tickets older than 3 days without resolution)
        overdue_query = f"""
        SELECT COUNT(*) as overdue_tickets
        FROM tickets t
        WHERE {where_clause}
        AND t.status IN ('nuevo', 'asignado', 'en_proceso', 'espera_cliente', 'reabierto')
        AND t.created_at < %s
        """
        
        three_days_ago = datetime.utcnow() - timedelta(days=3)
        overdue_params = params + [three_days_ago]
        overdue_result = current_app.db_manager.execute_query(overdue_query, tuple(overdue_params), fetch='one')
        
        # Calculate SLA compliance (simplified - percentage of tickets resolved within 3 days)
        sla_query = f"""
        SELECT 
            COUNT(*) as total_resolved,
            COUNT(CASE WHEN t.resolved_at <= t.created_at + INTERVAL '3 days' THEN 1 END) as within_sla
        FROM tickets t
        WHERE {where_clause}
        AND t.status IN ('resuelto', 'cerrado')
        AND t.resolved_at IS NOT NULL
        """
        
        sla_result = current_app.db_manager.execute_query(sla_query, tuple(params), fetch='one')
        
        # Calculate SLA compliance percentage
        sla_compliance = 0
        if sla_result and sla_result['total_resolved'] > 0:
            sla_compliance = round((sla_result['within_sla'] / sla_result['total_resolved']) * 100, 1)
        
        return {
            'total_tickets': ticket_counts['total_tickets'] or 0,
            'open_tickets': ticket_counts['open_tickets'] or 0,
            'assigned_tickets': ticket_counts['assigned_tickets'] or 0,
            'resolved_tickets': ticket_counts['resolved_tickets'] or 0,
            'closed_tickets': ticket_counts['closed_tickets'] or 0,
            'cancelled_tickets': ticket_counts['cancelled_tickets'] or 0,
            'overdue_tickets': overdue_result['overdue_tickets'] or 0,
            'sla_compliance': sla_compliance
        }
        
    except Exception as e:
        logger.error(f"Error getting ticket stats: {e}")
        return {
            'total_tickets': 0,
            'open_tickets': 0,
            'assigned_tickets': 0,
            'resolved_tickets': 0,
            'closed_tickets': 0,
            'cancelled_tickets': 0,
            'overdue_tickets': 0,
            'sla_compliance': 0
        }

def _get_admin_stats() -> dict:
    """Get admin-specific statistics"""
    try:
        # Get client count
        client_query = "SELECT COUNT(*) as total_clients FROM clients WHERE is_active = true"
        client_result = current_app.db_manager.execute_query(client_query, fetch='one')
        
        # Get user count
        user_query = "SELECT COUNT(*) as total_users FROM users WHERE is_active = true"
        user_result = current_app.db_manager.execute_query(user_query, fetch='one')
        
        # Get site count
        site_query = "SELECT COUNT(*) as total_sites FROM sites WHERE is_active = true"
        site_result = current_app.db_manager.execute_query(site_query, fetch='one')
        
        return {
            'total_clients': client_result['total_clients'] if client_result else 0,
            'total_users': user_result['total_users'] if user_result else 0,
            'total_sites': site_result['total_sites'] if site_result else 0
        }
        
    except Exception as e:
        logger.error(f"Error getting admin stats: {e}")
        return {
            'total_clients': 0,
            'total_users': 0,
            'total_sites': 0
        }

def _get_client_stats(client_id: str) -> dict:
    """Get client-specific statistics"""
    try:
        # Get user count for this client
        user_query = "SELECT COUNT(*) as client_users FROM users WHERE client_id = %s AND is_active = true"
        user_result = current_app.db_manager.execute_query(user_query, (client_id,), fetch='one')
        
        # Get site count for this client
        site_query = "SELECT COUNT(*) as client_sites FROM sites WHERE client_id = %s AND is_active = true"
        site_result = current_app.db_manager.execute_query(site_query, (client_id,), fetch='one')
        
        return {
            'client_users': user_result['client_users'] if user_result else 0,
            'client_sites': site_result['client_sites'] if site_result else 0
        }
        
    except Exception as e:
        logger.error(f"Error getting client stats: {e}")
        return {
            'client_users': 0,
            'client_sites': 0
        }

@dashboard_bp.route('/recent-activity', methods=['GET'])
@jwt_required()
def get_recent_activity():
    """Get recent activity feed"""
    try:
        # Get current user info
        claims = get_jwt()
        current_user_role = claims.get('role')
        current_user_client_id = claims.get('client_id')
        
        # Get recent tickets (tickets don't have is_active column)
        where_conditions = ["1=1"]
        params = []
        
        # Apply role-based filtering
        if current_user_role in ['client_admin', 'solicitante'] and current_user_client_id:
            where_conditions.append("t.client_id = %s")
            params.append(current_user_client_id)
        
        where_clause = " AND ".join(where_conditions)
        
        # Get recent ticket activity
        activity_query = f"""
        SELECT 
            t.ticket_id,
            t.ticket_number,
            t.subject,
            t.status,
            t.priority,
            t.created_at,
            t.updated_at,
            c.name as client_name,
            creator.name as created_by_name
        FROM tickets t
        LEFT JOIN clients c ON t.client_id = c.client_id
        LEFT JOIN users creator ON t.created_by = creator.user_id
        WHERE {where_clause}
        ORDER BY t.updated_at DESC
        LIMIT 10
        """
        
        activities = current_app.db_manager.execute_query(activity_query, tuple(params))
        
        # Format activities
        formatted_activities = []
        for activity in (activities or []):
            formatted_activities.append({
                'id': activity['ticket_id'],
                'type': 'ticket',
                'action': _get_activity_action(activity['status']),
                'ticket_number': activity['ticket_number'],
                'subject': activity['subject'],
                'client_name': activity['client_name'],
                'created_by': activity['created_by_name'],
                'timestamp': activity['updated_at'].isoformat() if activity['updated_at'] else None,
                'priority': activity['priority']
            })
        
        return current_app.response_manager.success(formatted_activities)
        
    except Exception as e:
        logger.error(f"Recent activity error: {e}")
        return current_app.response_manager.server_error('Failed to get recent activity')

@dashboard_bp.route('/charts', methods=['GET'])
@jwt_required()
def get_dashboard_charts():
    """Get chart data for dashboard visualizations"""
    try:
        # Get current user info
        claims = get_jwt()
        current_user_role = claims.get('role')
        current_user_client_id = claims.get('client_id')

        charts_data = {}

        # Tickets by status chart
        charts_data['tickets_by_status'] = _get_tickets_by_status_chart(current_user_role, current_user_client_id)

        # Tickets trend chart (last 30 days)
        charts_data['tickets_trend'] = _get_tickets_trend_chart(current_user_role, current_user_client_id)

        # SLA compliance chart
        charts_data['sla_compliance'] = _get_sla_compliance_chart(current_user_role, current_user_client_id)

        # Priority distribution chart
        charts_data['priority_distribution'] = _get_priority_distribution_chart(current_user_role, current_user_client_id)

        # Technician performance chart (admin only)
        if current_user_role in ['superadmin', 'admin', 'technician']:
            charts_data['technician_performance'] = _get_technician_performance_chart()

        return current_app.response_manager.success(charts_data)

    except Exception as e:
        logger.error(f"Dashboard charts error: {e}")
        return current_app.response_manager.server_error('Failed to get dashboard charts')

def _get_activity_action(status: str) -> str:
    """Get activity action description based on status"""
    actions = {
        'nuevo': 'creado',
        'asignado': 'asignado',
        'en_proceso': 'en proceso',
        'espera_cliente': 'esperando cliente',
        'resuelto': 'resuelto',
        'cerrado': 'cerrado',
        'cancelado': 'cancelado',
        'reabierto': 'reabierto'
    }
    return actions.get(status, status)

def _get_tickets_by_status_chart(user_role: str, client_id: str = None) -> list:
    """Get tickets by status data for pie chart"""
    try:
        # Base query conditions
        where_conditions = ["1=1"]
        params = []

        # Apply role-based filtering
        if user_role in ['client_admin', 'solicitante'] and client_id:
            where_conditions.append("t.client_id = %s")
            params.append(client_id)

        where_clause = " AND ".join(where_conditions)

        query = f"""
        SELECT
            t.status,
            COUNT(*) as count
        FROM tickets t
        WHERE {where_clause}
        GROUP BY t.status
        ORDER BY count DESC
        """

        results = current_app.db_manager.execute_query(query, tuple(params))

        # Format for chart
        chart_data = []
        status_labels = {
            'nuevo': 'Nuevo',
            'asignado': 'Asignado',
            'en_proceso': 'En Proceso',
            'espera_cliente': 'Espera Cliente',
            'resuelto': 'Resuelto',
            'cerrado': 'Cerrado',
            'cancelado': 'Cancelado',
            'reabierto': 'Reabierto'
        }

        for result in (results or []):
            chart_data.append({
                'name': status_labels.get(result['status'], result['status']),
                'value': result['count'],
                'status': result['status']
            })

        return chart_data

    except Exception as e:
        logger.error(f"Error getting tickets by status chart: {e}")
        return []

def _get_tickets_trend_chart(user_role: str, client_id: str = None) -> list:
    """Get tickets trend data for line chart (last 30 days)"""
    try:
        # Base query conditions
        where_conditions = ["t.created_at >= CURRENT_DATE - INTERVAL '30 days'"]
        params = []

        # Apply role-based filtering
        if user_role in ['client_admin', 'solicitante'] and client_id:
            where_conditions.append("t.client_id = %s")
            params.append(client_id)

        where_clause = " AND ".join(where_conditions)

        query = f"""
        SELECT
            DATE(t.created_at) as date,
            COUNT(*) as tickets_created,
            COUNT(CASE WHEN t.status IN ('resuelto', 'cerrado') THEN 1 END) as tickets_resolved
        FROM tickets t
        WHERE {where_clause}
        GROUP BY DATE(t.created_at)
        ORDER BY date ASC
        """

        results = current_app.db_manager.execute_query(query, tuple(params))

        # Format for chart
        chart_data = []
        for result in (results or []):
            chart_data.append({
                'date': result['date'].strftime('%d/%m') if result['date'] else '',
                'creados': result['tickets_created'],
                'resueltos': result['tickets_resolved']
            })

        return chart_data

    except Exception as e:
        logger.error(f"Error getting tickets trend chart: {e}")
        return []

def _get_sla_compliance_chart(user_role: str, client_id: str = None) -> dict:
    """Get SLA compliance data for gauge chart"""
    try:
        # Base query conditions
        where_conditions = ["1=1"]
        params = []

        # Apply role-based filtering
        if user_role in ['client_admin', 'solicitante'] and client_id:
            where_conditions.append("t.client_id = %s")
            params.append(client_id)

        where_clause = " AND ".join(where_conditions)

        query = f"""
        SELECT
            COUNT(*) as total_tickets,
            COUNT(CASE WHEN st.response_breach = false OR st.response_breach IS NULL THEN 1 END) as response_compliant,
            COUNT(CASE WHEN st.resolution_breach = false OR st.resolution_breach IS NULL THEN 1 END) as resolution_compliant
        FROM tickets t
        LEFT JOIN sla_tracking st ON t.ticket_id = st.ticket_id
        WHERE {where_clause}
        AND t.status IN ('resuelto', 'cerrado')
        """

        result = current_app.db_manager.execute_query(query, tuple(params), fetch='one')

        if result and result['total_tickets'] > 0:
            total = result['total_tickets']
            response_compliance = round((result['response_compliant'] / total) * 100, 1)
            resolution_compliance = round((result['resolution_compliant'] / total) * 100, 1)
            overall_compliance = round((response_compliance + resolution_compliance) / 2, 1)
        else:
            response_compliance = 0
            resolution_compliance = 0
            overall_compliance = 0

        return {
            'overall': overall_compliance,
            'response': response_compliance,
            'resolution': resolution_compliance,
            'total_tickets': result['total_tickets'] if result else 0
        }

    except Exception as e:
        logger.error(f"Error getting SLA compliance chart: {e}")
        return {'overall': 0, 'response': 0, 'resolution': 0, 'total_tickets': 0}

def _get_priority_distribution_chart(user_role: str, client_id: str = None) -> list:
    """Get priority distribution data for bar chart"""
    try:
        # Base query conditions
        where_conditions = ["1=1"]
        params = []

        # Apply role-based filtering
        if user_role in ['client_admin', 'solicitante'] and client_id:
            where_conditions.append("t.client_id = %s")
            params.append(client_id)

        where_clause = " AND ".join(where_conditions)

        query = f"""
        SELECT
            t.priority,
            COUNT(*) as count,
            COUNT(CASE WHEN t.status IN ('nuevo', 'asignado', 'en_proceso', 'espera_cliente', 'reabierto') THEN 1 END) as open_count,
            COUNT(CASE WHEN t.status IN ('resuelto', 'cerrado') THEN 1 END) as closed_count
        FROM tickets t
        WHERE {where_clause}
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

        # Format for chart
        chart_data = []
        priority_labels = {
            'alta': 'Alta',
            'media': 'Media',
            'baja': 'Baja'
        }

        for result in (results or []):
            chart_data.append({
                'priority': priority_labels.get(result['priority'], result['priority']),
                'total': result['count'],
                'abiertos': result['open_count'],
                'cerrados': result['closed_count']
            })

        return chart_data

    except Exception as e:
        logger.error(f"Error getting priority distribution chart: {e}")
        return []

def _get_technician_performance_chart() -> list:
    """Get technician performance data for bar chart"""
    try:
        query = """
        SELECT
            u.first_name,
            u.last_name,
            COUNT(t.ticket_id) as assigned_tickets,
            COUNT(CASE WHEN t.status = 'resuelto' THEN 1 END) as resolved_tickets,
            AVG(EXTRACT(EPOCH FROM (COALESCE(t.resolved_at, CURRENT_TIMESTAMP) - t.created_at))/3600) as avg_resolution_hours
        FROM users u
        LEFT JOIN tickets t ON u.user_id = t.assigned_to
            AND t.created_at >= CURRENT_DATE - INTERVAL '30 days'
        WHERE u.role = 'technician' AND u.is_active = true
        GROUP BY u.user_id, u.first_name, u.last_name
        HAVING COUNT(t.ticket_id) > 0
        ORDER BY resolved_tickets DESC
        LIMIT 10
        """

        results = current_app.db_manager.execute_query(query)

        # Format for chart
        chart_data = []
        for result in (results or []):
            chart_data.append({
                'name': f"{result['first_name']} {result['last_name']}",
                'asignados': result['assigned_tickets'],
                'resueltos': result['resolved_tickets'],
                'tiempo_promedio': round(result['avg_resolution_hours'] or 0, 1)
            })

        return chart_data

    except Exception as e:
        logger.error(f"Error getting technician performance chart: {e}")
        return []
