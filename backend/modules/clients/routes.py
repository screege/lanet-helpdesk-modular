#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - Clients Module Routes
Client management endpoints
"""

from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from utils.security import require_role
from utils.validators import ValidationUtils
from .wizard_service import ClientWizardService
from datetime import datetime
import uuid
import logging

clients_bp = Blueprint('clients', __name__)

@clients_bp.route('', methods=['GET'])
@clients_bp.route('/', methods=['GET'])
@jwt_required()
def get_clients():
    """Get all clients with statistics"""
    try:
        # Get user info
        claims = get_jwt()
        user_id = get_jwt_identity()
        user_role = claims.get('role')
        user_client_id = claims.get('client_id')

        current_app.logger.info(f"🔍 CLIENTS ENDPOINT - Role: {user_role}, Client ID: {user_client_id}")
        current_app.logger.info(f"🔍 CLIENTS ENDPOINT - Full claims: {claims}")

        # ✅ FIX: Set RLS context for database queries
        current_app.logger.info(f"🔧 Setting RLS context - User: {user_id}, Role: {user_role}, Client: {user_client_id}")
        current_app.db_manager.set_rls_context(
            user_id=user_id,
            user_role=user_role,
            client_id=user_client_id
        )
        current_app.logger.info(f"✅ RLS context set successfully")

        # Role-based access control
        if user_role in ['client_admin', 'solicitante']:
            # Clients can only see their own client
            if not user_client_id:
                return current_app.response_manager.forbidden('No client associated with user')
            # Return only their client
            client_query = """
                SELECT client_id, name, email, phone, address, city, state, country,
                       postal_code, is_active, created_at, updated_at
                FROM clients
                WHERE client_id = %s AND is_active = true
            """
            clients = current_app.db_manager.execute_query(client_query, (user_client_id,))
            formatted_clients = []
            for client in (clients or []):
                formatted_client = current_app.response_manager.format_client_data(client)
                formatted_clients.append(formatted_client)
            return current_app.response_manager.success(formatted_clients)

        elif user_role not in ['superadmin', 'admin', 'technician']:
            return current_app.response_manager.forbidden('Insufficient permissions')

        # For superadmin/admin/technician - show all clients
        # Get search parameter
        search = request.args.get('search', '').strip()
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))

        # Build query with statistics
        base_query = """
        SELECT
            c.client_id, c.name, c.email, c.rfc, c.phone, c.address,
            c.city, c.state, c.country, c.postal_code, c.is_active, c.created_at,
            COUNT(DISTINCT s.site_id) as total_sites,
            COUNT(DISTINCT u.user_id) as total_users,
            COUNT(DISTINCT t.ticket_id) as total_tickets,
            COUNT(DISTINCT CASE WHEN t.status IN ('nuevo', 'asignado', 'en_proceso', 'espera_cliente', 'reabierto') THEN t.ticket_id END) as open_tickets
        FROM clients c
        LEFT JOIN sites s ON c.client_id = s.client_id AND s.is_active = true
        LEFT JOIN users u ON c.client_id = u.client_id AND u.is_active = true
        LEFT JOIN tickets t ON c.client_id = t.client_id
        WHERE c.is_active = true
        """

        params = []

        # Add search filter
        if search:
            base_query += " AND (c.name ILIKE %s OR c.email ILIKE %s OR c.rfc ILIKE %s)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param])

        # Add GROUP BY and ORDER BY
        base_query += " GROUP BY c.client_id, c.name, c.email, c.rfc, c.phone, c.address, c.city, c.state, c.country, c.postal_code, c.is_active, c.created_at"
        base_query += " ORDER BY c.name"

        # Execute query
        clients = current_app.db_manager.execute_query(base_query, tuple(params))

        # Format clients data
        formatted_clients = []
        for client in clients:
            formatted_client = current_app.response_manager.format_client_data(client)
            # Add statistics
            formatted_client.update({
                'total_sites': client.get('total_sites', 0),
                'total_users': client.get('total_users', 0),
                'total_tickets': client.get('total_tickets', 0),
                'open_tickets': client.get('open_tickets', 0)
            })
            formatted_clients.append(formatted_client)

        return current_app.response_manager.success(formatted_clients)

    except Exception as e:
        current_app.logger.error(f"Get clients error: {e}")
        return current_app.response_manager.server_error('Failed to get clients')

@clients_bp.route('/<client_id>', methods=['GET'])
@jwt_required()
def get_client(client_id):
    """Get specific client"""
    try:
        client = current_app.db_manager.execute_query(
            "SELECT * FROM clients WHERE client_id = %s",
            (client_id,),
            fetch='one'
        )
        
        if not client:
            return current_app.response_manager.not_found('Client')
        
        formatted_client = current_app.response_manager.format_client_data(client)
        return current_app.response_manager.success(formatted_client)
        
    except Exception as e:
        current_app.logger.error(f"Get client error: {e}")
        return current_app.response_manager.server_error('Failed to get client')

@clients_bp.route('', methods=['POST'])
@clients_bp.route('/', methods=['POST'])
@jwt_required()
@require_role(['superadmin', 'admin'])
def create_client():
    """Create a new client"""
    try:
        data = request.get_json()

        if not data:
            return current_app.response_manager.error('No data provided', 400)

        # Validate required fields
        required_fields = ['name', 'email']
        for field in required_fields:
            if field not in data or not data[field]:
                return current_app.response_manager.error(f'{field} is required', 400)

        # Validate email format
        import re
        email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
        if not re.match(email_pattern, data['email']):
            return current_app.response_manager.error('Invalid email format', 400)

        # Check if client name already exists
        existing_client = current_app.db_manager.execute_query(
            "SELECT client_id FROM clients WHERE name = %s AND is_active = true",
            (data['name'].strip(),),
            fetch='one'
        )
        if existing_client:
            return current_app.response_manager.error('Client name already exists', 400)

        # Check if email already exists (if provided)
        if data.get('email'):
            existing_email = current_app.db_manager.execute_query(
                "SELECT client_id FROM clients WHERE email = %s AND is_active = true",
                (data['email'].lower().strip(),),
                fetch='one'
            )
            if existing_email:
                return current_app.response_manager.error('Email already exists', 400)

        # Prepare client data
        client_data = {
            'client_id': str(uuid.uuid4()),
            'name': data['name'].strip(),
            'rfc': data.get('rfc', '').strip() if data.get('rfc') else None,
            'email': data.get('email', '').lower().strip() if data.get('email') else None,
            'phone': data.get('phone', '').strip() if data.get('phone') else None,
            'allowed_emails': data.get('allowed_emails', []),
            'address': data.get('address', '').strip() if data.get('address') else None,
            'city': data.get('city', '').strip() if data.get('city') else None,
            'state': data.get('state', '').strip() if data.get('state') else None,
            'country': data.get('country', 'México').strip(),
            'postal_code': data.get('postal_code', '').strip() if data.get('postal_code') else None,
            'is_active': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

        # Insert client
        result = current_app.db_manager.execute_insert(
            'clients',
            client_data,
            returning='client_id, name, email, created_at'
        )

        if result:
            current_app.logger.info(f"Client created successfully: {result['name']}")
            formatted_client = current_app.response_manager.format_client_data(result)
            return current_app.response_manager.success(formatted_client, "Client created successfully", 201)
        else:
            return current_app.response_manager.server_error('Failed to create client')

    except Exception as e:
        current_app.logger.error(f"Create client error: {e}")
        return current_app.response_manager.server_error('Failed to create client')

@clients_bp.route('/<client_id>', methods=['PUT'])
@jwt_required()
@require_role(['superadmin', 'admin'])
def update_client(client_id):
    """Update an existing client"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        if not data:
            return current_app.response_manager.bad_request('No data provided')

        # Use service layer for proper validation and error handling
        from .service import ClientService
        clients_service = ClientService(current_app.db_manager, current_app.auth_manager)
        result = clients_service.update_client(client_id, data, current_user_id)

        if result['success']:
            return current_app.response_manager.success(result['data'], 'Client updated successfully')
        else:
            return current_app.response_manager.error(
                'Failed to update client',
                400,
                details=result.get('errors')
            )

    except Exception as e:
        current_app.logger.error(f"Update client error: {e}")
        return current_app.response_manager.server_error('Failed to update client')

