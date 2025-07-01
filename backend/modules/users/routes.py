#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - Users Module Routes
Complete CRUD API endpoints for user management
"""

from flask import Blueprint, request, current_app, g
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from utils.security import require_role
# from utils.validators import ValidationUtils  # Not implemented yet
from datetime import datetime
import uuid
import logging
from .service import UserService

users_bp = Blueprint('users', __name__)
logger = logging.getLogger(__name__)

@users_bp.route('', methods=['GET'])
@users_bp.route('/', methods=['GET'])
@jwt_required()
@require_role(['superadmin', 'admin', 'technician'])
def get_users():
    """Get all users with pagination and search"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        search = request.args.get('search', '').strip()

        # Build search condition
        search_condition = ""
        search_params = []

        if search:
            search_condition = """
            WHERE (u.name ILIKE %s OR u.email ILIKE %s)
            AND u.is_active = true
            """
            search_term = f"%{search}%"
            search_params = [search_term, search_term]
        else:
            search_condition = "WHERE u.is_active = true"

        # Get total count
        count_query = f"SELECT COUNT(*) as total FROM users u {search_condition}"
        total_result = current_app.db_manager.execute_query(count_query, tuple(search_params), fetch='one')
        total = total_result['total'] if total_result else 0

        # Calculate offset
        offset = (page - 1) * per_page

        # Get users with pagination
        query = f"""
        SELECT u.user_id, u.client_id, u.name, u.email, u.role, u.phone, u.is_active,
               u.last_login, u.created_at, u.updated_at,
               c.name as client_name
        FROM users u
        LEFT JOIN clients c ON u.client_id = c.client_id
        {search_condition}
        ORDER BY u.name
        LIMIT %s OFFSET %s
        """

        params = search_params + [per_page, offset]
        users = current_app.db_manager.execute_query(query, tuple(params))

        # Format response
        result = {
            'users': [current_app.response_manager.format_user_data(user) for user in (users or [])],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': (total + per_page - 1) // per_page,
                'has_next': page * per_page < total,
                'has_prev': page > 1
            }
        }

        return current_app.response_manager.success(result)

    except Exception as e:
        logger.error(f"Get users error: {e}")
        return current_app.response_manager.server_error('Failed to get users')

@users_bp.route('/<user_id>', methods=['GET'])
@jwt_required()
@require_role(['superadmin', 'admin', 'technician'])
def get_user(user_id):
    """Get specific user by ID"""
    try:
        # Validate UUID
        if not current_app.db_manager.validate_uuid(user_id):
            return current_app.response_manager.bad_request('Invalid user ID format')

        query = """
        SELECT u.user_id, u.client_id, u.name, u.email, u.role, u.phone,
               u.is_active, u.last_login, u.created_at, u.updated_at,
               c.name as client_name
        FROM users u
        LEFT JOIN clients c ON u.client_id = c.client_id
        WHERE u.user_id = %s
        """

        user = current_app.db_manager.execute_query(query, (user_id,), fetch='one')

        if not user:
            return current_app.response_manager.not_found('User')

        formatted_user = current_app.response_manager.format_user_data(user)
        return current_app.response_manager.success(formatted_user)

    except Exception as e:
        logger.error(f"Get user error: {e}")
        return current_app.response_manager.server_error('Failed to get user')

