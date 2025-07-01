#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - Users Module Service
Business logic for user management operations
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from core.database import DatabaseManager
from core.auth import AuthManager
from utils.validators import ValidationUtils
import logging

class UserService:
    """Service class for user management operations"""
    
    def __init__(self, db_manager: DatabaseManager, auth_manager: AuthManager):
        self.db = db_manager
        self.auth = auth_manager
        self.logger = logging.getLogger(__name__)
    
    def get_all_users(self, page: int = 1, per_page: int = 20, search: str = None) -> Dict[str, Any]:
        """Get all users with pagination and search"""
        try:
            # Build search condition
            search_condition = ""
            search_params = []
            
            if search:
                search_condition = """
                WHERE (name ILIKE %s OR email ILIKE %s) 
                AND is_active = true
                """
                search_term = f"%{search}%"
                search_params = [search_term, search_term]
            else:
                search_condition = "WHERE is_active = true"
            
            # Get total count
            count_query = f"SELECT COUNT(*) as total FROM users {search_condition}"
            total_result = self.db.execute_query(count_query, tuple(search_params), fetch='one')
            total = total_result['total'] if total_result else 0
            
            # Calculate offset
            offset = (page - 1) * per_page
            
            # Get users with pagination
            query = f"""
            SELECT user_id, client_id, name, email, role, phone, is_active, 
                   last_login, created_at, updated_at,
                   c.name as client_name
            FROM users u
            LEFT JOIN clients c ON u.client_id = c.client_id
            {search_condition}
            ORDER BY u.name
            LIMIT %s OFFSET %s
            """
            
            params = search_params + [per_page, offset]
            users = self.db.execute_query(query, tuple(params))
            
            return {
                'users': users or [],
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': (total + per_page - 1) // per_page
            }
            
        except Exception as e:
            self.logger.error(f"Error getting users: {e}")
            raise
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID with client information"""
        try:
            if not self.db.validate_uuid(user_id):
                return None
                
            query = """
            SELECT u.user_id, u.client_id, u.name, u.email, u.role, u.phone, 
                   u.is_active, u.last_login, u.created_at, u.updated_at,
                   c.name as client_name
            FROM users u
            LEFT JOIN clients c ON u.client_id = c.client_id
            WHERE u.user_id = %s
            """
            
            return self.db.execute_query(query, (user_id,), fetch='one')
            
        except Exception as e:
            self.logger.error(f"Error getting user {user_id}: {e}")
            raise
    
    def create_user(self, user_data: Dict[str, Any], created_by: str) -> Dict[str, Any]:
        """Create a new user"""
        try:
            # Validate input data
            errors = ValidationUtils.validate_user_data(user_data, is_update=False)
            if errors:
                return {'success': False, 'errors': errors}
            
            # Check if email already exists
            existing_user = self.db.get_user_by_email(user_data['email'])
            if existing_user:
                return {'success': False, 'errors': {'email': 'Email already exists'}}
            
            # Validate client_id if provided
            if user_data.get('client_id'):
                client = self.db.execute_query(
                    "SELECT client_id FROM clients WHERE client_id = %s AND is_active = true",
                    (user_data['client_id'],),
                    fetch='one'
                )
                if not client:
                    return {'success': False, 'errors': {'client_id': 'Invalid client ID'}}
            
            # Hash password
            password_hash = self.auth.hash_password(user_data['password'])
            
            # Prepare user data for insertion
            new_user_data = {
                'user_id': str(uuid.uuid4()),
                'client_id': user_data.get('client_id'),
                'name': user_data['name'].strip(),
                'email': user_data['email'].lower().strip(),
                'password_hash': password_hash,
                'role': user_data['role'],
                'phone': user_data.get('phone', '').strip() if user_data.get('phone') else None,
                'is_active': True,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'created_by': created_by
            }
            
            # Insert user
            result = self.db.execute_insert(
                'users',
                new_user_data,
                returning='user_id, name, email, role, created_at'
            )
            
            if result:
                self.logger.info(f"User created successfully: {result['email']}")
                return {'success': True, 'user': result, 'user_id': result['user_id']}
            else:
                return {'success': False, 'errors': {'general': 'Failed to create user'}}
                
        except Exception as e:
            self.logger.error(f"Error creating user: {e}")
            return {'success': False, 'errors': {'general': 'Internal server error'}}
    
    def update_user(self, user_id: str, user_data: Dict[str, Any], updated_by: str) -> Dict[str, Any]:
        """Update an existing user"""
        try:
            # Validate user ID
            if not self.db.validate_uuid(user_id):
                return {'success': False, 'errors': {'user_id': 'Invalid user ID'}}
            
            # Check if user exists
            existing_user = self.get_user_by_id(user_id)
            if not existing_user:
                return {'success': False, 'errors': {'user_id': 'User not found'}}
            
            # Validate input data
            errors = ValidationUtils.validate_user_data(user_data, is_update=True)
            if errors:
                return {'success': False, 'errors': errors}
            
            # Check email uniqueness if email is being changed
            if 'email' in user_data and user_data['email'] != existing_user['email']:
                email_check = self.db.get_user_by_email(user_data['email'])
                if email_check:
                    return {'success': False, 'errors': {'email': 'Email already exists'}}
            
            # Validate client_id if provided
            if user_data.get('client_id'):
                client = self.db.execute_query(
                    "SELECT client_id FROM clients WHERE client_id = %s AND is_active = true",
                    (user_data['client_id'],),
                    fetch='one'
                )
                if not client:
                    return {'success': False, 'errors': {'client_id': 'Invalid client ID'}}
            
            # Prepare update data
            update_data = {
                'updated_at': datetime.utcnow(),
                'updated_by': updated_by
            }
            
            # Add fields that can be updated
            updatable_fields = ['name', 'email', 'role', 'phone', 'client_id', 'is_active']
            for field in updatable_fields:
                if field in user_data:
                    if field == 'email':
                        update_data[field] = user_data[field].lower().strip()
                    elif field == 'name':
                        update_data[field] = user_data[field].strip()
                    elif field == 'phone':
                        update_data[field] = user_data[field].strip() if user_data[field] else None
                    else:
                        update_data[field] = user_data[field]
            
            # Handle password update separately
            if 'password' in user_data and user_data['password']:
                password_validation = ValidationUtils.validate_password(user_data['password'])
                if not password_validation['valid']:
                    return {'success': False, 'errors': {'password': '; '.join(password_validation['errors'])}}
                update_data['password_hash'] = self.auth.hash_password(user_data['password'])
            
            # Update user
            rows_updated = self.db.execute_update(
                'users',
                update_data,
                'user_id = %s',
                (user_id,)
            )
            
            if rows_updated > 0:
                # Get updated user
                updated_user = self.get_user_by_id(user_id)
                self.logger.info(f"User updated successfully: {updated_user['email']}")
                return {'success': True, 'user': updated_user}
            else:
                return {'success': False, 'errors': {'general': 'Failed to update user'}}
                
        except Exception as e:
            self.logger.error(f"Error updating user {user_id}: {e}")
            return {'success': False, 'errors': {'general': 'Internal server error'}}
    
    def delete_user(self, user_id: str, deleted_by: str) -> Dict[str, Any]:
        """Soft delete a user (set is_active = false)"""
        try:
            # Validate user ID
            if not self.db.validate_uuid(user_id):
                return {'success': False, 'errors': {'user_id': 'Invalid user ID'}}
            
            # Check if user exists
            existing_user = self.get_user_by_id(user_id)
            if not existing_user:
                return {'success': False, 'errors': {'user_id': 'User not found'}}
            
            # Prevent self-deletion
            if user_id == deleted_by:
                return {'success': False, 'errors': {'general': 'Cannot delete your own account'}}
            
            # Soft delete (set is_active = false)
            rows_updated = self.db.execute_update(
                'users',
                {
                    'is_active': False,
                    'updated_at': datetime.utcnow(),
                    'updated_by': deleted_by
                },
                'user_id = %s',
                (user_id,)
            )
            
            if rows_updated > 0:
                self.logger.info(f"User deleted successfully: {existing_user['email']}")
                return {'success': True, 'message': 'User deleted successfully'}
            else:
                return {'success': False, 'errors': {'general': 'Failed to delete user'}}
                
        except Exception as e:
            self.logger.error(f"Error deleting user {user_id}: {e}")
            return {'success': False, 'errors': {'general': 'Internal server error'}}
    
    def get_users_by_client(self, client_id: str) -> List[Dict]:
        """Get all users for a specific client"""
        try:
            if not self.db.validate_uuid(client_id):
                return []
                
            query = """
            SELECT user_id, name, email, role, phone, is_active, 
                   last_login, created_at
            FROM users
            WHERE client_id = %s AND is_active = true
            ORDER BY name
            """
            
            return self.db.execute_query(query, (client_id,)) or []
            
        except Exception as e:
            self.logger.error(f"Error getting users for client {client_id}: {e}")
            return []
    
    def assign_user_to_sites(self, user_id: str, site_ids: List[str], assigned_by: str) -> Dict[str, Any]:
        """Assign user to multiple sites"""
        try:
            # Validate user ID
            if not self.db.validate_uuid(user_id):
                return {'success': False, 'errors': {'user_id': 'Invalid user ID'}}
            
            # Check if user exists
            user = self.get_user_by_id(user_id)
            if not user:
                return {'success': False, 'errors': {'user_id': 'User not found'}}
            
            # Validate site IDs
            for site_id in site_ids:
                if not self.db.validate_uuid(site_id):
                    return {'success': False, 'errors': {'site_ids': f'Invalid site ID: {site_id}'}}
            
            # Remove existing assignments
            self.db.execute_delete(
                'user_site_assignments',
                'user_id = %s',
                (user_id,)
            )
            
            # Add new assignments
            for site_id in site_ids:
                assignment_data = {
                    'assignment_id': str(uuid.uuid4()),
                    'user_id': user_id,
                    'site_id': site_id,
                    'assigned_by': assigned_by,
                    'created_at': datetime.utcnow()
                }
                self.db.execute_insert('user_site_assignments', assignment_data)
            
            self.logger.info(f"User {user_id} assigned to {len(site_ids)} sites")
            return {'success': True, 'message': f'User assigned to {len(site_ids)} sites'}
            
        except Exception as e:
            self.logger.error(f"Error assigning user to sites: {e}")
            return {'success': False, 'errors': {'general': 'Internal server error'}}

    def create_solicitante(self, user_data: Dict[str, Any], site_ids: List[str], created_by: str) -> Dict[str, Any]:
        """Create a new solicitante user and assign to sites"""
        try:
            self.logger.info(f"Creating solicitante: {user_data.get('name')} with sites: {site_ids}")

            # Validate required fields for solicitante (phone is mandatory for solicitantes)
            required_fields = ['client_id', 'name', 'email', 'password', 'phone']
            for field in required_fields:
                if field not in user_data or not user_data[field]:
                    field_name = 'teléfono' if field == 'phone' else field
                    self.logger.error(f"Missing required field: {field}")
                    return {'success': False, 'errors': {field: f'{field_name} es requerido para solicitantes'}}

            # Validate client exists
            client = self.db.execute_query(
                "SELECT client_id FROM clients WHERE client_id = %s AND is_active = true",
                (user_data['client_id'],),
                fetch='one'
            )
            if not client:
                return {'success': False, 'errors': {'client_id': 'Invalid client ID'}}

            # Validate sites belong to the same client
            if site_ids:
                # Convert site_ids to proper format for PostgreSQL
                site_ids_array = '{' + ','.join(site_ids) + '}'
                site_check = self.db.execute_query(
                    "SELECT COUNT(*) as count FROM sites WHERE site_id = ANY(%s::uuid[]) AND client_id = %s AND is_active = true",
                    (site_ids_array, user_data['client_id']),
                    fetch='one'
                )
                if not site_check or site_check['count'] != len(site_ids):
                    return {'success': False, 'errors': {'sites': 'One or more sites do not belong to the specified client'}}

            # Create user with solicitante role
            user_data['role'] = 'solicitante'
            self.logger.info(f"Creating user with data: {user_data}")
            create_result = self.create_user(user_data, created_by)

            if not create_result['success']:
                self.logger.error(f"User creation failed: {create_result}")
                return create_result

            user_id = create_result['user_id']
            self.logger.info(f"User created with ID: {user_id}")

            # Assign user to sites
            if site_ids:
                for site_id in site_ids:
                    assignment_data = {
                        'assignment_id': str(uuid.uuid4()),
                        'user_id': user_id,
                        'site_id': site_id,
                        'assigned_by': created_by,
                        'created_at': datetime.utcnow()
                    }
                    self.db.execute_insert('user_site_assignments', assignment_data)

            self.logger.info(f"Solicitante created successfully: {user_data['name']} (ID: {user_id})")
            return {
                'success': True,
                'user_id': user_id,
                'name': user_data['name'],
                'assigned_sites': len(site_ids) if site_ids else 0,
                'message': 'Solicitante created successfully'
            }

        except Exception as e:
            self.logger.error(f"Error creating solicitante: {e}")
            return {'success': False, 'errors': {'general': 'Failed to create solicitante'}}

    def get_users_by_client(self, client_id: str, role: str = None) -> Dict[str, Any]:
        """Get users by client ID, optionally filtered by role"""
        try:
            query = """
                SELECT user_id, name, email, role, phone, is_active, created_at
                FROM users
                WHERE client_id = %s AND is_active = true
            """
            params = [client_id]

            if role:
                query += " AND role = %s"
                params.append(role)

            query += " ORDER BY name"

            users = self.db.execute_query(query, tuple(params), fetch='all')

            return {
                'success': True,
                'users': users or [],
                'count': len(users) if users else 0
            }

        except Exception as e:
            self.logger.error(f"Error getting users by client: {e}")
            return {'success': False, 'errors': {'general': 'Failed to get users'}}

    def create_technician(self, user_data: Dict[str, Any], created_by: str) -> Dict[str, Any]:
        """Create a new technician user"""
        try:
            # Validate required fields for technician
            required_fields = ['name', 'email', 'password']
            for field in required_fields:
                if field not in user_data or not user_data[field]:
                    return {'success': False, 'errors': {field: f'{field} is required'}}

            # Technicians don't belong to a specific client
            user_data['client_id'] = None
            user_data['role'] = 'technician'

            # Create user
            create_result = self.create_user(user_data, created_by)

            if create_result['success']:
                self.logger.info(f"Technician created successfully: {user_data['name']} (ID: {create_result['user_id']})")

            return create_result

        except Exception as e:
            self.logger.error(f"Error creating technician: {e}")
            return {'success': False, 'errors': {'general': 'Failed to create technician'}}

    def get_users_by_client(self, client_id: str, role: str = None) -> Dict[str, Any]:
        """Get all users for a specific client, optionally filtered by role"""
        try:
            conditions = ["client_id = %s", "is_active = true"]
            params = [client_id]

            if role:
                conditions.append("role = %s")
                params.append(role)

            query = f"""
            SELECT user_id, name, email, role, phone, is_active,
                   last_login, created_at, updated_at
            FROM users
            WHERE {' AND '.join(conditions)}
            ORDER BY name
            """

            users = self.db.execute_query(query, tuple(params))

            return {
                'success': True,
                'users': users,
                'total': len(users)
            }

        except Exception as e:
            self.logger.error(f"Error getting users for client {client_id}: {e}")
            return {'success': False, 'error': 'Failed to retrieve users'}

    def get_available_sites_for_user(self, user_id: str) -> Dict[str, Any]:
        """Get sites that a user can be assigned to"""
        try:
            # Get user info
            user = self.db.execute_query(
                "SELECT user_id, client_id, role FROM users WHERE user_id = %s AND is_active = true",
                (user_id,),
                fetch='one'
            )
            if not user:
                return {'success': False, 'error': 'User not found'}

            # For client users (solicitante, client_admin), only show sites from their client
            # For technicians, show all sites
            if user['role'] in ['solicitante', 'client_admin'] and user['client_id']:
                query = """
                SELECT s.site_id, s.name, s.address, s.city, s.state,
                       CASE WHEN usa.user_id IS NOT NULL THEN true ELSE false END as is_assigned
                FROM sites s
                LEFT JOIN user_site_assignments usa ON s.site_id = usa.site_id AND usa.user_id = %s
                WHERE s.client_id = %s AND s.is_active = true
                ORDER BY s.name
                """
                params = (user_id, user['client_id'])
            else:
                # Technicians can be assigned to any site
                query = """
                SELECT s.site_id, s.name, s.address, s.city, s.state, c.name as client_name,
                       CASE WHEN usa.user_id IS NOT NULL THEN true ELSE false END as is_assigned
                FROM sites s
                JOIN clients c ON s.client_id = c.client_id
                LEFT JOIN user_site_assignments usa ON s.site_id = usa.site_id AND usa.user_id = %s
                WHERE s.is_active = true
                ORDER BY c.name, s.name
                """
                params = (user_id,)

            sites = self.db.execute_query(query, params)

            return {
                'success': True,
                'sites': sites,
                'user': user
            }

        except Exception as e:
            self.logger.error(f"Error getting available sites for user {user_id}: {e}")
            return {'success': False, 'error': 'Failed to retrieve available sites'}