@clients_bp.route('/<client_id>', methods=['DELETE'])
@jwt_required()
@require_role(['superadmin', 'admin'])
def delete_client(client_id):
    """Delete a client (soft delete)"""
    try:
        # Validate UUID
        if not current_app.db_manager.validate_uuid(client_id):
            return current_app.response_manager.bad_request('Invalid client ID format')

        # Check if client exists
        existing_client = current_app.db_manager.execute_query(
            "SELECT client_id, name FROM clients WHERE client_id = %s",
            (client_id,),
            fetch='one'
        )
        if not existing_client:
            return current_app.response_manager.not_found('Client')

        # Check if client has active tickets
        active_tickets = current_app.db_manager.execute_query(
            "SELECT COUNT(*) as count FROM tickets WHERE client_id = %s AND status NOT IN ('cerrado', 'cancelado')",
            (client_id,),
            fetch='one'
        )

        if active_tickets and active_tickets['count'] > 0:
            return current_app.response_manager.bad_request('Cannot delete client with active tickets')

        # Soft delete client and related entities
        with current_app.db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                # Deactivate client
                cursor.execute(
                    "UPDATE clients SET is_active = false, updated_at = %s WHERE client_id = %s",
                    (datetime.utcnow(), client_id)
                )

                # Deactivate related sites
                cursor.execute(
                    "UPDATE sites SET is_active = false, updated_at = %s WHERE client_id = %s",
                    (datetime.utcnow(), client_id)
                )

                # Deactivate related users
                cursor.execute(
                    "UPDATE users SET is_active = false, updated_at = %s WHERE client_id = %s",
                    (datetime.utcnow(), client_id)
                )

                conn.commit()

        current_app.logger.info(f"Client deleted successfully: {existing_client['name']}")
        return current_app.response_manager.success(None, "Client deleted successfully")

    except Exception as e:
        current_app.logger.error(f"Delete client error: {e}")
        return current_app.response_manager.server_error('Failed to delete client')

