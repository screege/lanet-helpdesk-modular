#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - Agents Service
Handles business logic for agent installation tokens and agent registration
"""

import logging
import uuid
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from core.database import DatabaseManager


class AgentsService:
    """Service class for managing agent installation tokens and agent registration"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.logger = logging.getLogger(__name__)

    def create_installation_token(self, client_id: str, site_id: str, created_by: str, 
                                 expires_days: Optional[int] = None, notes: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new agent installation token
        
        Args:
            client_id: UUID of the client
            site_id: UUID of the site
            created_by: UUID of the user creating the token
            expires_days: Optional expiration in days (None = no expiration)
            notes: Optional description/notes
            
        Returns:
            Dict with token information
        """
        try:
            # Validate UUIDs
            uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
            if not uuid_pattern.match(client_id):
                raise ValueError("Invalid client_id format")
            if not uuid_pattern.match(site_id):
                raise ValueError("Invalid site_id format")
            if not uuid_pattern.match(created_by):
                raise ValueError("Invalid created_by format")
            
            # Verify client and site exist and are accessible
            client_site_query = """
            SELECT c.name as client_name, s.name as site_name
            FROM clients c
            JOIN sites s ON s.client_id = c.client_id
            WHERE c.client_id = %s AND s.site_id = %s
            """
            client_site = self.db.execute_query(client_site_query, (client_id, site_id), fetch='one')
            
            if not client_site:
                raise ValueError("Client or site not found or not accessible")
            
            # Generate token value using database function
            self.logger.info(f"Generating token for client {client_id}, site {site_id}")
            token_result = self.db.execute_query(
                "SELECT generate_agent_token(%s, %s) as token",
                (client_id, site_id),
                fetch='one'
            )
            token_value = token_result['token']
            self.logger.info(f"Generated token: {token_value}")
            
            # Calculate expiration date if specified
            expires_at = None
            if expires_days and expires_days > 0:
                expires_at = datetime.now() + timedelta(days=expires_days)
            
            # Insert token record
            insert_query = """
            INSERT INTO agent_installation_tokens
            (client_id, site_id, token_value, created_by, expires_at, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING token_id, token_value, created_at
            """

            self.logger.info(f"Inserting token record with values: {client_id}, {site_id}, {token_value}, {created_by}, {expires_at}, {notes}")
            token_record = self.db.execute_query(
                insert_query,
                (client_id, site_id, token_value, created_by, expires_at, notes),
                fetch='one'
            )
            self.logger.info(f"Token record inserted: {token_record}")
            
            self.logger.info(f"Created installation token {token_value} for client {client_id}, site {site_id}")
            
            return {
                'token_id': str(token_record['token_id']),
                'token_value': token_record['token_value'],
                'client_id': client_id,
                'site_id': site_id,
                'client_name': client_site['client_name'],
                'site_name': client_site['site_name'],
                'expires_at': expires_at.isoformat() if expires_at else None,
                'notes': notes,
                'created_at': token_record['created_at'].isoformat(),
                'usage_count': 0,
                'is_active': True
            }
            
        except Exception as e:
            self.logger.error(f"Error creating installation token: {e}")
            raise

    def get_tokens_for_client_site(self, client_id: str, site_id: str) -> List[Dict[str, Any]]:
        """
        Get all installation tokens for a specific client and site
        
        Args:
            client_id: UUID of the client
            site_id: UUID of the site
            
        Returns:
            List of token dictionaries
        """
        try:
            query = """
            SELECT 
                t.token_id,
                t.token_value,
                t.client_id,
                t.site_id,
                t.is_active,
                t.created_at,
                t.expires_at,
                t.usage_count,
                t.last_used_at,
                t.notes,
                c.name as client_name,
                s.name as site_name,
                u.name as created_by_name
            FROM agent_installation_tokens t
            JOIN clients c ON t.client_id = c.client_id
            JOIN sites s ON t.site_id = s.site_id
            JOIN users u ON t.created_by = u.user_id
            WHERE t.client_id = %s AND t.site_id = %s
            ORDER BY t.created_at DESC
            """
            
            tokens = self.db.execute_query(query, (client_id, site_id))
            
            return [self._format_token_data(token) for token in tokens]
            
        except Exception as e:
            self.logger.error(f"Error getting tokens for client {client_id}, site {site_id}: {e}")
            raise

    def get_all_tokens_for_client(self, client_id: str) -> List[Dict[str, Any]]:
        """
        Get all installation tokens for a specific client (all sites)
        
        Args:
            client_id: UUID of the client
            
        Returns:
            List of token dictionaries
        """
        try:
            query = """
            SELECT 
                t.token_id,
                t.token_value,
                t.client_id,
                t.site_id,
                t.is_active,
                t.created_at,
                t.expires_at,
                t.usage_count,
                t.last_used_at,
                t.notes,
                c.name as client_name,
                s.name as site_name,
                u.name as created_by_name
            FROM agent_installation_tokens t
            JOIN clients c ON t.client_id = c.client_id
            JOIN sites s ON t.site_id = s.site_id
            JOIN users u ON t.created_by = u.user_id
            WHERE t.client_id = %s
            ORDER BY t.created_at DESC
            """
            
            tokens = self.db.execute_query(query, (client_id,))
            
            return [self._format_token_data(token) for token in tokens]
            
        except Exception as e:
            self.logger.error(f"Error getting tokens for client {client_id}: {e}")
            raise

    def get_all_tokens(self) -> List[Dict[str, Any]]:
        """
        Get all installation tokens (superadmin/technician only)
        
        Returns:
            List of token dictionaries
        """
        try:
            query = """
            SELECT 
                t.token_id,
                t.token_value,
                t.client_id,
                t.site_id,
                t.is_active,
                t.created_at,
                t.expires_at,
                t.usage_count,
                t.last_used_at,
                t.notes,
                c.name as client_name,
                s.name as site_name,
                u.name as created_by_name
            FROM agent_installation_tokens t
            JOIN clients c ON t.client_id = c.client_id
            JOIN sites s ON t.site_id = s.site_id
            JOIN users u ON t.created_by = u.user_id
            ORDER BY t.created_at DESC
            """
            
            tokens = self.db.execute_query(query)
            
            return [self._format_token_data(token) for token in tokens]
            
        except Exception as e:
            self.logger.error(f"Error getting all tokens: {e}")
            raise

    def update_token_status(self, token_id: str, is_active: bool) -> Dict[str, Any]:
        """
        Update token active status
        
        Args:
            token_id: UUID of the token
            is_active: New active status
            
        Returns:
            Updated token information
        """
        try:
            uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
            if not uuid_pattern.match(token_id):
                raise ValueError("Invalid token_id format")
            
            # Update token status
            update_query = """
            UPDATE agent_installation_tokens 
            SET is_active = %s
            WHERE token_id = %s
            RETURNING token_id
            """
            
            result = self.db.execute_query(update_query, (is_active, token_id), fetch='one')
            
            if not result:
                raise ValueError("Token not found or not accessible")
            
            # Get updated token data
            return self.get_token_by_id(token_id)
            
        except Exception as e:
            self.logger.error(f"Error updating token status: {e}")
            raise

    def get_token_by_id(self, token_id: str) -> Dict[str, Any]:
        """
        Get token by ID
        
        Args:
            token_id: UUID of the token
            
        Returns:
            Token dictionary
        """
        try:
            query = """
            SELECT 
                t.token_id,
                t.token_value,
                t.client_id,
                t.site_id,
                t.is_active,
                t.created_at,
                t.expires_at,
                t.usage_count,
                t.last_used_at,
                t.notes,
                c.name as client_name,
                s.name as site_name,
                u.name as created_by_name
            FROM agent_installation_tokens t
            JOIN clients c ON t.client_id = c.client_id
            JOIN sites s ON t.site_id = s.site_id
            JOIN users u ON t.created_by = u.user_id
            WHERE t.token_id = %s
            """
            
            token = self.db.execute_query(query, (token_id,), fetch='one')
            
            if not token:
                raise ValueError("Token not found")
            
            return self._format_token_data(token)
            
        except Exception as e:
            self.logger.error(f"Error getting token by ID {token_id}: {e}")
            raise

    def register_agent_with_token(self, token_value: str, hardware_info: Dict[str, Any],
                                 ip_address: str, user_agent: str) -> Dict[str, Any]:
        """
        Register a new agent using an installation token

        Args:
            token_value: Installation token value
            hardware_info: Hardware information from agent
            ip_address: IP address of the registering agent
            user_agent: User agent string

        Returns:
            Registration result with asset_id and JWT token
        """
        try:
            # Validate token
            validation_result = self.db.execute_query(
                "SELECT * FROM validate_agent_token(%s)",
                (token_value,),
                fetch='one'
            )

            if not validation_result['is_valid']:
                # Log failed attempt
                self._log_token_usage(token_value, ip_address, user_agent,
                                    hardware_info.get('computer_name'), hardware_info,
                                    False, None, validation_result['error_message'])
                raise ValueError(validation_result['error_message'])

            client_id = str(validation_result['client_id'])
            site_id = str(validation_result['site_id'])
            computer_name = hardware_info.get('computer_name', 'Unknown')

            # Create asset record
            asset_data = {
                'client_id': client_id,
                'site_id': site_id,
                'name': f"{computer_name} (Agent)",
                'asset_type': 'workstation',
                'status': 'active',
                'agent_status': 'online',
                'agent_version': hardware_info.get('agent_version', '1.0.0'),
                'last_seen': datetime.now(),
                'last_inventory_update': datetime.now(),
                'hardware_specs': hardware_info.get('hardware', {}),
                'software_inventory': hardware_info.get('software', []),
                'system_metrics': hardware_info.get('status', {})
            }

            # Insert asset
            insert_asset_query = """
            INSERT INTO assets (
                client_id, site_id, name, asset_type, status,
                agent_status, agent_version, last_seen, last_inventory_update,
                hardware_specs, software_inventory, system_metrics
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) RETURNING asset_id
            """

            asset_result = self.db.execute_query(
                insert_asset_query,
                (
                    client_id, site_id, asset_data['name'], asset_data['asset_type'],
                    asset_data['status'], asset_data['agent_status'], asset_data['agent_version'],
                    asset_data['last_seen'], asset_data['last_inventory_update'],
                    asset_data['hardware_specs'], asset_data['software_inventory'],
                    asset_data['system_metrics']
                ),
                fetch='one'
            )

            asset_id = str(asset_result['asset_id'])

            # Update token usage count
            self.db.execute_query(
                """UPDATE agent_installation_tokens
                   SET usage_count = usage_count + 1, last_used_at = NOW()
                   WHERE token_value = %s""",
                (token_value,)
            )

            # Log successful usage
            self._log_token_usage(token_value, ip_address, user_agent, computer_name,
                                hardware_info, True, asset_id, None)

            # Generate JWT token for agent authentication
            agent_token = self._generate_agent_jwt_token(asset_id, client_id, site_id)

            self.logger.info(f"Successfully registered agent {computer_name} as asset {asset_id}")

            return {
                'success': True,
                'asset_id': asset_id,
                'client_id': client_id,
                'site_id': site_id,
                'client_name': validation_result['client_name'],
                'site_name': validation_result['site_name'],
                'agent_token': agent_token,
                'config': self._get_agent_config()
            }

        except Exception as e:
            self.logger.error(f"Error registering agent with token {token_value}: {e}")
            # Log failed attempt if we have token info
            try:
                self._log_token_usage(token_value, ip_address, user_agent,
                                    hardware_info.get('computer_name'), hardware_info,
                                    False, None, str(e))
            except:
                pass
            raise

    def _log_token_usage(self, token_value: str, ip_address: str, user_agent: str,
                        computer_name: str, hardware_info: Dict[str, Any],
                        success: bool, asset_id: Optional[str], error_message: Optional[str]):
        """Log token usage attempt"""
        try:
            # Get token_id
            token_query = "SELECT token_id FROM agent_installation_tokens WHERE token_value = %s"
            token_result = self.db.execute_query(token_query, (token_value,), fetch='one')

            if token_result:
                insert_usage_query = """
                INSERT INTO agent_token_usage_history
                (token_id, ip_address, user_agent, computer_name, hardware_fingerprint,
                 registration_successful, asset_id, error_message)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """

                self.db.execute_query(
                    insert_usage_query,
                    (
                        token_result['token_id'], ip_address, user_agent, computer_name,
                        hardware_info, success, asset_id, error_message
                    )
                )
        except Exception as e:
            self.logger.warning(f"Failed to log token usage: {e}")

    def _generate_agent_jwt_token(self, asset_id: str, client_id: str, site_id: str) -> str:
        """Generate JWT token for agent authentication"""
        # This would integrate with the existing JWT system
        # For now, return a placeholder
        return f"agent_token_{asset_id}_{uuid.uuid4().hex[:8]}"

    def _get_agent_config(self) -> Dict[str, Any]:
        """Get agent configuration from system_config"""
        try:
            config_query = """
            SELECT config_key, config_value
            FROM system_config
            WHERE config_key LIKE 'agent_%'
            """

            config_rows = self.db.execute_query(config_query)
            config = {}

            for row in config_rows:
                key = row['config_key'].replace('agent_', '')
                config[key] = row['config_value']

            # Default configuration
            default_config = {
                'heartbeat_interval': 60,
                'inventory_interval': 3600,
                'metrics_interval': 300,
                'server_url': 'https://helpdesk.lanet.mx/api'
            }

            return {**default_config, **config}

        except Exception as e:
            self.logger.warning(f"Error getting agent config: {e}")
            return {
                'heartbeat_interval': 60,
                'inventory_interval': 3600,
                'metrics_interval': 300,
                'server_url': 'https://helpdesk.lanet.mx/api'
            }

    def _format_token_data(self, token: Dict[str, Any]) -> Dict[str, Any]:
        """Format token data for API response"""
        return {
            'token_id': str(token['token_id']),
            'token_value': token['token_value'],
            'client_id': str(token['client_id']),
            'site_id': str(token['site_id']),
            'client_name': token['client_name'],
            'site_name': token['site_name'],
            'is_active': token['is_active'],
            'created_at': token['created_at'].isoformat() if token['created_at'] else None,
            'expires_at': token['expires_at'].isoformat() if token['expires_at'] else None,
            'usage_count': token['usage_count'],
            'last_used_at': token['last_used_at'].isoformat() if token['last_used_at'] else None,
            'notes': token['notes'],
            'created_by_name': token['created_by_name']
        }
