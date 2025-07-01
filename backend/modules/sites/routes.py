#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - Sites Routes
Complete CRUD API endpoints for site management
"""

from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from utils.security import require_role
from .service import SitesService
import logging
import uuid
from datetime import datetime

sites_bp = Blueprint('sites', __name__)
logger = logging.getLogger(__name__)

@sites_bp.route('', methods=['GET'])
@sites_bp.route('/', methods=['GET'])
@jwt_required()
def get_sites():
    """Get all sites (superadmin/admin) or client-specific sites (client_admin)"""
    try:
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        user_role = claims.get('role')
        user_client_id = claims.get('client_id')
        
        # Get query parameters
        client_id = request.args.get('client_id')
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 50)), 100)
        
        sites_service = SitesService(current_app.db_manager)
        
        if user_role in ['superadmin', 'admin', 'technician']:
            # Can access all sites or filter by client_id
            if client_id:
                result = sites_service.get_sites_by_client(client_id, user_role, user_client_id)
            else:
                # Get all sites across all clients
                query = """
                SELECT s.site_id, s.client_id, s.name, s.address, s.city, s.state, 
                       s.country, s.postal_code, s.is_active, s.created_at,
                       c.name as client_name,
                       COUNT(DISTINCT usa.user_id) as assigned_users,
                       COUNT(DISTINCT t.ticket_id) as total_tickets
                FROM sites s
                JOIN clients c ON s.client_id = c.client_id
                LEFT JOIN user_site_assignments usa ON s.site_id = usa.site_id
                LEFT JOIN tickets t ON s.site_id = t.site_id
                WHERE s.is_active = true
                GROUP BY s.site_id, s.client_id, s.name, s.address, s.city, s.state,
                         s.country, s.postal_code, s.is_active, s.created_at, c.name
                ORDER BY c.name, s.name
                LIMIT %s OFFSET %s
                """
                
                offset = (page - 1) * per_page
                sites = current_app.db_manager.execute_query(query, (per_page, offset))
                
                # Get total count
                count_query = "SELECT COUNT(*) as total FROM sites WHERE is_active = true"
                total_result = current_app.db_manager.execute_query(count_query, fetch='one')
                total = total_result['total'] if total_result else 0
                
                result = {
                    'success': True,
                    'sites': sites,
                    'total': total,
                    'page': page,
                    'per_page': per_page,
                    'pages': (total + per_page - 1) // per_page
                }
                
        elif user_role == 'client_admin':
            # Can only access their own client's sites
            if not user_client_id:
                return current_app.response_manager.error('Client ID not found in token', 400)

            result = sites_service.get_sites_by_client(user_client_id, user_role, user_client_id)

        elif user_role == 'solicitante':
            # Can only access their assigned sites
            query = """
            SELECT s.site_id, s.client_id, s.name, s.address, s.city, s.state,
                   s.country, s.postal_code, s.is_active, s.created_at,
                   c.name as client_name,
                   COUNT(DISTINCT usa.user_id) as assigned_users,
                   COUNT(DISTINCT t.ticket_id) as total_tickets
            FROM sites s
            JOIN clients c ON s.client_id = c.client_id
            LEFT JOIN user_site_assignments usa ON s.site_id = usa.site_id
            LEFT JOIN tickets t ON s.site_id = t.site_id
            INNER JOIN user_site_assignments usa2 ON s.site_id = usa2.site_id
            WHERE s.is_active = true AND usa2.user_id = %s
            GROUP BY s.site_id, s.client_id, s.name, s.address, s.city, s.state,
                     s.country, s.postal_code, s.is_active, s.created_at, c.name
            ORDER BY s.name
            """

            sites = current_app.db_manager.execute_query(query, (current_user_id,))

            result = {
                'success': True,
                'sites': sites or [],
                'total': len(sites or []),
                'page': 1,
                'per_page': len(sites or []),
                'pages': 1
            }

        else:
            return current_app.response_manager.error('Insufficient permissions', 403)
        
        if result['success']:
            return current_app.response_manager.success(result)
        else:
            return current_app.response_manager.error(result['error'], 400)
            
    except Exception as e:
        logger.error(f"Get sites error: {e}")
        return current_app.response_manager.server_error('Failed to retrieve sites')

@sites_bp.route('/<site_id>', methods=['GET'])
@jwt_required()
def get_site(site_id):
    """Get a specific site by ID"""
    try:
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        user_role = claims.get('role')
        user_client_id = claims.get('client_id')
        
        sites_service = SitesService(current_app.db_manager)
        result = sites_service.get_site_by_id(site_id, user_role, user_client_id)
        
        if result['success']:
            return current_app.response_manager.success(result)
        else:
            status_code = 404 if result['error'] == 'Site not found' else 403
            return current_app.response_manager.error(result['error'], status_code)
            
    except Exception as e:
        logger.error(f"Get site error: {e}")
        return current_app.response_manager.server_error('Failed to retrieve site')

@sites_bp.route('', methods=['POST'])
@sites_bp.route('/', methods=['POST'])
@jwt_required()
@require_role(['superadmin', 'admin'])
def create_site():
    """Create a new site"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return current_app.response_manager.bad_request('No data provided')
        
        sites_service = SitesService(current_app.db_manager)
        result = sites_service.create_site(data, current_user_id)
        
        if result['success']:
            return current_app.response_manager.success(result, 'Site created successfully', 201)
        else:
            return current_app.response_manager.error('Failed to create site', 400, details=result.get('errors'))
            
    except Exception as e:
        logger.error(f"Create site error: {e}")
        return current_app.response_manager.server_error('Failed to create site')