@clients_bp.route('/<client_id>/sites', methods=['GET'])
@jwt_required()
@require_role(['superadmin', 'admin', 'technician', 'client_admin'])
def get_client_sites(client_id):
    """Get all sites for a specific client"""
    try:
        # Validate UUID
        if not current_app.db_manager.validate_uuid(client_id):
            return current_app.response_manager.bad_request('Invalid client ID format')

        # Check access permissions for client users
        claims = get_jwt()
        current_user_role = claims.get('role')
        current_user_client_id = claims.get('client_id')

        if current_user_role in ['client_admin', 'solicitante']:
            if current_user_client_id != client_id:
                return current_app.response_manager.forbidden('Access denied')

        query = """
        SELECT s.site_id, s.client_id, s.name, s.address, s.city, s.state,
               s.country, s.postal_code, s.latitude, s.longitude, s.authorized_emails, s.is_active,
               s.created_at, s.updated_at,
               0 as total_users,
               COUNT(DISTINCT t.ticket_id) as total_tickets
        FROM sites s
        LEFT JOIN tickets t ON s.site_id = t.site_id
        WHERE s.client_id = %s AND s.is_active = true
        GROUP BY s.site_id, s.client_id, s.name, s.address, s.city, s.state,
                 s.country, s.postal_code, s.latitude, s.longitude, s.authorized_emails, s.is_active,
                 s.created_at, s.updated_at
        ORDER BY s.name
        """

        sites = current_app.db_manager.execute_query(query, (client_id,))
        formatted_sites = [current_app.response_manager.format_site_data(site) for site in (sites or [])]

        return current_app.response_manager.success(formatted_sites)

    except Exception as e:
        current_app.logger.error(f"Get client sites error: {e}")
        return current_app.response_manager.server_error('Failed to retrieve sites')

