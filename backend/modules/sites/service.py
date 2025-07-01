#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - Sites Service
Complete CRUD operations for site management
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from core.database import DatabaseManager
from utils.validators import ValidationUtils
import logging

class SitesService:
    """Service class for site management operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.logger = logging.getLogger(__name__)
    
    def get_sites_by_client(self, client_id: str, user_role: str = None, user_client_id: str = None) -> Dict[str, Any]:
        """Get all sites for a specific client with RLS enforcement"""
        try:
            # RLS enforcement: client_admin can only see their own client's sites
            if user_role == 'client_admin' and user_client_id != client_id:
                return {'success': False, 'error': 'Access denied to this client'}
            
            query = """
            SELECT s.site_id, s.name, s.address, s.city, s.state, s.country, 
                   s.postal_code, s.latitude, s.longitude, s.is_active,
                   s.created_at, s.updated_at,
                   COUNT(DISTINCT usa.user_id) as assigned_users,
                   COUNT(DISTINCT t.ticket_id) as total_tickets
            FROM sites s
            LEFT JOIN user_site_assignments usa ON s.site_id = usa.site_id
            LEFT JOIN tickets t ON s.site_id = t.site_id
            WHERE s.client_id = %s AND s.is_active = true
            GROUP BY s.site_id, s.name, s.address, s.city, s.state, s.country,
                     s.postal_code, s.latitude, s.longitude, s.is_active,
                     s.created_at, s.updated_at
            ORDER BY s.name
            """
            
            sites = self.db.execute_query(query, (client_id,))
            
            return {
                'success': True,
                'sites': sites,
                'total': len(sites)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting sites for client {client_id}: {e}")
            return {'success': False, 'error': 'Failed to retrieve sites'}
    
    def get_site_by_id(self, site_id: str, user_role: str = None, user_client_id: str = None) -> Dict[str, Any]:
        """Get a specific site by ID with RLS enforcement"""
        try:
            query = """
            SELECT s.site_id, s.client_id, s.name, s.address, s.city, s.state, 
                   s.country, s.postal_code, s.latitude, s.longitude, s.is_active,
                   s.created_at, s.updated_at, s.created_by,
                   c.name as client_name
            FROM sites s
            JOIN clients c ON s.client_id = c.client_id
            WHERE s.site_id = %s AND s.is_active = true
            """
            
            site = self.db.execute_query(query, (site_id,), fetch='one')
            
            if not site:
                return {'success': False, 'error': 'Site not found'}
            
            # RLS enforcement
            if user_role == 'client_admin' and user_client_id != site['client_id']:
                return {'success': False, 'error': 'Access denied to this site'}
            
            # Get assigned users
            users_query = """
            SELECT u.user_id, u.name, u.email, u.role, usa.created_at as assigned_at
            FROM users u
            JOIN user_site_assignments usa ON u.user_id = usa.user_id
            WHERE usa.site_id = %s AND u.is_active = true
            ORDER BY u.name
            """
            
            assigned_users = self.db.execute_query(users_query, (site_id,))
            
            return {
                'success': True,
                'site': site,
                'assigned_users': assigned_users
            }
            
        except Exception as e:
            self.logger.error(f"Error getting site {site_id}: {e}")
            return {'success': False, 'error': 'Failed to retrieve site'}
    
    def create_site(self, site_data: Dict[str, Any], created_by: str) -> Dict[str, Any]:
        """Create a new site"""
        try:
            # Validate required fields
            required_fields = ['client_id', 'name', 'address', 'city', 'state', 'postal_code']
            for field in required_fields:
                if field not in site_data or not site_data[field]:
                    return {'success': False, 'errors': {field: f'{field} is required'}}
            
            # Validate client exists
            client = self.db.execute_query(
                "SELECT client_id FROM clients WHERE client_id = %s AND is_active = true",
                (site_data['client_id'],),
                fetch='one'
            )
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
            
            # Validate postal code format
            if not ValidationUtils.validate_postal_code(site_data['postal_code']):
                return {'success': False, 'errors': {'postal_code': 'Invalid postal code format'}}
            
            # Prepare site data
            site_id = str(uuid.uuid4())
            insert_data = {
                'site_id': site_id,
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
            result = self.db.execute_insert('sites', insert_data, returning='site_id, name')
            
            if result:
                self.logger.info(f"Site created successfully: {result['name']} (ID: {site_id})")
                return {
                    'success': True,
                    'site_id': site_id,
                    'name': result['name'],
                    'message': 'Site created successfully'
                }
            else:
                return {'success': False, 'errors': {'general': 'Failed to create site'}}
                
        except Exception as e:
            self.logger.error(f"Error creating site: {e}")
            return {'success': False, 'errors': {'general': 'Failed to create site'}}
    
    def update_site(self, site_id: str, site_data: Dict[str, Any], updated_by: str) -> Dict[str, Any]:
        """Update an existing site"""
        try:
            # Check if site exists
            existing_site = self.db.execute_query(
                "SELECT site_id, client_id, name FROM sites WHERE site_id = %s AND is_active = true",
                (site_id,),
                fetch='one'
            )
            if not existing_site:
                return {'success': False, 'error': 'Site not found'}
            
            # Validate required fields if provided
            if 'name' in site_data and not site_data['name']:
                return {'success': False, 'errors': {'name': 'Site name is required'}}
            
            # Check for duplicate name (excluding current site)
            if 'name' in site_data:
                duplicate_check = self.db.execute_query(
                    "SELECT site_id FROM sites WHERE client_id = %s AND name = %s AND site_id != %s AND is_active = true",
                    (existing_site['client_id'], site_data['name'].strip(), site_id),
                    fetch='one'
                )
                if duplicate_check:
                    return {'success': False, 'errors': {'name': 'Site name already exists for this client'}}
            
            # Validate postal code if provided
            if 'postal_code' in site_data and site_data['postal_code']:
                if not ValidationUtils.validate_postal_code(site_data['postal_code']):
                    return {'success': False, 'errors': {'postal_code': 'Invalid postal code format'}}
            
            # Prepare update data
            update_data = {'updated_at': datetime.utcnow()}
            
            # Add fields that are being updated
            updatable_fields = ['name', 'address', 'city', 'state', 'country', 'postal_code', 'latitude', 'longitude']
            for field in updatable_fields:
                if field in site_data:
                    if field in ['name', 'address', 'city', 'state', 'country', 'postal_code']:
                        update_data[field] = site_data[field].strip() if site_data[field] else None
                    else:
                        update_data[field] = site_data[field]
            
            # Update site
            result = self.db.execute_update(
                'sites',
                update_data,
                'site_id = %s',
                (site_id,)
            )
            
            if result:
                self.logger.info(f"Site updated successfully: {site_id}")
                return {
                    'success': True,
                    'site_id': site_id,
                    'message': 'Site updated successfully'
                }
            else:
                return {'success': False, 'error': 'Failed to update site'}
                
        except Exception as e:
            self.logger.error(f"Error updating site {site_id}: {e}")
            return {'success': False, 'error': 'Failed to update site'}
    
    def delete_site(self, site_id: str, deleted_by: str) -> Dict[str, Any]:
        """Soft delete a site (set is_active = false)"""
        try:
            # Check if site exists
            existing_site = self.db.execute_query(
                "SELECT site_id, name FROM sites WHERE site_id = %s AND is_active = true",
                (site_id,),
                fetch='one'
            )
            if not existing_site:
                return {'success': False, 'error': 'Site not found'}
            
            # Check if site has active tickets
            active_tickets = self.db.execute_query(
                "SELECT COUNT(*) as count FROM tickets WHERE site_id = %s AND status NOT IN ('cerrado', 'resuelto')",
                (site_id,),
                fetch='one'
            )
            
            if active_tickets and active_tickets['count'] > 0:
                return {
                    'success': False, 
                    'error': f'Cannot delete site with {active_tickets["count"]} active tickets. Close all tickets first.'
                }
            
            # Soft delete site
            result = self.db.execute_update(
                'sites',
                {
                    'is_active': False,
                    'updated_at': datetime.utcnow()
                },
                'site_id = %s',
                (site_id,)
            )
            
            if result:
                # Also remove user assignments (if any exist)
                try:
                    self.db.execute_query(
                        "DELETE FROM user_site_assignments WHERE site_id = %s",
                        (site_id,),
                        fetch=None  # Don't try to fetch results from DELETE
                    )
                except Exception as e:
                    # It's OK if there are no assignments to delete
                    self.logger.debug(f"No user assignments to delete for site {site_id}: {e}")
                
                self.logger.info(f"Site deleted successfully: {existing_site['name']} (ID: {site_id})")
                return {
                    'success': True,
                    'message': f'Site "{existing_site["name"]}" deleted successfully'
                }
            else:
                return {'success': False, 'error': 'Failed to delete site'}
                
        except Exception as e:
            self.logger.error(f"Error deleting site {site_id}: {e}")
            return {'success': False, 'error': 'Failed to delete site'}