@sites_bp.route('/<site_id>', methods=['PUT'])
@jwt_required()
@require_role(['superadmin', 'admin'])
def update_site(site_id):
    """Update an existing site"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return current_app.response_manager.bad_request('No data provided')
        
        sites_service = SitesService(current_app.db_manager)
        result = sites_service.update_site(site_id, data, current_user_id)
        
        if result['success']:
            return current_app.response_manager.success(result, 'Site updated successfully')
        else:
            status_code = 404 if result['error'] == 'Site not found' else 400
            return current_app.response_manager.error(result['error'], status_code, details=result.get('errors'))
            
    except Exception as e:
        logger.error(f"Update site error: {e}")
        return current_app.response_manager.server_error('Failed to update site')

@sites_bp.route('/<site_id>', methods=['DELETE'])
@jwt_required()
@require_role(['superadmin', 'admin'])
def delete_site(site_id):
    """Delete a site (soft delete)"""
    try:
        current_user_id = get_jwt_identity()
        
        sites_service = SitesService(current_app.db_manager)
        result = sites_service.delete_site(site_id, current_user_id)
        
        if result['success']:
            return current_app.response_manager.success(result, result['message'])
        else:
            status_code = 404 if result['error'] == 'Site not found' else 400
            return current_app.response_manager.error(result['error'], status_code)
            
    except Exception as e:
        logger.error(f"Delete site error: {e}")
        return current_app.response_manager.server_error('Failed to delete site')

@sites_bp.route('/<site_id>/users', methods=['GET'])
@jwt_required()
def get_site_users(site_id):
    """Get all users assigned to a specific site"""
    try:
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        user_role = claims.get('role')
        user_client_id = claims.get('client_id')
        
        # First verify access to the site
        sites_service = SitesService(current_app.db_manager)
        site_result = sites_service.get_site_by_id(site_id, user_role, user_client_id)
        
        if not site_result['success']:
            status_code = 404 if site_result['error'] == 'Site not found' else 403
            return current_app.response_manager.error(site_result['error'], status_code)
        
        # Get assigned users
        query = """
        SELECT u.user_id, u.name, u.email, u.role, u.phone, u.is_active,
               usa.created_at as assigned_at, usa.assigned_by,
               assigner.name as assigned_by_name
        FROM users u
        JOIN user_site_assignments usa ON u.user_id = usa.user_id
        LEFT JOIN users assigner ON usa.assigned_by = assigner.user_id
        WHERE usa.site_id = %s AND u.is_active = true
        ORDER BY u.role, u.name
        """
        
        users = current_app.db_manager.execute_query(query, (site_id,))
        
        return current_app.response_manager.success({
            'site': site_result['site'],
            'users': users,
            'total_users': len(users)
        })
        
    except Exception as e:
        logger.error(f"Get site users error: {e}")
        return current_app.response_manager.server_error('Failed to retrieve site users')

@sites_bp.route('/<site_id>/assign-user', methods=['POST'])
@jwt_required()
@require_role(['superadmin', 'admin'])
def assign_user_to_site(site_id):
    """Assign a user to a site"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'user_id' not in data:
            return current_app.response_manager.bad_request('User ID is required')
        
        user_id = data['user_id']
        
        # Verify site exists
        site = current_app.db_manager.execute_query(
            "SELECT site_id, client_id FROM sites WHERE site_id = %s AND is_active = true",
            (site_id,),
            fetch='one'
        )
        if not site:
            return current_app.response_manager.error('Site not found', 404)
        
        # Verify user exists and belongs to the same client
        user = current_app.db_manager.execute_query(
            "SELECT user_id, client_id, role FROM users WHERE user_id = %s AND is_active = true",
            (user_id,),
            fetch='one'
        )
        if not user:
            return current_app.response_manager.error('User not found', 404)
        
        # Check if user belongs to the same client (for client users)
        if user['role'] in ['client_admin', 'solicitante'] and user['client_id'] != site['client_id']:
            return current_app.response_manager.error('User does not belong to the same client as the site', 400)
        
        # Check if assignment already exists
        existing = current_app.db_manager.execute_query(
            "SELECT assignment_id FROM user_site_assignments WHERE user_id = %s AND site_id = %s",
            (user_id, site_id),
            fetch='one'
        )
        if existing:
            return current_app.response_manager.error('User is already assigned to this site', 400)
        
        # Create assignment
        assignment_data = {
            'assignment_id': str(uuid.uuid4()),
            'user_id': user_id,
            'site_id': site_id,
            'assigned_by': current_user_id,
            'created_at': datetime.utcnow()
        }
        
        result = current_app.db_manager.execute_insert('user_site_assignments', assignment_data)
        
        if result:
            logger.info(f"User {user_id} assigned to site {site_id} by {current_user_id}")
            return current_app.response_manager.success({
                'assignment_id': assignment_data['assignment_id'],
                'message': 'User assigned to site successfully'
            }, 'User assigned successfully', 201)
        else:
            return current_app.response_manager.server_error('Failed to assign user to site')
            
    except Exception as e:
        logger.error(f"Assign user to site error: {e}")
        return current_app.response_manager.server_error('Failed to assign user to site')

@sites_bp.route('/<site_id>/unassign-user/<user_id>', methods=['DELETE'])
@jwt_required()
@require_role(['superadmin', 'admin'])
def unassign_user_from_site(site_id, user_id):
    """Remove a user assignment from a site"""
    try:
        current_user_id = get_jwt_identity()
        
        # Check if assignment exists
        assignment = current_app.db_manager.execute_query(
            "SELECT assignment_id FROM user_site_assignments WHERE user_id = %s AND site_id = %s",
            (user_id, site_id),
            fetch='one'
        )
        if not assignment:
            return current_app.response_manager.error('Assignment not found', 404)
        
        # Remove assignment
        result = current_app.db_manager.execute_query(
            "DELETE FROM user_site_assignments WHERE user_id = %s AND site_id = %s",
            (user_id, site_id)
        )
        
        if result is not None:
            logger.info(f"User {user_id} unassigned from site {site_id} by {current_user_id}")
            return current_app.response_manager.success({
                'message': 'User unassigned from site successfully'
            })
        else:
            return current_app.response_manager.server_error('Failed to unassign user from site')
            
    except Exception as e:
        logger.error(f"Unassign user from site error: {e}")
        return current_app.response_manager.server_error('Failed to unassign user from site')