@clients_bp.route('/<client_id>/users', methods=['GET'])
@jwt_required()
@require_role(['superadmin', 'admin', 'technician', 'client_admin'])
def get_client_users(client_id):
    """Get all users for a specific client"""
    try:
        # Verify client exists and user has access
        client = current_app.db_manager.execute_query(
            "SELECT client_id, name FROM clients WHERE client_id = %s AND is_active = true",
            (client_id,),
            fetch='one'
        )

        if not client:
            return current_app.response_manager.not_found('Client not found')

        # Get users for this client
        users = current_app.db_manager.execute_query("""
            SELECT
                u.user_id,
                u.name,
                u.email,
                u.role,
                u.phone,
                u.is_active,
                u.created_at,
                u.last_login
            FROM users u
            WHERE u.client_id = %s
            ORDER BY u.created_at DESC
        """, (client_id,), fetch='all')

        return current_app.response_manager.success(users or [])

    except Exception as e:
        current_app.logger.error(f"Get client users error: {e}")
        return current_app.response_manager.server_error('Failed to retrieve users')

@clients_bp.route('/<client_id>/stats', methods=['GET'])
@jwt_required()
@require_role(['superadmin', 'admin', 'technician', 'client_admin'])
def get_client_stats(client_id):
    """Get comprehensive statistics for a client"""
    try:
        # Validate UUID
        if not current_app.db_manager.validate_uuid(client_id):
            return current_app.response_manager.bad_request('Invalid client ID format')

        # Check access permissions for client users
        claims = get_jwt()
        current_user_role = claims.get('role')
        current_user_client_id = claims.get('client_id')

        if current_user_role in ['client_admin', 'solicitante']:
            if current_user_client_id != client_id:
                return current_app.response_manager.forbidden('Access denied')

        stats_query = """
        SELECT
            c.name as client_name,
            COUNT(DISTINCT s.site_id) as total_sites,
            COUNT(DISTINCT u.user_id) as total_users,
            COUNT(DISTINCT t.ticket_id) as total_tickets,
            COUNT(DISTINCT CASE WHEN t.status IN ('nuevo', 'asignado', 'en_proceso') THEN t.ticket_id END) as open_tickets,
            COUNT(DISTINCT CASE WHEN t.status = 'resuelto' THEN t.ticket_id END) as resolved_tickets,
            COUNT(DISTINCT CASE WHEN t.created_at >= NOW() - INTERVAL '30 days' THEN t.ticket_id END) as tickets_last_30_days
        FROM clients c
        LEFT JOIN sites s ON c.client_id = s.client_id AND s.is_active = true
        LEFT JOIN users u ON c.client_id = u.client_id AND u.is_active = true
        LEFT JOIN tickets t ON c.client_id = t.client_id
        WHERE c.client_id = %s
        GROUP BY c.client_id, c.name
        """

        stats = current_app.db_manager.execute_query(stats_query, (client_id,), fetch='one')

        if not stats:
            return current_app.response_manager.not_found('Client')

        return current_app.response_manager.success(stats)

    except Exception as e:
        current_app.logger.error(f"Get client stats error: {e}")
        return current_app.response_manager.server_error('Failed to get client statistics')

