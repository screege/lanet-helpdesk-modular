#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - Agents Service
Handles business logic for agent installation tokens and agent registration
"""

import logging
import uuid
import re
import json
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

    def validate_token_for_installation(self, token_value: str) -> Dict[str, Any]:
        """
        Validate an installation token and return client/site information for installation UI

        Args:
            token_value: Installation token value

        Returns:
            Dict with validation result and client/site information
        """
        try:
            # Validate token using database function
            validation_result = self.db.execute_query(
                "SELECT * FROM validate_agent_token(%s)",
                (token_value,),
                fetch='one'
            )

            if not validation_result['is_valid']:
                return {
                    'is_valid': False,
                    'error_message': validation_result['error_message']
                }

            # Get detailed client and site information
            client_site_query = """
            SELECT
                c.client_id,
                c.name as client_name,
                c.rfc as client_rfc,
                s.site_id,
                s.name as site_name,
                s.address as site_address,
                s.city as site_city,
                s.state as site_state
            FROM clients c
            JOIN sites s ON s.client_id = c.client_id
            WHERE c.client_id = %s AND s.site_id = %s
            """

            client_site = self.db.execute_query(
                client_site_query,
                (validation_result['client_id'], validation_result['site_id']),
                fetch='one'
            )

            if not client_site:
                return {
                    'is_valid': False,
                    'error_message': 'Client or site not found'
                }

            return {
                'is_valid': True,
                'client_id': str(client_site['client_id']),
                'client_name': client_site['client_name'],
                'client_rfc': client_site['client_rfc'],
                'site_id': str(client_site['site_id']),
                'site_name': client_site['site_name'],
                'site_address': client_site['site_address'],
                'site_city': client_site['site_city'],
                'site_state': client_site['site_state'],
                'token_value': token_value
            }

        except Exception as e:
            self.logger.error(f"Error validating token for installation: {e}")
            return {
                'is_valid': False,
                'error_message': 'Error validating token'
            }

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

            # Generate hardware fingerprint for duplicate detection
            hardware_fingerprint = self._generate_hardware_fingerprint(hardware_info)

            # Check for existing asset by hardware fingerprint first
            existing_asset = self._check_existing_asset_by_fingerprint(
                hardware_fingerprint, client_id, site_id
            )

            # If not found by fingerprint, check by computer name as fallback
            if not existing_asset:
                existing_asset = self._check_existing_asset_by_name(f"{computer_name} (Agent)")

            # If existing asset found, update it instead of creating new one
            if existing_asset:
                self.logger.info(f"Found existing asset {existing_asset['asset_id']} for {computer_name}")

                # Update existing asset with latest information
                asset_id = str(existing_asset['asset_id'])
                self._update_existing_asset(asset_id, hardware_info, hardware_fingerprint)

                # Update token usage count
                self.db.execute_query(
                    """UPDATE agent_installation_tokens
                       SET usage_count = usage_count + 1, last_used_at = NOW()
                       WHERE token_value = %s""",
                    (token_value,),
                    fetch='none'
                )

                # Log successful usage
                self._log_token_usage(token_value, ip_address, user_agent, computer_name,
                                    hardware_info, True, asset_id, None)

                # Generate JWT token for agent authentication
                agent_token = self._generate_agent_jwt_token(asset_id, client_id, site_id)

                self.logger.info(f"Successfully updated existing asset {asset_id} for {computer_name}")

                return {
                    'success': True,
                    'asset_id': asset_id,
                    'client_id': client_id,
                    'site_id': site_id,
                    'client_name': validation_result['client_name'],
                    'site_name': validation_result['site_name'],
                    'agent_token': agent_token,
                    'config': self._get_agent_config(),
                    'existing_asset': True
                }

            # Create new asset record
            asset_data = {
                'client_id': client_id,
                'site_id': site_id,
                'name': f"{computer_name} (Agent)",
                'asset_type': 'desktop',
                'status': 'active',
                'agent_status': 'online',
                'last_seen': datetime.now(),
                'specifications': {
                    'agent_version': hardware_info.get('agent_version', '1.0.0'),
                    'hardware': hardware_info.get('hardware', {}),
                    'software': hardware_info.get('software', []),
                    'system_metrics': hardware_info.get('status', {}),
                    'os': hardware_info.get('os', ''),
                    'registration_date': datetime.now().isoformat(),
                    'hardware_fingerprint': hardware_fingerprint,
                    'network_interfaces': hardware_info.get('network_interfaces', []),
                    'platform_details': hardware_info.get('platform_details', {})
                }
            }

            # Insert asset
            insert_asset_query = """
            INSERT INTO assets (
                client_id, site_id, name, asset_type, status,
                agent_status, last_seen, specifications
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s
            ) RETURNING asset_id
            """

            asset_result = self.db.execute_query(
                insert_asset_query,
                (
                    client_id, site_id, asset_data['name'], asset_data['asset_type'],
                    asset_data['status'], asset_data['agent_status'], asset_data['last_seen'],
                    json.dumps(asset_data['specifications'])
                ),
                fetch='one'
            )

            asset_id = str(asset_result['asset_id'])

            # Update token usage count
            self.db.execute_query(
                """UPDATE agent_installation_tokens
                   SET usage_count = usage_count + 1, last_used_at = NOW()
                   WHERE token_value = %s""",
                (token_value,),
                fetch='none'
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

        except ValueError as ve:
            # Token validation errors - don't crash the backend
            self.logger.warning(f"Token validation error for {token_value}: {ve}")
            try:
                self._log_token_usage(token_value, ip_address, user_agent,
                                    hardware_info.get('computer_name', 'Unknown'), hardware_info,
                                    False, None, str(ve))
            except Exception as log_error:
                self.logger.error(f"Failed to log token usage: {log_error}")
            raise ve
        except Exception as e:
            # Unexpected errors - log but don't crash backend
            self.logger.error(f"Unexpected error registering agent with token {token_value}: {e}", exc_info=True)

            # Try to log failed attempt
            try:
                self._log_token_usage(token_value, ip_address, user_agent,
                                    hardware_info.get('computer_name', 'Unknown'), hardware_info,
                                    False, None, f"Registration error: {str(e)}")
            except Exception as log_error:
                self.logger.error(f"Failed to log token usage after error: {log_error}")

            # Re-raise as a controlled error to prevent backend crash
            raise Exception(f"Agent registration failed: {str(e)}")

    def _generate_hardware_fingerprint(self, hardware_info: Dict[str, Any]) -> str:
        """Generate a unique hardware fingerprint from hardware information"""
        try:
            import hashlib

            # Collect unique hardware identifiers
            fingerprint_data = []

            # Computer name
            if hardware_info.get('computer_name'):
                fingerprint_data.append(f"name:{hardware_info['computer_name']}")

            # Network interfaces (MAC addresses)
            network_interfaces = hardware_info.get('network_interfaces', [])
            mac_addresses = []
            for interface in network_interfaces:
                if 'mac_address' in interface and interface['mac_address']:
                    mac_addresses.append(interface['mac_address'].upper())

            if mac_addresses:
                mac_addresses.sort()  # Ensure consistent ordering
                fingerprint_data.append(f"mac:{','.join(mac_addresses)}")

            # Hardware details
            hardware = hardware_info.get('hardware', {})
            if hardware:
                # CPU info
                cpu = hardware.get('cpu', {})
                if cpu.get('cores'):
                    fingerprint_data.append(f"cpu_cores:{cpu['cores']}")

                # Memory info
                memory = hardware.get('memory', {})
                if memory.get('total_bytes'):
                    fingerprint_data.append(f"memory:{memory['total_bytes']}")

                # Disk info
                disk = hardware.get('disk', {})
                if disk.get('total_bytes'):
                    fingerprint_data.append(f"disk:{disk['total_bytes']}")

            # Platform details
            platform_details = hardware_info.get('platform_details', {})
            if platform_details:
                if platform_details.get('machine'):
                    fingerprint_data.append(f"machine:{platform_details['machine']}")
                if platform_details.get('processor'):
                    fingerprint_data.append(f"processor:{platform_details['processor']}")

            # Create hash from collected data
            if fingerprint_data:
                fingerprint_string = '|'.join(sorted(fingerprint_data))
                fingerprint_hash = hashlib.sha256(fingerprint_string.encode('utf-8')).hexdigest()[:16]
                self.logger.info(f"Generated hardware fingerprint: {fingerprint_hash} from {len(fingerprint_data)} identifiers")
                return fingerprint_hash
            else:
                # Fallback to computer name hash if no hardware data available
                fallback_data = hardware_info.get('computer_name', 'unknown')
                fingerprint_hash = hashlib.sha256(fallback_data.encode('utf-8')).hexdigest()[:16]
                self.logger.warning(f"Using fallback fingerprint: {fingerprint_hash}")
                return fingerprint_hash

        except Exception as e:
            self.logger.error(f"Error generating hardware fingerprint: {e}")
            # Return a fallback fingerprint
            import hashlib
            fallback_data = hardware_info.get('computer_name', 'unknown')
            return hashlib.sha256(fallback_data.encode('utf-8')).hexdigest()[:16]

    def _check_existing_asset_by_fingerprint(self, hardware_fingerprint: str,
                                           client_id: str, site_id: str) -> Optional[Dict]:
        """Check if asset already exists based on hardware fingerprint"""
        try:
            # Check by hardware fingerprint within the same client/site
            existing_asset = self.db.execute_query(
                """SELECT asset_id, name, client_id, site_id, specifications
                   FROM assets
                   WHERE client_id = %s
                   AND site_id = %s
                   AND status = 'active'
                   AND specifications->>'hardware_fingerprint' = %s
                   LIMIT 1""",
                (client_id, site_id, hardware_fingerprint),
                fetch='one'
            )

            if existing_asset:
                self.logger.info(f"Found existing asset by hardware fingerprint: {hardware_fingerprint}")
                return existing_asset

            return None

        except Exception as e:
            self.logger.error(f"Error checking existing asset by fingerprint: {e}")
            return None

    def _check_existing_asset_by_name(self, asset_name: str) -> Optional[Dict]:
        """Check if asset already exists based on computer name"""
        try:
            # Check by computer name
            existing_asset = self.db.execute_query(
                """SELECT asset_id, name, client_id, site_id
                   FROM assets
                   WHERE name = %s
                   AND status = 'active'
                   LIMIT 1""",
                (asset_name,),
                fetch='one'
            )

            if existing_asset:
                self.logger.info(f"Found existing asset by name: {asset_name}")
                return existing_asset

            return None

        except Exception as e:
            self.logger.error(f"Error checking existing asset by name: {e}")
            return None

    def _update_existing_asset(self, asset_id: str, hardware_info: Dict[str, Any],
                             hardware_fingerprint: str):
        """Update existing asset with latest hardware information"""
        try:
            # Update asset with latest information
            update_query = """
            UPDATE assets
            SET
                agent_status = 'online',
                last_seen = NOW(),
                specifications = specifications || %s,
                updated_at = NOW()
            WHERE asset_id = %s
            """

            # Prepare updated specifications
            updated_specs = {
                'agent_version': hardware_info.get('agent_version', '1.0.0'),
                'hardware': hardware_info.get('hardware', {}),
                'software': hardware_info.get('software', []),
                'system_metrics': hardware_info.get('status', {}),
                'os': hardware_info.get('os', ''),
                'last_registration_date': datetime.now().isoformat(),
                'hardware_fingerprint': hardware_fingerprint,
                'network_interfaces': hardware_info.get('network_interfaces', []),
                'platform_details': hardware_info.get('platform_details', {})
            }

            self.db.execute_query(
                update_query,
                (json.dumps(updated_specs), asset_id),
                fetch='none'
            )

            self.logger.info(f"Updated existing asset {asset_id} with latest hardware information")

        except Exception as e:
            self.logger.error(f"Error updating existing asset {asset_id}: {e}")
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
                        json.dumps(hardware_info), success, asset_id, error_message
                    ),
                    fetch='none'
                )
        except Exception as e:
            self.logger.warning(f"Failed to log token usage: {e}")

    def _generate_agent_jwt_token(self, asset_id: str, client_id: str, site_id: str) -> str:
        """Generate JWT token for agent authentication"""
        try:
            from flask_jwt_extended import create_access_token
            from datetime import timedelta

            # Create JWT token with agent identity
            additional_claims = {
                'asset_id': asset_id,
                'client_id': client_id,
                'site_id': site_id,
                'type': 'agent'
            }

            # Token expires in 30 days for agents
            token = create_access_token(
                identity=f"agent_{asset_id}",
                expires_delta=timedelta(days=30),
                additional_claims=additional_claims
            )

            return token

        except Exception as e:
            self.logger.error(f"Error generating JWT token: {e}")
            # Fallback to placeholder if JWT fails
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
