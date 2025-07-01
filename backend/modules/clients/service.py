#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - Clients Module Service
Business logic for client and site management operations
MSP Workflow: Organization → Sites → Contacts → Tickets
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from core.database import DatabaseManager
from core.auth import AuthManager
from utils.validators import ValidationUtils
import logging

class ClientService:
    """Service class for client and site management operations"""
    
    def __init__(self, db_manager: DatabaseManager, auth_manager: AuthManager):
        self.db = db_manager
        self.auth = auth_manager
        self.logger = logging.getLogger(__name__)
    
    def get_all_clients(self, page: int = 1, per_page: int = 20, search: str = None) -> Dict[str, Any]:
        """Get all clients with pagination and search"""
        try:
            # Build search condition
            search_condition = ""
            search_params = []
            
            if search:
                search_condition = """
                WHERE (c.name ILIKE %s OR c.email ILIKE %s OR c.rfc ILIKE %s) 
                AND c.is_active = true
                """
                search_term = f"%{search}%"
                search_params = [search_term, search_term, search_term]
            else:
                search_condition = "WHERE c.is_active = true"
            
            # Get total count
            count_query = f"SELECT COUNT(*) as total FROM clients c {search_condition}"
            total_result = self.db.execute_query(count_query, tuple(search_params), fetch='one')
            total = total_result['total'] if total_result else 0
            
            # Calculate offset
            offset = (page - 1) * per_page
            
            # Get clients with pagination and related data
            query = f"""
            SELECT c.client_id, c.name, c.rfc, c.email, c.phone, c.address, c.city, 
                   c.state, c.country, c.postal_code, c.is_active, c.created_at, c.updated_at,
                   COUNT(DISTINCT s.site_id) as total_sites,
                   COUNT(DISTINCT u.user_id) as total_users,
                   COUNT(DISTINCT t.ticket_id) as total_tickets
            FROM clients c
            LEFT JOIN sites s ON c.client_id = s.client_id AND s.is_active = true
            LEFT JOIN users u ON c.client_id = u.client_id AND u.is_active = true
            LEFT JOIN tickets t ON c.client_id = t.client_id
            {search_condition}
            GROUP BY c.client_id, c.name, c.rfc, c.email, c.phone, c.address, 
                     c.city, c.state, c.country, c.postal_code, c.is_active, 
                     c.created_at, c.updated_at
            ORDER BY c.name
            LIMIT %s OFFSET %s
            """
            
            params = search_params + [per_page, offset]
            clients = self.db.execute_query(query, tuple(params))
            
            return {
                'clients': clients or [],
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': (total + per_page - 1) // per_page
            }
            
        except Exception as e:
            self.logger.error(f"Error getting clients: {e}")
            raise
    
    def get_client_by_id(self, client_id: str) -> Optional[Dict]:
        """Get client by ID with complete information"""
        try:
            if not self.db.validate_uuid(client_id):
                return None
                
            query = """
            SELECT c.client_id, c.name, c.rfc, c.email, c.phone, c.allowed_emails,
                   c.address, c.city, c.state, c.country, c.postal_code, 
                   c.is_active, c.created_at, c.updated_at,
                   COUNT(DISTINCT s.site_id) as total_sites,
                   COUNT(DISTINCT u.user_id) as total_users,
                   COUNT(DISTINCT t.ticket_id) as total_tickets,
                   COUNT(DISTINCT CASE WHEN t.status IN ('nuevo', 'asignado', 'en_proceso') THEN t.ticket_id END) as open_tickets
            FROM clients c
            LEFT JOIN sites s ON c.client_id = s.client_id AND s.is_active = true
            LEFT JOIN users u ON c.client_id = u.client_id AND u.is_active = true
            LEFT JOIN tickets t ON c.client_id = t.client_id
            WHERE c.client_id = %s
            GROUP BY c.client_id, c.name, c.rfc, c.email, c.phone, c.allowed_emails,
                     c.address, c.city, c.state, c.country, c.postal_code, 
                     c.is_active, c.created_at, c.updated_at
            """
            
            return self.db.execute_query(query, (client_id,), fetch='one')
            
        except Exception as e:
            self.logger.error(f"Error getting client {client_id}: {e}")
            raise
    
    def create_client(self, client_data: Dict[str, Any], created_by: str) -> Dict[str, Any]:
        """Create a new client with MSP workflow validation"""
        try:
            # Validate input data
            errors = ValidationUtils.validate_client_data(client_data, is_update=False)
            if errors:
                return {'success': False, 'errors': errors}
            
            # Check if client name already exists
            existing_client = self.db.execute_query(
                "SELECT client_id FROM clients WHERE name = %s AND is_active = true",
                (client_data['name'].strip(),),
                fetch='one'
            )
            if existing_client:
                return {'success': False, 'errors': {'name': 'Client name already exists'}}
            
            # Check if email already exists
            if client_data.get('email'):
                existing_email = self.db.execute_query(
                    "SELECT client_id FROM clients WHERE email = %s AND is_active = true",
                    (client_data['email'].lower().strip(),),
                    fetch='one'
                )
                if existing_email:
                    return {'success': False, 'errors': {'email': 'Email already exists'}}
            
            # Prepare client data for insertion
            new_client_data = {
                'client_id': str(uuid.uuid4()),
                'name': client_data['name'].strip(),
                'rfc': client_data.get('rfc', '').strip() if client_data.get('rfc') else None,
                'email': client_data.get('email', '').lower().strip() if client_data.get('email') else None,
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
                new_client_data,
                returning='client_id, name, email, created_at'
            )
            
            if result:
                self.logger.info(f"Client created successfully: {result['name']}")
                return {'success': True, 'client': result}
            else:
                return {'success': False, 'errors': {'general': 'Failed to create client'}}
                
        except Exception as e:
            self.logger.error(f"Error creating client: {e}")
            return {'success': False, 'errors': {'general': 'Internal server error'}}
    
    def update_client(self, client_id: str, client_data: Dict[str, Any], updated_by: str) -> Dict[str, Any]:
        """Update an existing client"""
        try:
            # Validate client ID
            if not self.db.validate_uuid(client_id):
                return {'success': False, 'errors': {'client_id': 'Invalid client ID'}}
            
            # Check if client exists
            existing_client = self.get_client_by_id(client_id)
            if not existing_client:
                return {'success': False, 'errors': {'client_id': 'Client not found'}}
            
            # Validate input data
            errors = ValidationUtils.validate_client_data(client_data, is_update=True)
            if errors:
                return {'success': False, 'errors': errors}
            
            # Check name uniqueness if name is being changed
            if 'name' in client_data and client_data['name'] != existing_client['name']:
                name_check = self.db.execute_query(
                    "SELECT client_id FROM clients WHERE name = %s AND client_id != %s AND is_active = true",
                    (client_data['name'].strip(), client_id),
                    fetch='one'
                )
                if name_check:
                    return {'success': False, 'errors': {'name': 'Client name already exists'}}
            
            # Check email uniqueness if email is being changed
            if 'email' in client_data and client_data.get('email') != existing_client.get('email'):
                if client_data.get('email'):
                    email_check = self.db.execute_query(
                        "SELECT client_id FROM clients WHERE email = %s AND client_id != %s AND is_active = true",
                        (client_data['email'].lower().strip(), client_id),
                        fetch='one'
                    )
                    if email_check:
                        return {'success': False, 'errors': {'email': 'Email already exists'}}
            
            # Prepare update data
            update_data = {
                'updated_at': datetime.utcnow(),
                'updated_by': updated_by
            }
            
            # Add fields that can be updated
            updatable_fields = ['name', 'rfc', 'email', 'phone', 'allowed_emails', 
                              'address', 'city', 'state', 'country', 'postal_code', 'is_active']
            for field in updatable_fields:
                if field in client_data:
                    if field == 'email':
                        update_data[field] = client_data[field].lower().strip() if client_data[field] else None
                    elif field in ['name', 'rfc', 'phone', 'address', 'city', 'state', 'country', 'postal_code']:
                        update_data[field] = client_data[field].strip() if client_data[field] else None
                    else:
                        update_data[field] = client_data[field]
            
            # Update client
            rows_updated = self.db.execute_update(
                'clients',
                update_data,
                'client_id = %s',
                (client_id,)
            )
            
            if rows_updated > 0:
                # Get updated client
                updated_client = self.get_client_by_id(client_id)
                self.logger.info(f"Client updated successfully: {updated_client['name']}")
                return {'success': True, 'client': updated_client}
            else:
                return {'success': False, 'errors': {'general': 'Failed to update client'}}
                
        except Exception as e:
            self.logger.error(f"Error updating client {client_id}: {e}")
            return {'success': False, 'errors': {'general': 'Internal server error'}}
    
    def delete_client(self, client_id: str, deleted_by: str) -> Dict[str, Any]:
        """Soft delete a client (set is_active = false)"""
        try:
            # Validate client ID
            if not self.db.validate_uuid(client_id):
                return {'success': False, 'errors': {'client_id': 'Invalid client ID'}}
            
            # Check if client exists
            existing_client = self.get_client_by_id(client_id)
            if not existing_client:
                return {'success': False, 'errors': {'client_id': 'Client not found'}}
            
            # Check if client has active tickets
            active_tickets = self.db.execute_query(
                "SELECT COUNT(*) as count FROM tickets WHERE client_id = %s AND status NOT IN ('cerrado', 'resuelto', 'cancelado')",
                (client_id,),
                fetch='one'
            )
            
            if active_tickets and active_tickets['count'] > 0:
                return {'success': False, 'errors': {'general': 'Cannot delete client with active tickets'}}
            
            # Soft delete client and related entities
            with self.db.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Deactivate client
                    cursor.execute(
                        "UPDATE clients SET is_active = false, updated_at = %s, updated_by = %s WHERE client_id = %s",
                        (datetime.utcnow(), deleted_by, client_id)
                    )
                    
                    # Deactivate related sites
                    cursor.execute(
                        "UPDATE sites SET is_active = false, updated_at = %s, updated_by = %s WHERE client_id = %s",
                        (datetime.utcnow(), deleted_by, client_id)
                    )
                    
                    # Deactivate related users
                    cursor.execute(
                        "UPDATE users SET is_active = false, updated_at = %s, updated_by = %s WHERE client_id = %s",
                        (datetime.utcnow(), deleted_by, client_id)
                    )
                    
                    conn.commit()
            
            self.logger.info(f"Client deleted successfully: {existing_client['name']}")
            return {'success': True, 'message': 'Client and related entities deleted successfully'}
                
        except Exception as e:
            self.logger.error(f"Error deleting client {client_id}: {e}")
            return {'success': False, 'errors': {'general': 'Internal server error'}}

    # Site Management Methods

    def get_sites_by_client(self, client_id: str) -> List[Dict]:
        """Get all sites for a specific client"""
        try:
            if not self.db.validate_uuid(client_id):
                return []

            query = """
            SELECT s.site_id, s.client_id, s.name, s.address, s.city, s.state,
                   s.country, s.postal_code, s.latitude, s.longitude, s.is_active,
                   s.created_at, s.updated_at,
                   COUNT(DISTINCT u.user_id) as total_users,
                   COUNT(DISTINCT t.ticket_id) as total_tickets
            FROM sites s
            LEFT JOIN users u ON s.site_id = ANY(u.site_ids) AND u.is_active = true
            LEFT JOIN tickets t ON s.site_id = t.site_id
            WHERE s.client_id = %s AND s.is_active = true
            GROUP BY s.site_id, s.client_id, s.name, s.address, s.city, s.state,
                     s.country, s.postal_code, s.latitude, s.longitude, s.is_active,
                     s.created_at, s.updated_at
            ORDER BY s.name
            """

            return self.db.execute_query(query, (client_id,)) or []

        except Exception as e:
            self.logger.error(f"Error getting sites for client {client_id}: {e}")
            return []

    def create_site(self, site_data: Dict[str, Any], created_by: str) -> Dict[str, Any]:
        """Create a new site for a client"""
        try:
            # Validate input data
            errors = ValidationUtils.validate_site_data(site_data, is_update=False)
            if errors:
                return {'success': False, 'errors': errors}

            # Validate client exists
            client = self.get_client_by_id(site_data['client_id'])
            if not client:
                return {'success': False, 'errors': {'client_id': 'Invalid client ID'}}

            # Check if site name already exists for this client
            existing_site = self.db.execute_query(
                "SELECT site_id FROM sites WHERE client_id = %s AND name = %s AND is_active = true",
                (site_data['client_id'], site_data['name'].strip()),
                fetch='one'
            )
            if existing_site:
                return {'success': False, 'errors': {'name': 'Site name already exists for this client'}}

            # Prepare site data for insertion
            new_site_data = {
                'site_id': str(uuid.uuid4()),
                'client_id': site_data['client_id'],
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

            # Insert site
            result = self.db.execute_insert(
                'sites',
                new_site_data,
                returning='site_id, name, address, city, state, created_at'
            )

            if result:
                self.logger.info(f"Site created successfully: {result['name']}")
                return {'success': True, 'site': result}
            else:
                return {'success': False, 'errors': {'general': 'Failed to create site'}}

        except Exception as e:
            self.logger.error(f"Error creating site: {e}")
            return {'success': False, 'errors': {'general': 'Internal server error'}}

    def update_site(self, site_id: str, site_data: Dict[str, Any], updated_by: str) -> Dict[str, Any]:
        """Update an existing site"""
        try:
            # Validate site ID
            if not self.db.validate_uuid(site_id):
                return {'success': False, 'errors': {'site_id': 'Invalid site ID'}}

            # Check if site exists
            existing_site = self.db.execute_query(
                "SELECT * FROM sites WHERE site_id = %s",
                (site_id,),
                fetch='one'
            )
            if not existing_site:
                return {'success': False, 'errors': {'site_id': 'Site not found'}}

            # Validate input data
            errors = ValidationUtils.validate_site_data(site_data, is_update=True)
            if errors:
                return {'success': False, 'errors': errors}

            # Check name uniqueness if name is being changed
            if 'name' in site_data and site_data['name'] != existing_site['name']:
                name_check = self.db.execute_query(
                    "SELECT site_id FROM sites WHERE client_id = %s AND name = %s AND site_id != %s AND is_active = true",
                    (existing_site['client_id'], site_data['name'].strip(), site_id),
                    fetch='one'
                )
                if name_check:
                    return {'success': False, 'errors': {'name': 'Site name already exists for this client'}}

            # Prepare update data
            update_data = {
                'updated_at': datetime.utcnow(),
                'updated_by': updated_by
            }

            # Add fields that can be updated
            updatable_fields = ['name', 'address', 'city', 'state', 'country', 'postal_code',
                              'latitude', 'longitude', 'is_active']
            for field in updatable_fields:
                if field in site_data:
                    if field in ['name', 'address', 'city', 'state', 'country', 'postal_code']:
                        update_data[field] = site_data[field].strip() if site_data[field] else None
                    else:
                        update_data[field] = site_data[field]

            # Update site
            rows_updated = self.db.execute_update(
                'sites',
                update_data,
                'site_id = %s',
                (site_id,)
            )

            if rows_updated > 0:
                # Get updated site
                updated_site = self.db.execute_query(
                    "SELECT * FROM sites WHERE site_id = %s",
                    (site_id,),
                    fetch='one'
                )
                self.logger.info(f"Site updated successfully: {updated_site['name']}")
                return {'success': True, 'site': updated_site}
            else:
                return {'success': False, 'errors': {'general': 'Failed to update site'}}

        except Exception as e:
            self.logger.error(f"Error updating site {site_id}: {e}")
            return {'success': False, 'errors': {'general': 'Internal server error'}}

    def delete_site(self, site_id: str, deleted_by: str) -> Dict[str, Any]:
        """Soft delete a site (set is_active = false)"""
        try:
            # Validate site ID
            if not self.db.validate_uuid(site_id):
                return {'success': False, 'errors': {'site_id': 'Invalid site ID'}}

            # Check if site exists
            existing_site = self.db.execute_query(
                "SELECT * FROM sites WHERE site_id = %s",
                (site_id,),
                fetch='one'
            )
            if not existing_site:
                return {'success': False, 'errors': {'site_id': 'Site not found'}}

            # Check if site has active tickets
            active_tickets = self.db.execute_query(
                "SELECT COUNT(*) as count FROM tickets WHERE site_id = %s AND status NOT IN ('cerrado', 'resuelto', 'cancelado')",
                (site_id,),
                fetch='one'
            )

            if active_tickets and active_tickets['count'] > 0:
                return {'success': False, 'errors': {'general': 'Cannot delete site with active tickets'}}

            # Soft delete site
            rows_updated = self.db.execute_update(
                'sites',
                {
                    'is_active': False,
                    'updated_at': datetime.utcnow(),
                    'updated_by': deleted_by
                },
                'site_id = %s',
                (site_id,)
            )

            if rows_updated > 0:
                self.logger.info(f"Site deleted successfully: {existing_site['name']}")
                return {'success': True, 'message': 'Site deleted successfully'}
            else:
                return {'success': False, 'errors': {'general': 'Failed to delete site'}}

        except Exception as e:
            self.logger.error(f"Error deleting site {site_id}: {e}")
            return {'success': False, 'errors': {'general': 'Internal server error'}}

    def get_client_stats(self, client_id: str) -> Dict[str, Any]:
        """Get comprehensive statistics for a client"""
        try:
            if not self.db.validate_uuid(client_id):
                return {}

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

            return self.db.execute_query(stats_query, (client_id,), fetch='one') or {}

        except Exception as e:
            self.logger.error(f"Error getting client stats for {client_id}: {e}")
            return {}