@clients_bp.route('/wizard', methods=['POST'])
@jwt_required()
@require_role(['superadmin', 'admin'])
def create_client_wizard():
    """
    MSP Client Creation Wizard
    Workflow: Cliente Padre → Admin Principal → Sitio(s) → Asignación de Solicitantes
    """
    try:
        data = request.get_json()

        if not data:
            return current_app.response_manager.bad_request('No data provided')

        # Validate wizard structure
        required_sections = ['client', 'admin_user', 'sites']
        for section in required_sections:
            if section not in data:
                return current_app.response_manager.bad_request(f'{section} data is required')

        # Validate client data
        client_data = data['client']
        required_client_fields = ['name', 'email']
        for field in required_client_fields:
            if field not in client_data or not client_data[field]:
                return current_app.response_manager.bad_request(f'Client {field} is required')

        # Validate admin user data
        admin_data = data['admin_user']
        required_admin_fields = ['name', 'email', 'password']
        for field in required_admin_fields:
            if field not in admin_data or not admin_data[field]:
                return current_app.response_manager.bad_request(f'Admin user {field} is required')

        # Validate sites data (mínimo 1)
        sites_data = data['sites']
        if not sites_data or len(sites_data) == 0:
            return current_app.response_manager.bad_request('At least one site is required')

        for i, site in enumerate(sites_data):
            required_site_fields = ['name', 'address', 'city', 'state', 'postal_code']
            for field in required_site_fields:
                if field not in site or not site[field]:
                    return current_app.response_manager.bad_request(f'Site {i+1} {field} is required')

        # Validate additional users (optional)
        if data.get('additional_users'):
            for i, user in enumerate(data['additional_users']):
                required_user_fields = ['name', 'email', 'password']
                for field in required_user_fields:
                    if field not in user or not user[field]:
                        return current_app.response_manager.bad_request(f'Additional user {i+1} {field} is required')

                # Validate site assignment (mínimo 1 sitio)
                if not user.get('site_ids') or len(user['site_ids']) == 0:
                    return current_app.response_manager.bad_request(f'Additional user {i+1} must be assigned to at least one site')

        # Get current user
        current_user_id = get_jwt_identity()

        # Execute wizard using ClientWizardService
        try:
            current_app.logger.info(f"Starting wizard execution for user: {current_user_id}")
            current_app.logger.info(f"Wizard data keys: {list(data.keys())}")

            # Initialize wizard service
            wizard_service = ClientWizardService(current_app.db_manager, current_app.auth_manager)
            result = wizard_service.create_client_complete(data, current_user_id)

            current_app.logger.info(f"Wizard result: {result}")
        except Exception as wizard_error:
            current_app.logger.error(f"Wizard execution error: {wizard_error}")
            import traceback
            current_app.logger.error(f"Wizard traceback: {traceback.format_exc()}")
            return current_app.response_manager.server_error(f'Wizard error: {str(wizard_error)}')

        if result['success']:
            current_app.logger.info(f"Client wizard completed successfully: {result.get('client_id')}")

            # Get complete client data for response
            client_query = """
            SELECT c.client_id, c.name, c.email, c.created_at,
                   COUNT(DISTINCT s.site_id) as total_sites,
                   COUNT(DISTINCT u.user_id) as total_users
            FROM clients c
            LEFT JOIN sites s ON c.client_id = s.client_id AND s.is_active = true
            LEFT JOIN users u ON c.client_id = u.client_id AND u.is_active = true
            WHERE c.client_id = %s
            GROUP BY c.client_id, c.name, c.email, c.created_at
            """

            client_info = current_app.db_manager.execute_query(
                client_query,
                (result['client_id'],),
                fetch='one'
            )

            response_data = {
                'client': current_app.response_manager.format_client_data(client_info),
                'admin_user_id': result['admin_user_id'],
                'site_ids': result['site_ids'],
                'additional_user_ids': result.get('additional_user_ids', []),
                'summary': {
                    'total_sites': len(result['site_ids']),
                    'total_users': 1 + len(result.get('additional_user_ids', [])),
                    'workflow_completed': True
                }
            }

            return current_app.response_manager.success(
                response_data,
                "MSP Client created successfully with complete workflow",
                201
            )
        else:
            return current_app.response_manager.error(
                'Failed to create client',
                400,
                details=result.get('errors')
            )

    except Exception as e:
        current_app.logger.error(f"Client wizard error: {e}")
        return current_app.response_manager.server_error('Failed to create client wizard')

