#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - Client Creation Wizard Service
MSP Workflow: Cliente Padre → Admin Principal (solicitante) → Sitio(s) → Asignación de Solicitantes a Sitios
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from core.database import DatabaseManager
from core.auth import AuthManager
import logging
import bcrypt

class ClientWizardService:
    """Service class for MSP client creation wizard"""
    
    def __init__(self, db_manager: DatabaseManager, auth_manager: AuthManager):
        self.db = db_manager
        self.auth = auth_manager
        self.logger = logging.getLogger(__name__)
    
    def create_client_complete(self, wizard_data: Dict[str, Any], created_by: str) -> Dict[str, Any]:
        """
        Complete MSP client creation wizard
        Steps: 1. Cliente Padre → 2. Admin Principal → 3. Sitio(s) → 4. Asignación
        """
        try:
            # Validate wizard data structure
            required_sections = ['client', 'admin_user', 'sites']
            for section in required_sections:
                if section not in wizard_data:
                    return {'success': False, 'errors': {section: f'{section} data is required'}}
            
            # Step 1: Create Cliente Padre
            client_result = self._create_client_step(wizard_data['client'], created_by)
            if not client_result['success']:
                return client_result

            client_id = client_result['client_id']

            # Step 2: Create Admin Principal (solicitante)
            admin_result = self._create_admin_user_step(
                wizard_data['admin_user'],
                client_id,
                created_by
            )
            if not admin_result['success']:
                return admin_result

            admin_user_id = admin_result['user_id']

            # Step 3: Create Sitio(s) - mínimo 1
            sites_result = self._create_sites_step(
                wizard_data['sites'],
                client_id,
                created_by
            )
            if not sites_result['success']:
                return sites_result

            site_ids = sites_result['site_ids']

            # Step 4: Assign Admin to Sites (mínimo 1 sitio)
            assignment_result = self._assign_user_to_sites(
                admin_user_id,
                site_ids,
                created_by
            )
            if not assignment_result['success']:
                return assignment_result

            # Step 5: Create Additional Contacts (optional)
            additional_users = []
            if wizard_data.get('additional_users'):
                for user_data in wizard_data['additional_users']:
                    user_result = self._create_additional_user_step(
                        user_data,
                        client_id,
                        created_by
                    )
                    if user_result['success']:
                        additional_users.append(user_result['user_id'])

                        # Assign to specified sites
                        if user_data.get('site_ids'):
                            self._assign_user_to_sites(
                                user_result['user_id'],
                                user_data['site_ids'],
                                created_by
                            )

            # Log successful completion
            self.logger.info(f"Client wizard completed successfully for client: {client_id}")

            return {
                'success': True,
                'client_id': client_id,
                'admin_user_id': admin_user_id,
                'site_ids': site_ids,
                'additional_user_ids': additional_users,
                'message': 'Client created successfully with complete MSP setup'
            }
                    
        except Exception as e:
            self.logger.error(f"Error in client wizard: {e}")
            return {'success': False, 'errors': {'general': 'Internal server error'}}
    
    def _create_client_step(self, client_data: Dict, created_by: str) -> Dict[str, Any]:
        """Step 1: Create Cliente Padre"""
        try:
            # Validate required fields
            required_fields = ['name', 'email']
            for field in required_fields:
                if field not in client_data or not client_data[field]:
                    return {'success': False, 'errors': {field: f'{field} is required'}}
            
            # Validate email format
            import re
            email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
            if not re.match(email_pattern, client_data['email']):
                return {'success': False, 'errors': {'email': 'Invalid email format'}}
            
            # Check if client name already exists
            name_check = self.db.execute_query(
                "SELECT client_id FROM clients WHERE name = %s AND is_active = true",
                (client_data['name'].strip(),),
                fetch='one'
            )
            if name_check:
                return {'success': False, 'errors': {'name': 'Client name already exists'}}

            # Check if email already exists
            email_check = self.db.execute_query(
                "SELECT client_id FROM clients WHERE email = %s AND is_active = true",
                (client_data['email'].lower().strip(),),
                fetch='one'
            )
            if email_check:
                return {'success': False, 'errors': {'email': 'Email already exists'}}
            
            # Prepare client data
            client_id = str(uuid.uuid4())
            insert_data = {
                'client_id': client_id,
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
            
            # Insert client
            result = self.db.execute_insert(
                'clients',
                insert_data,
                returning='client_id, name'
            )

            if not result:
                return {'success': False, 'errors': {'general': 'Failed to create client'}}
            
            return {
                'success': True,
                'client_id': client_id,
                'client_name': insert_data['name']
            }
            
        except Exception as e:
            self.logger.error(f"Error creating client: {e}")
            return {'success': False, 'errors': {'general': 'Failed to create client'}}
    
    def _create_admin_user_step(self, user_data: Dict, client_id: str, created_by: str) -> Dict[str, Any]:
        """Step 2: Create Admin Principal (solicitante)"""
        try:
            # Validate required fields
            required_fields = ['name', 'email', 'password']
            for field in required_fields:
                if field not in user_data or not user_data[field]:
                    return {'success': False, 'errors': {field: f'{field} is required'}}

            # Validate email format
            import re
            email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
            if not re.match(email_pattern, user_data['email']):
                return {'success': False, 'errors': {'email': 'Invalid email format'}}

            # Check if email already exists
            email_check = self.db.execute_query(
                "SELECT user_id FROM users WHERE email = %s",
                (user_data['email'].lower().strip(),),
                fetch='one'
            )
            if email_check:
                return {'success': False, 'errors': {'email': 'Email already exists'}}

            # Hash password
            salt = bcrypt.gensalt()
            password_hash = bcrypt.hashpw(user_data['password'].encode('utf-8'), salt).decode('utf-8')

            # Prepare user data
            user_id = str(uuid.uuid4())
            insert_data = {
                'user_id': user_id,
                'client_id': client_id,
                'name': user_data['name'].strip(),
                'email': user_data['email'].lower().strip(),
                'password_hash': password_hash,
                'role': user_data.get('role', 'client_admin'),  # Default to client_admin
                'phone': user_data.get('phone', '').strip() if user_data.get('phone') else None,
                'is_active': True,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'created_by': created_by
            }

            # Insert user using database manager
            result = self.db.execute_insert(
                'users',
                insert_data,
                returning='user_id, name'
            )

            if not result:
                return {'success': False, 'errors': {'general': 'Failed to create admin user'}}

            return {
                'success': True,
                'user_id': user_id,
                'user_name': insert_data['name']
            }

        except Exception as e:
            self.logger.error(f"Error creating admin user: {e}")
            return {'success': False, 'errors': {'general': 'Failed to create admin user'}}
    
    def _create_sites_step(self, sites_data: List[Dict], client_id: str, created_by: str) -> Dict[str, Any]:
        """Step 3: Create Sitio(s) - mínimo 1"""
        try:
            if not sites_data or len(sites_data) == 0:
                return {'success': False, 'errors': {'sites': 'At least one site is required'}}

            site_ids = []

            for i, site_data in enumerate(sites_data):
                # Validate required fields
                required_fields = ['name', 'address', 'city', 'state', 'postal_code']
                for field in required_fields:
                    if field not in site_data or not site_data[field]:
                        return {'success': False, 'errors': {f'site_{i}_{field}': f'{field} is required for site {i+1}'}}

                # Check if site name already exists for this client
                site_check = self.db.execute_query(
                    "SELECT site_id FROM sites WHERE client_id = %s AND name = %s AND is_active = true",
                    (client_id, site_data['name'].strip()),
                    fetch='one'
                )
                if site_check:
                    return {'success': False, 'errors': {f'site_{i}_name': f'Site name already exists for this client'}}

                # Prepare site data
                site_id = str(uuid.uuid4())
                insert_data = {
                    'site_id': site_id,
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

                # Insert site using database manager
                result = self.db.execute_insert(
                    'sites',
                    insert_data,
                    returning='site_id'
                )

                if not result:
                    return {'success': False, 'errors': {'general': f'Failed to create site {i+1}'}}

                site_ids.append(site_id)

            return {
                'success': True,
                'site_ids': site_ids
            }

        except Exception as e:
            self.logger.error(f"Error creating sites: {e}")
            return {'success': False, 'errors': {'general': 'Failed to create sites'}}
    
    def _assign_user_to_sites(self, user_id: str, site_ids: List[str], assigned_by: str) -> Dict[str, Any]:
        """Step 4: Assign user to sites (mínimo 1 sitio)"""
        try:
            if not site_ids or len(site_ids) == 0:
                return {'success': False, 'errors': {'sites': 'User must be assigned to at least one site'}}

            # Create individual site assignments in user_site_assignments table
            for site_id in site_ids:
                assignment_data = {
                    'assignment_id': str(uuid.uuid4()),
                    'user_id': user_id,
                    'site_id': site_id,
                    'assigned_by': assigned_by,
                    'created_at': datetime.utcnow()
                }

                result = self.db.execute_insert('user_site_assignments', assignment_data)
                if not result:
                    self.logger.error(f"Failed to assign user {user_id} to site {site_id}")

            return {'success': True}

        except Exception as e:
            self.logger.error(f"Error assigning user to sites: {e}")
            return {'success': False, 'errors': {'general': 'Failed to assign user to sites'}}
    
    def _create_additional_user_step(self, user_data: Dict, client_id: str, created_by: str) -> Dict[str, Any]:
        """Step 5: Create additional solicitante (optional)"""
        try:
            # Same validation as admin user but role defaults to 'solicitante'
            user_data['role'] = user_data.get('role', 'solicitante')
            return self._create_admin_user_step(user_data, client_id, created_by)

        except Exception as e:
            self.logger.error(f"Error creating additional user: {e}")
            return {'success': False, 'errors': {'general': 'Failed to create additional user'}}