@users_bp.route('', methods=['POST'])
@users_bp.route('/', methods=['POST'])
@jwt_required()
@require_role(['superadmin'])
def create_user():
    """Create a new user"""
    try:
        data = request.get_json()

        if not data:
            return current_app.response_manager.bad_request('No data provided')

        # Validate required fields
        required_fields = ['name', 'email', 'password', 'role']
        for field in required_fields:
            if field not in data or not data[field]:
                return current_app.response_manager.bad_request(f'{field} is required')

        # Validate email format
        import re
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_pattern, data['email']):
            return current_app.response_manager.bad_request('Invalid email format')

        # Validate role
        valid_roles = ['superadmin', 'admin', 'technician', 'client_admin', 'solicitante']
        if data['role'] not in valid_roles:
            return current_app.response_manager.bad_request('Invalid role')

        # Check if email already exists
        existing_user = current_app.db_manager.execute_query(
            "SELECT user_id FROM users WHERE email = %s",
            (data['email'].lower().strip(),),
            fetch='one'
        )
        if existing_user:
            return current_app.response_manager.bad_request('Email already exists')

        # Validate client_id if provided
        if data.get('client_id'):
            if not current_app.db_manager.validate_uuid(data['client_id']):
                return current_app.response_manager.bad_request('Invalid client ID format')

            client = current_app.db_manager.execute_query(
                "SELECT client_id FROM clients WHERE client_id = %s AND is_active = true",
                (data['client_id'],),
                fetch='one'
            )
            if not client:
                return current_app.response_manager.bad_request('Invalid client ID')

        # Hash password
        import bcrypt
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), salt).decode('utf-8')

        # Prepare user data
        user_data = {
            'user_id': str(uuid.uuid4()),
            'client_id': data.get('client_id'),
            'name': data['name'].strip(),
            'email': data['email'].lower().strip(),
            'password_hash': password_hash,
            'role': data['role'],
            'phone': data.get('phone', '').strip() if data.get('phone') else None,
            'is_active': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

        # Insert user
        result = current_app.db_manager.execute_insert(
            'users',
            user_data,
            returning='user_id, name, email, role, created_at'
        )

        if result:
            logger.info(f"User created successfully: {result['email']}")
            formatted_user = current_app.response_manager.format_user_data(result)
            return current_app.response_manager.success(formatted_user, "User created successfully", 201)
        else:
            return current_app.response_manager.server_error('Failed to create user')

    except Exception as e:
        logger.error(f"Create user error: {e}")
        return current_app.response_manager.server_error('Failed to create user')

@users_bp.route('/<user_id>', methods=['PUT'])
@jwt_required()
@require_role(['superadmin'])
def update_user(user_id):
    """Update an existing user"""
    try:
        # Validate UUID
        if not current_app.db_manager.validate_uuid(user_id):
            return current_app.response_manager.bad_request('Invalid user ID format')

        data = request.get_json()
        if not data:
            return current_app.response_manager.bad_request('No data provided')

        # Check if user exists
        existing_user = current_app.db_manager.execute_query(
            "SELECT user_id, email FROM users WHERE user_id = %s",
            (user_id,),
            fetch='one'
        )
        if not existing_user:
            return current_app.response_manager.not_found('User')

        # Validate email if being changed
        if 'email' in data and data['email'] != existing_user['email']:
            import re
            email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
            if not re.match(email_pattern, data['email']):
                return current_app.response_manager.bad_request('Invalid email format')

            email_check = current_app.db_manager.execute_query(
                "SELECT user_id FROM users WHERE email = %s AND user_id != %s",
                (data['email'].lower().strip(), user_id),
                fetch='one'
            )
            if email_check:
                return current_app.response_manager.bad_request('Email already exists')

        # Validate role if provided (4 roles only as per blueprint)
        if 'role' in data:
            valid_roles = ['superadmin', 'technician', 'client_admin', 'solicitante']
            if data['role'] not in valid_roles:
                return current_app.response_manager.bad_request('Invalid role')

        # Validate client_id if provided
        if 'client_id' in data and data['client_id']:
            if not current_app.db_manager.validate_uuid(data['client_id']):
                return current_app.response_manager.bad_request('Invalid client ID format')

            client = current_app.db_manager.execute_query(
                "SELECT client_id FROM clients WHERE client_id = %s AND is_active = true",
                (data['client_id'],),
                fetch='one'
            )
            if not client:
                return current_app.response_manager.bad_request('Invalid client ID')

        # Prepare update data
        update_data = {'updated_at': datetime.utcnow()}

        # Add updatable fields
        updatable_fields = ['name', 'email', 'role', 'phone', 'client_id', 'is_active']
        for field in updatable_fields:
            if field in data:
                if field == 'email':
                    update_data[field] = data[field].lower().strip()
                elif field == 'name':
                    update_data[field] = data[field].strip()
                elif field == 'phone':
                    update_data[field] = data[field].strip() if data[field] else None
                else:
                    update_data[field] = data[field]

        # Handle password update
        if 'password' in data and data['password']:
            password_hash = current_app.auth_manager.hash_password(data['password'])
            update_data['password_hash'] = password_hash

        # Update user
        rows_updated = current_app.db_manager.execute_update(
            'users',
            update_data,
            'user_id = %s',
            (user_id,)
        )

        if rows_updated > 0:
            # Get updated user
            updated_user = current_app.db_manager.execute_query(
                """
                SELECT u.user_id, u.client_id, u.name, u.email, u.role, u.phone,
                       u.is_active, u.last_login, u.created_at, u.updated_at,
                       c.name as client_name
                FROM users u
                LEFT JOIN clients c ON u.client_id = c.client_id
                WHERE u.user_id = %s
                """,
                (user_id,),
                fetch='one'
            )

            logger.info(f"User updated successfully: {updated_user['email']}")
            formatted_user = current_app.response_manager.format_user_data(updated_user)
            return current_app.response_manager.success(formatted_user, "User updated successfully")
        else:
            return current_app.response_manager.server_error('Failed to update user')

    except Exception as e:
        logger.error(f"Update user error: {e}")
        return current_app.response_manager.server_error('Failed to update user')

@users_bp.route('/<user_id>', methods=['DELETE'])
@jwt_required()
@require_role(['superadmin'])
def delete_user(user_id):
    """Delete a user (soft delete)"""
    try:
        # Validate UUID
        if not current_app.db_manager.validate_uuid(user_id):
            return current_app.response_manager.bad_request('Invalid user ID format')

        # Check if user exists
        existing_user = current_app.db_manager.execute_query(
            "SELECT user_id, email FROM users WHERE user_id = %s",
            (user_id,),
            fetch='one'
        )
        if not existing_user:
            return current_app.response_manager.not_found('User')

        # Prevent self-deletion
        current_user_id = get_jwt_identity()
        if user_id == current_user_id:
            return current_app.response_manager.bad_request('Cannot delete your own account')

        # Soft delete (set is_active = false)
        rows_updated = current_app.db_manager.execute_update(
            'users',
            {
                'is_active': False,
                'updated_at': datetime.utcnow()
            },
            'user_id = %s',
            (user_id,)
        )

        if rows_updated > 0:
            logger.info(f"User deleted successfully: {existing_user['email']}")
            return current_app.response_manager.success(None, "User deleted successfully")
        else:
            return current_app.response_manager.server_error('Failed to delete user')

    except Exception as e:
        logger.error(f"Delete user error: {e}")
        return current_app.response_manager.server_error('Failed to delete user')

@users_bp.route('/client/<client_id>', methods=['GET'])
@jwt_required()
@require_role(['superadmin', 'admin', 'technician', 'client_admin'])
def get_users_by_client(client_id):
    """Get all users for a specific client"""
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
        SELECT user_id, name, email, role, phone, is_active,
               last_login, created_at
        FROM users
        WHERE client_id = %s AND is_active = true
        ORDER BY name
        """

        users = current_app.db_manager.execute_query(query, (client_id,))
        formatted_users = [current_app.response_manager.format_user_data(user) for user in (users or [])]

        return current_app.response_manager.success(formatted_users)

    except Exception as e:
        logger.error(f"Get users by client error: {e}")
        return current_app.response_manager.server_error('Failed to retrieve users')

@users_bp.route('/roles', methods=['GET'])
@jwt_required()
@require_role(['superadmin'])
def get_user_roles():
    """Get available user roles"""
    try:
        # Only 4 roles as per blueprint
        roles = [
            {'value': 'superadmin', 'label': 'Super Administrador', 'description': 'Acceso completo al sistema'},
            {'value': 'technician', 'label': 'Técnico', 'description': 'Gestión de tickets y soporte técnico'},
            {'value': 'client_admin', 'label': 'Administrador de Cliente', 'description': 'Gestión de su organización'},
            {'value': 'solicitante', 'label': 'Solicitante', 'description': 'Creación y seguimiento de tickets'}
        ]

        return current_app.response_manager.success(roles)

    except Exception as e:
        logger.error(f"Get user roles error: {e}")
        return current_app.response_manager.server_error('Failed to get user roles')

@users_bp.route('/stats', methods=['GET'])
@jwt_required()
@require_role(['superadmin'])
def get_user_stats():
    """Get user statistics"""
    try:
        stats_query = """
        SELECT
            COUNT(*) as total_users,
            COUNT(CASE WHEN is_active = true THEN 1 END) as active_users,
            COUNT(CASE WHEN role = 'admin' THEN 1 END) as admin_users,
            COUNT(CASE WHEN role = 'technician' THEN 1 END) as technician_users,
            COUNT(CASE WHEN role = 'client_admin' THEN 1 END) as client_admin_users,
            COUNT(CASE WHEN role = 'solicitante' THEN 1 END) as solicitante_users,
            COUNT(CASE WHEN last_login >= NOW() - INTERVAL '30 days' THEN 1 END) as active_last_30_days
        FROM users
        """

        stats = current_app.db_manager.execute_query(stats_query, fetch='one')

        return current_app.response_manager.success(stats)

    except Exception as e:
        logger.error(f"Get user stats error: {e}")
        return current_app.response_manager.server_error('Failed to get user statistics')

@users_bp.route('/solicitante-test', methods=['POST'])
@jwt_required()
def test_solicitante():
    """Test endpoint for solicitante creation"""
    logger.info("Test solicitante endpoint called!")
    return current_app.response_manager.success({'test': 'working'}, 'Test endpoint working')

@users_bp.route('/solicitante', methods=['POST'])
@jwt_required()
def create_solicitante():
    """Create a new solicitante user"""
    try:
        logger.info("=== SOLICITANTE ENDPOINT CALLED ===")

        current_user_id = get_jwt_identity()
        logger.info(f"Current user ID: {current_user_id}")

        data = request.get_json()
        logger.info(f"Request data: {data}")

        if not data:
            logger.error("No data provided in request")
            return current_app.response_manager.bad_request('No data provided')

        # Extract site IDs
        site_ids = data.pop('site_ids', [])
        logger.info(f"Extracted site_ids: {site_ids}")

        # Import UserService here to avoid import issues
        from .service import UserService
        logger.info("UserService imported successfully")

        user_service = UserService(current_app.db_manager, current_app.auth_manager)
        logger.info("UserService instantiated successfully")

        result = user_service.create_solicitante(data, site_ids, current_user_id)
        logger.info(f"Service result: {result}")

        if result['success']:
            return current_app.response_manager.success(result, 'Solicitante created successfully', 201)
        else:
            return current_app.response_manager.error('Failed to create solicitante', 400, details=result.get('errors'))

    except Exception as e:
        logger.error(f"Create solicitante error: {e}", exc_info=True)
        return current_app.response_manager.server_error('Failed to create solicitante')

@users_bp.route('/<user_id>/assign-sites', methods=['POST'])
@jwt_required()
@require_role(['superadmin'])
def assign_user_to_sites(user_id):
    """Assign an existing user to sites"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        if not data or 'site_ids' not in data:
            return current_app.response_manager.bad_request('Site IDs are required')

        site_ids = data['site_ids']

        from .service import UserService
        user_service = UserService(current_app.db_manager, current_app.auth_manager)
        result = user_service.assign_user_to_sites(user_id, site_ids, current_user_id)

        if result['success']:
            return current_app.response_manager.success(result, 'User assigned to sites successfully')
        else:
            return current_app.response_manager.error('Failed to assign user to sites', 400, details=result.get('errors'))

    except Exception as e:
        logger.error(f"Assign user to sites error: {e}")
        return current_app.response_manager.server_error('Failed to assign user to sites')

@users_bp.route('/<user_id>/unassign-sites', methods=['POST'])
@jwt_required()
@require_role(['superadmin'])
def unassign_user_from_sites(user_id):
    """Unassign a user from sites"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        if not data or 'site_ids' not in data:
            return current_app.response_manager.bad_request('Site IDs are required')

        site_ids = data['site_ids']

        from .service import UserService
        user_service = UserService(current_app.db_manager, current_app.auth_manager)
        result = user_service.unassign_user_from_sites(user_id, site_ids, current_user_id)

        if result['success']:
            return current_app.response_manager.success(result, 'User unassigned from sites successfully')
        else:
            return current_app.response_manager.error('Failed to unassign user from sites', 400, details=result.get('errors'))

    except Exception as e:
        logger.error(f"Unassign user from sites error: {e}")
        return current_app.response_manager.server_error('Failed to unassign user from sites')

@users_bp.route('/by-client/<client_id>', methods=['GET'])
@jwt_required()
def get_client_users(client_id):
    """Get users by client ID (for solicitante assignment)"""
    try:
        role = request.args.get('role', 'solicitante')  # Default to solicitantes

        from .service import UserService
        user_service = UserService(current_app.db_manager, current_app.auth_manager)
        result = user_service.get_users_by_client(client_id, role)

        if result['success']:
            return current_app.response_manager.success(result, 'Users retrieved successfully')
        else:
            return current_app.response_manager.error('Failed to get users', 400, details=result.get('errors'))

    except Exception as e:
        logger.error(f"Get users by client error: {e}")
        return current_app.response_manager.server_error('Failed to get users by client')

@users_bp.route('/technician', methods=['POST'])
@jwt_required()
@require_role(['superadmin', 'admin'])
def create_technician():
    """Create a new technician user"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        if not data:
            return current_app.response_manager.bad_request('No data provided')

        user_service = UserService(current_app.db_manager, current_app.auth_manager)
        result = user_service.create_technician(data, current_user_id)

        if result['success']:
            return current_app.response_manager.success(result, 'Technician created successfully', 201)
        else:
            return current_app.response_manager.error('Failed to create technician', 400, details=result.get('errors'))

    except Exception as e:
        logger.error(f"Create technician error: {e}")
        return current_app.response_manager.server_error('Failed to create technician')

@users_bp.route('/<user_id>/sites', methods=['GET'])
@jwt_required()
def get_user_sites(user_id):
    """Get sites available for user assignment"""
    try:
        # Validate UUID
        if not current_app.db_manager.validate_uuid(user_id):
            return current_app.response_manager.bad_request('Invalid user ID format')

        user_service = UserService(current_app.db_manager, current_app.auth_manager)
        result = user_service.get_available_sites_for_user(user_id)

        if result['success']:
            return current_app.response_manager.success(result)
        else:
            status_code = 404 if result['error'] == 'User not found' else 400
            return current_app.response_manager.error(result['error'], status_code)

    except Exception as e:
        logger.error(f"Get user sites error: {e}")
        return current_app.response_manager.server_error('Failed to retrieve user sites')