def _execute_client_wizard(wizard_data: dict, created_by: str) -> dict:
    """Execute MSP client wizard using existing services"""
    try:
        import bcrypt

        # Step 1: Create Client
        client_data = wizard_data['client']

        # Check if client name already exists
        name_check = current_app.db_manager.execute_query(
            "SELECT client_id FROM clients WHERE name = %s AND is_active = true",
            (client_data['name'].strip(),),
            fetch='one'
        )
        if name_check:
            return {'success': False, 'errors': {'name': 'Client name already exists'}}

        # Check if email already exists
        email_check = current_app.db_manager.execute_query(
            "SELECT client_id FROM clients WHERE email = %s AND is_active = true",
            (client_data['email'].lower().strip(),),
            fetch='one'
        )
        if email_check:
            return {'success': False, 'errors': {'email': 'Email already exists'}}

        # Create client
        client_insert_data = {
            'client_id': str(uuid.uuid4()),
            'name': client_data['name'].strip(),
            'rfc': client_data.get('rfc', '').strip() if client_data.get('rfc') else None,
            'email': client_data['email'].lower().strip(),
            'phone': client_data.get('phone', '').strip() if client_data.get('phone') else None,
            'allowed_emails': client_data.get('allowed_emails', []),
            'address': client_data.get('address', '').strip() if client_data.get('address') else None,
            'city': client_data.get('city', '').strip() if client_data.get('city') else None,
            'state': client_data.get('state', '').strip() if client_data.get('state') else None,
            'country': client_data.get('country', 'México').strip(),
            'postal_code': client_data.get('postal_code', '').strip() if client_data.get('postal_code') else None,
            'is_active': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'created_by': created_by
        }

        client_result = current_app.db_manager.execute_insert(
            'clients',
            client_insert_data,
            returning='client_id, name'
        )

        if not client_result:
            return {'success': False, 'errors': {'general': 'Failed to create client'}}

        client_id = client_result['client_id']

        # Step 2: Create Admin User
        admin_data = wizard_data['admin_user']

        # Check if email already exists
        email_check = current_app.db_manager.execute_query(
            "SELECT user_id FROM users WHERE email = %s",
            (admin_data['email'].lower().strip(),),
            fetch='one'
        )
        if email_check:
            return {'success': False, 'errors': {'admin_email': 'Admin email already exists'}}

        # Hash password (simplified for testing)
        import hashlib
        password_hash = hashlib.sha256(admin_data['password'].encode('utf-8')).hexdigest()

        admin_insert_data = {
            'user_id': str(uuid.uuid4()),
            'client_id': client_id,
            'name': admin_data['name'].strip(),
            'email': admin_data['email'].lower().strip(),
            'password_hash': password_hash,
            'role': admin_data.get('role', 'client_admin'),
            'phone': admin_data.get('phone', '').strip() if admin_data.get('phone') else None,
            'is_active': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'created_by': created_by
        }

        admin_result = current_app.db_manager.execute_insert(
            'users',
            admin_insert_data,
            returning='user_id, name'
        )

        if not admin_result:
            return {'success': False, 'errors': {'general': 'Failed to create admin user'}}

        admin_user_id = admin_result['user_id']

        # Step 3: Create Sites
        sites_data = wizard_data['sites']
        site_ids = []

        for i, site_data in enumerate(sites_data):
            # Check if site name already exists for this client
            site_check = current_app.db_manager.execute_query(
                "SELECT site_id FROM sites WHERE client_id = %s AND name = %s AND is_active = true",
                (client_id, site_data['name'].strip()),
                fetch='one'
            )
            if site_check:
                return {'success': False, 'errors': {f'site_{i}_name': f'Site name already exists for this client'}}

            site_insert_data = {
                'site_id': str(uuid.uuid4()),
                'client_id': client_id,
                'name': site_data['name'].strip(),
                'address': site_data['address'].strip(),
                'city': site_data['city'].strip(),
                'state': site_data['state'].strip(),
                'country': site_data.get('country', 'México').strip(),
                'postal_code': site_data['postal_code'].strip(),
                'latitude': site_data.get('latitude'),
                'longitude': site_data.get('longitude'),
                'is_active': True,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'created_by': created_by
            }

            site_result = current_app.db_manager.execute_insert(
                'sites',
                site_insert_data,
                returning='site_id'
            )

            if site_result:
                site_ids.append(site_result['site_id'])

        # Step 4: Assign Admin to Sites using user_site_assignments table
        if site_ids:
            for site_id in site_ids:
                assignment_data = {
                    'assignment_id': str(uuid.uuid4()),
                    'user_id': admin_user_id,
                    'site_id': site_id,
                    'assigned_by': created_by,
                    'created_at': datetime.utcnow()
                }
                current_app.db_manager.execute_insert('user_site_assignments', assignment_data)

        return {
            'success': True,
            'client_id': client_id,
            'admin_user_id': admin_user_id,
            'site_ids': site_ids,
            'additional_user_ids': []
        }

    except Exception as e:
        current_app.logger.error(f"Error in client wizard execution: {e}")
        return {'success': False, 'errors': {'general': 'Internal server error'}}
